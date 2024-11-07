#!/usr/bin/env python3

"""
WARNING: NOT TESTED
NetBox script to scan device ports and synchronize discovered services.
Creates and updates service records based on port availability.
"""

import socket
from typing import List, Dict, Tuple, Optional

from django.utils.text import slugify
from dcim.models import Device
from ipam.models import IPAddress
from extras.scripts import Script, StringVar, IntegerVar
from utilities.exceptions import AbortScript
from extras.models import Tag


class ScanAndSyncServices(Script):
    """
    Scans network devices for open ports and synchronizes discovered services in NetBox.
    Creates or updates service records for each discovered service.
    """

    class Meta:
        name = "Scan and Sync Services"
        description = "Scans device ports and creates/updates corresponding service records"
        field_order = ['timeout']

    timeout = IntegerVar(
        description="Connection timeout in seconds",
        default=2,
        min_value=1,
        max_value=10
    )

    # Service definitions with port mappings
    SERVICES: Dict[int, str] = {
        # Web Services
        80: "HTTP",
        443: "HTTPS",
        8080: "HTTP-Alternative",
        8443: "HTTPS-Alternative",
        8081: "HTTP-Alternative",
        8000: "Django Dev Server",
        8088: "Alternative HTTP/Reverse Proxies",
        
        # Administrative
        22: "SSH",
        21: "FTP",
        23: "Telnet",
        3389: "RDP",
        5900: "VNC",
        5901: "VNC alternative",
        2222: "DirectAdmin",
        
        # Database Services
        3306: "MySQL",
        5432: "PostgreSQL",
        27017: "MongoDB",
        6379: "Redis",
        11211: "Memcached",
        
        # Monitoring & Management
        161: "SNMP",
        162: "SNMP Trap",
        9090: "Prometheus",
        9093: "Alertmanager",
        5666: "NRPE",
        10050: "Zabbix Agent",
        10051: "Zabbix Server",
        
        # Infrastructure
        53: "DNS",
        25: "SMTP",
        110: "POP3",
        143: "IMAP",
        389: "LDAP",
        636: "LDAPS",
        637: "Ldap alternative",
        123: "NTP",
        514: "Syslog",
        
        # Application Services
        2375: "Docker API (insecure)",
        2376: "Docker API (secure)",
        9200: "Elasticsearch",
        5672: "RabbitMQ",
        15672: "RabbitMQ Management",
        1883: "MQTT",
        1880: "Node-RED",
        9001: "Portainer",
        8006: "Proxmox",
        3899: "Skype",
        6667: "IRC",
        7000: "Afes alternative",
        7070: "RealPlayer alternative",
        9092: "Kafka Broker",
        10000: "Webmin",
        9000: "SonarQube",
        1025: "NFS or alternative"
    }

    def test_port(self, ip: str, port: int, timeout: int) -> bool:
        """
        Test if a specific port is open on the given IP address.

        Args:
            ip (str): IP address to test
            port (int): Port number to test
            timeout (int): Connection timeout in seconds

        Returns:
            bool: True if port is open, False otherwise
        """
        try:
            with socket.create_connection((ip, port), timeout=timeout) as sock:
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False

    def get_or_create_service_tag(self) -> Tag:
        """
        Get or create a tag for automatically discovered services.

        Returns:
            Tag: The created or retrieved tag object
        """
        tag_name = "Auto-Discovered Service"
        tag_slug = slugify(tag_name)

        tag, _ = Tag.objects.get_or_create(
            name=tag_name,
            slug=tag_slug,
            defaults={
                'description': 'Service automatically discovered by port scanning script',
                'color': '0000FF'  # Blue color
            }
        )
        return tag

    def update_service_record(self, device: Device, port: int, service_name: str, 
                            ip_address_obj: IPAddress, tag: Tag) -> None:
        """
        Create or update a service record in NetBox.

        Args:
            device (Device): NetBox device object
            port (int): Port number of the service
            service_name (str): Name of the service
            ip_address_obj (IPAddress): IP address object associated with the service
            tag (Tag): Tag to apply to the service
        """
        service, created = Service.objects.get_or_create(
            device=device,
            name=service_name,
            protocol="tcp",
            defaults={"ports": [port]}
        )

        if not created and port not in service.ports:
            service.ports.append(port)

        service.ipaddresses.add(ip_address_obj)
        service.tags.add(tag)
        service.save()

        action = "Created" if created else "Updated"
        self.log_success(f"{action} service record: {service_name} on port {port}")

    def run(self, data, commit):
        """
        Main execution method for the script.
        
        Args:
            data: Script data from NetBox
            commit: Whether to commit changes to the database
        """
        if not commit:
            self.log_warning("Script running in dry-run mode. No changes will be made.")
            return

        # Get devices with primary IPv4 addresses
        devices = Device.objects.filter(primary_ip4__isnull=False)
        if not devices.exists():
            raise AbortScript("No devices with primary IPv4 addresses found.")

        # Get or create the auto-discovery tag
        service_tag = self.get_or_create_service_tag()
        
        for device in devices:
            reachable_ports = []
            ip_address_obj = device.primary_ip4
            ip = str(ip_address_obj.address.ip)

            self.log_info(f"Scanning device: {device.name} ({ip})")

            for port, service_name in self.SERVICES.items():
                if self.test_port(ip, port, self.timeout):
                    reachable_ports.append(port)
                    self.update_service_record(
                        device=device,
                        port=port,
                        service_name=service_name,
                        ip_address_obj=ip_address_obj,
                        tag=service_tag
                    )

            if reachable_ports:
                self.log_success(f"Found {len(reachable_ports)} services on {device.name}")
            else:
                self.log_info(f"No reachable ports found on {device.name}")

        self.log_success(f"Completed service discovery for {len(devices)} devices")