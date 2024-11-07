# NetBox Device Port Scanner Script
![Status](https://img.shields.io/badge/status-not%20tested-red)
![Steinzi-Approval-status](https://img.shields.io/badge/Steinzi--Approval--status-not%20reviewed-orange)
![Author](https://img.shields.io/badge/BasedOnChat-Marvin%20Cordes-blue)
![LLM](https://img.shields.io/badge/LLM-Translated%20from%20German-yellow)


From a chat with Marvin Cordes in netbox slack

## TLDR
you want to dump in 
## Overview
This NetBox script performs automated port scanning on devices registered in your NetBox instance. It checks for commonly used network services and ports, creating or updating service records in NetBox based on the scan results. This helps maintain an accurate inventory of running services across your infrastructure.



## Purpose
The script serves several key functions:
- Automatically discovers active services on network devices
- Maintains up-to-date service records in NetBox
- Provides visibility into which standard ports are accessible
- Helps identify potential security risks or unauthorized services
- Assists with network documentation and inventory management

## Features
- Scans 45+ common network service ports
- Automatically creates/updates NetBox service records
- Associates services with device IP addresses
- Handles connection timeouts gracefully
- Provides success/info logging for scan results
- Supports common services including:
  - Web services (HTTP/HTTPS)
  - Administrative services (SSH, RDP, VNC)
  - Database services (MySQL, PostgreSQL, MongoDB)
  - Monitoring services (Zabbix, Prometheus)
  - Infrastructure services (DNS, NTP, SMTP)
  - Application services (Docker, Elasticsearch, RabbitMQ)

## Requirements
- NetBox instance with API access
- Python environment with required NetBox libraries
- Network access to target devices
- Appropriate permissions to create/update service records

## How It Works
1. The script queries NetBox for all devices with primary IPv4 addresses
2. For each device, it attempts to connect to each port in the predefined list
3. When a port is accessible:
   - Creates or updates a service record in NetBox
   - Associates the service with the device's IP address
   - Logs the successful connection
4. If no ports are reachable, it logs an informational message

## Port Categories
The script checks for the following categories of services:

### Web Services
- HTTP (80, 8080, 8081)
- HTTPS (443, 8443)
- Development Servers (8000)

### Administrative
- SSH (22)
- FTP (21)
- Telnet (23)
- RDP (3389)
- VNC (5900, 5901)

### Databases
- MySQL (3306)
- PostgreSQL (5432)
- MongoDB (27017)
- Redis (6379)

### Monitoring & Management
- SNMP (161, 162)
- Zabbix (10050, 10051)
- Prometheus (9090)
- Alertmanager (9093)

### Infrastructure
- DNS (53)
- SMTP (25)
- NTP (123)
- Syslog (514)

### Application Services
- Docker API (2375, 2376)
- Elasticsearch (9200)
- RabbitMQ (5672, 15672)
- Kafka (9092)

## Usage
1. Install the script in your NetBox scripts directory
2. Run the script through the NetBox web interface or via API
3. Review the results in:
   - NetBox service records
   - Script execution logs
   - Device service associations

## Best Practices
- Run during maintenance windows to avoid false positives from temporary outages
- Adjust timeout values based on your network characteristics
- Regular execution helps maintain accurate service records
- Review logs to identify patterns or issues
- Consider security implications of port scanning in your environment

## Security Considerations
- The script performs active port scanning which may trigger security alerts
- Some organizations may require approval for port scanning activities
- Consider adding exclusions for sensitive devices
- Review the ports list and remove any that aren't relevant to your environment
- Ensure appropriate access controls are in place

## Limitations
- Only scans IPv4 addresses
- Fixed 2-second timeout per port
- Does not verify the actual service running on the port
- Limited to TCP connections
- Does not perform deep service inspection

## Contributing
Feel free to modify the port list and timeout values to match your organization's needs. Consider contributing improvements back to the community if you enhance the script's functionality.