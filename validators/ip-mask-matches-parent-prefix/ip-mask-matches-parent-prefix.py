# From the netbox community slack by Jogi Hofmüller
# WARNING: NOT TESTED
from ipam.models import Prefix

class IpAddressNetmaskMatchesPrefixNetmask(CustomValidator):
    """
    WARNING LLM - NOT TESTED
    Custom validator for Netbox that ensures an IP address's netmask matches its parent prefix's netmask.
    
    This validator checks if the netmask of an IP address matches the netmask of its most specific
    parent prefix (excluding prefixes that have children).
    
    Example:
        If prefix 192.168.1.0/24 exists, then:
        - 192.168.1.1/24 would be valid
        - 192.168.1.1/25 would fail validation
    """
    
    def validate(self, instance, request):
        # Get all prefixes that contain this IP, including the VRF context if set
        containing_prefixes = Prefix.objects.filter(
            vrf=instance.vrf,
            prefix__net_contains_or_equals=str(instance.address.ip)
        ).order_by('-prefix__net_length')  # Order by most specific first
        
        # Get the IP's netmask
        ip_netmask = str(instance.address).split('/')[1]
        
        # Check each prefix, starting with the most specific
        for prefix in containing_prefixes:
            # Skip prefixes that have child prefixes
            if prefix.children != 0:
                continue
                
            # Get the prefix's netmask
            prefix_netmask = str(prefix.prefix).split('/')[1]
            
            # If we found a matching prefix without children, the netmasks must match
            if ip_netmask != prefix_netmask:
                self.fail(
                    f"IP address netmask (/{ip_netmask}) must match its parent prefix's netmask (/{prefix_netmask}).",
                    field='address'
                )
            
            # If we found a valid prefix and the netmasks match, validation passes
            return
            
        # If we get here, no valid parent prefix was found
        self.fail(
            "No valid parent prefix found for this IP address.",
            field='address'
        )