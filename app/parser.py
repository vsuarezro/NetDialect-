import pyparsing as pp

interface_name = pp.Word(pp.alphas + "_") + pp.Word(pp.nums + "/")
description = pp.Suppress("description") + pp.restOfLine
vrf = pp.Suppress("ip binding vpn-instance") + pp.Word(pp.alphas + "_" + "&")
ip_address = pp.Combine(pp.Word(pp.nums) + "." + pp.Word(pp.nums) + "." + pp.Word(pp.nums) + "." + pp.Word(pp.nums))
mask = pp.Combine(pp.Word(pp.nums) + "." + pp.Word(pp.nums) + "." + pp.Word(pp.nums) + "." + pp.Word(pp.nums))
portswitch = pp.Word("portswitch")
link_type = pp.Suppress("port link-type") + pp.Word(pp.alphas)
vlan = pp.Suppress("port default vlan") + pp.Word(pp.nums)

interface_block = (
    "interface" + interface_name("interface_name")
    + pp.Optional(portswitch("portswitch"))
    + pp.Optional(description("description"))
    + pp.Optional(pp.Suppress("undo shutdown"))
    + pp.Optional(vrf("vrf"))
    + pp.Optional(pp.Suppress("ip address") + ip_address("ip_address") + mask("mask") )
    + pp.Optional(link_type("lisk_type"))
    + pp.Optional(vlan("vlan"))
    + pp.Optional(pp.Suppress("traffic-policy" + pp.Word(pp.alphanums + "_") + pp.Word(pp.alphanums) + pp.Word(pp.alphanums) + pp.Word(pp.alphanums) ))
    + pp.Optional(pp.Suppress("undo dcn"))
)

config_grammar = pp.OneOrMore(pp.Group(interface_block) + pp.Optional(pp.Suppress("#")) )

if __name__ == "__main__":
    huawei_config = """
interface Vlanif622
  description To-NEC-O&M
  ip binding vpn-instance Nextel_O&M
  ip address 10.60.71.1 255.255.255.240
#
interface Vlanif623
  description To-NEC-O&M
  ip binding vpn-instance Nextel_O&M
  ip address 10.60.70.1 255.255.255.240
#
interface GigabitEthernet1/1/6
  portswitch
  description To-NEC-MXNLESNG0959MW03-O&M
  undo shutdown
  port link-type access
  port default vlan 622
  traffic-policy qos_cs2 inbound vlan 622
  undo dcn 
#
"""
    results = config_grammar.parse_string(huawei_config)
    results.pprint()
    for interface_data in results:
        interface_name = interface_data.get("interface_name")
        print(f"\nInterface Name: {interface_name}")
        print("IP Address:", interface_data.get('ip_address'))
        print("Subnet Mask:", interface_data.get('mask'))
        print("Description:", interface_data.get('description'))
        print("VRF:", interface_data.get('vrf'))
