# From the netbox community slack by Jogi Hofmüller

class IpAddressNetmaskMatchesPrefixNetmask(CustomValidator):
# Fail if the netmasks don't match the parent prefix

    def validate(self, instance, request):
        from ipam.models import Prefix

        resultset = Prefix.objects.filter(vrf=instance.vrf, prefix__net_contains_or_equals=str(instance.address.ip))
        for prefix in resultset:
            if prefix.children != 0:
                continue
            if str(prefix.prefix).split('/')[1] == str(instance.address).split('/')[1]:
                return

        self.fail('Computer says no (incorrect netmask).', field = 'address')