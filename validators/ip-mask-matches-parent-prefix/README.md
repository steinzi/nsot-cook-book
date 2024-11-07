# ip-mask-matches-parent-prefix
(Not tested yet)
For more information, refer to the [NetBox Custom Validation Documentation](https://netboxlabs.com/docs/netbox/en/stable/customization/custom-validation/).


So this is when you need to make sure that people that are assigning IP addresses to devices are doing so in a way that is consistent with the network's addressing scheme.

In this case it's about not allowing people to save IP addresses that don't match the parrentprefix mask of the network.

This is a pretty common thing to want to do, and it's a good idea to make sure that people are doing this correctly.