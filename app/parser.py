import pyparsing as pp

interface_name = pp.Word(pp.alphas + "_" + "-" ) + pp.Word(pp.nums + "/")
description = pp.Suppress("description") + pp.restOfLine
vrf = pp.Word(pp.alphas + "_" + "&")
ip_address = pp.Combine(pp.Word(pp.nums) + "." + pp.Word(pp.nums) + "." + pp.Word(pp.nums) + "." + pp.Word(pp.nums))
mask = pp.Combine(pp.Word(pp.nums) + "." + pp.Word(pp.nums) + "." + pp.Word(pp.nums) + "." + pp.Word(pp.nums))
portswitch = pp.Word("portswitch")
link_type = pp.Suppress("port link-type") + pp.Word(pp.alphas)
vlan = pp.Suppress("port default vlan") + pp.Word(pp.nums)

interface_block = (
    "interface" + interface_name("interface_name")
    + pp.Optional(portswitch("portswitch"))
    + pp.Optional(description("description"))
    + pp.Optional(pp.Suppress("ip binding vpn-instance") + vrf("vrf"))
    + pp.Optional(pp.Suppress("ip address") + ip_address("ip_address") + mask("mask") )
    + pp.Optional(link_type("link_type"))
    + pp.Optional(vlan("vlan"))
    + pp.Optional(pp.Suppress("traffic-policy" + pp.Word(pp.alphanums + "_") + pp.Word(pp.alphanums) + pp.Word(pp.alphanums) + pp.Word(pp.alphanums) ))
    + pp.Optional(pp.Suppress("undo dcn"))
)

vlan_id = pp.Word(pp.nums)
aggregate_vlan_str = pp.Word("aggregate-vlan")

vlan_block = (
    "vlan" + vlan_id("vlan_name")
    + pp.Optional(description("description"))
    + aggregate_vlan_str("aggregate_vlan")
    + "access-vlan" + vlan_id("vlan_start") + "to" + vlan_id("vlan_end")
)

static_route_starter = pp.Word("ip route-static vpn-instance")

static_route_block = (
    static_route_starter("static")
    + vrf("vrf") 
    + ip_address("destination")
    + ip_address("destination_mask")
    + ip_address("next_hop") 
    + pp.Optional(description("description"))

)

ignore_line = pp.Regex(r".*\r?\n")

config_grammar = pp.OneOrMore(pp.Group(interface_block) | 
        pp.Group(vlan_block) | 
        pp.Group(static_route_block) |
        pp.Suppress("#") | 
        pp.Suppress(ignore_line) )

if __name__ == "__main__":
    huawei_config = """
#
sysname HOSTNAME_STRING
#
ip vpn-instance Nextel_eNodeB
 ipv4-family
  route-distinguisher 28469:1700
  vpn-target 28469:1700 28469:1792 export-extcommunity
  vpn-target 28469:1700 28469:1792 import-extcommunity
#
vlan 3200
 description eNodeB Service
 aggregate-vlan
 access-vlan 3100 to 3199
vlan 3500
 description eNodeB O&M
 aggregate-vlan
 access-vlan 3400 to 3499
#
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
interface Eth-Trunk1
 portswitch
 description To-MXDIFCYN0384MW01
 port link-type trunk
 port trunk allow-pass vlan 185 to 198 485 to 498 624 to 626 800 802 to 804 816 to 819 824 to 825 1000 1002 to 1004 1016 to 1019
 port trunk allow-pass vlan 1024 to 1025 1200 1202 to 1204 1216 to 1219 1224 to 1225 1400 1402 to 1404 1416 to 1419 1424 to 1425 1600
 port trunk allow-pass vlan 1602 to 1604 1616 to 1619 1624 to 1625 2100 2102 to 2104 2116 to 2119 2124 to 2125 3101 to 3114 3401 to 3414
 traffic-policy qos_cs2 inbound vlan 486 to 498
 traffic-policy qos_cs2 inbound vlan 626
 traffic-policy qos_cs2 inbound vlan 800
 traffic-policy qos_cs2 inbound vlan 802 to 804
 traffic-policy qos_cs2 inbound vlan 816 to 819
 traffic-policy qos_cs2 inbound vlan 825
 traffic-policy qos_cs2 inbound vlan 1400
 traffic-policy qos_cs2 inbound vlan 1402 to 1404
 traffic-policy qos_cs2 inbound vlan 1416 to 1419
 traffic-policy qos_cs2 inbound vlan 1425
 traffic-policy qos_cs2 inbound vlan 3401 to 3414
 mode lacp-static
 trust upstream default vlan 186 to 198 1000 1002 to 1004 1016 to 1019 1025 1200 1202 to 1204 1216 to 1219 1225 1600
 trust upstream default vlan 1602 to 1604 1616 to 1619 1625 2100 2102 to 2104 2116 to 2119 2125 3101 to 3114
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
interface GigabitEthernet1/1/9
 description To-ASR920-NS-O&M
 shutdown
 ip binding vpn-instance Nextel_O&M
 ip address 10.224.71.191 255.255.255.254
 traffic-policy qos_cs2 inbound
#
interface GigabitEthernet1/1/10
 description To-MXAGUAGU0025MW01
 undo shutdown
 eth-trunk 1
#
interface Virtual-Template0
 ppp authentication-mode auto
#
#
ip community-filter 191 permit 64218:921
ip community-filter 192 permit 64218:922
#
ip route-static vpn-instance Nextel_NodeB 10.246.17.192 255.255.255.252 10.247.17.194 description DIFIZT1180/GSM-Service
ip route-static vpn-instance Nextel_NodeB 10.246.17.196 255.255.255.252 10.247.17.198 description HMEX0589/GSM-Service
ip route-static vpn-instance Nextel_NodeB 10.246.17.200 255.255.255.252 10.247.17.202 description HMEX0199/GSM-Service
ip route-static vpn-instance Nextel_NodeB 10.246.17.204 255.255.255.252 10.247.17.206 description HMEX0587/GSM-Service
ip route-static vpn-instance Nextel_NodeB 10.246.17.208 255.255.255.252 10.247.17.210 description HMEX1083/GSM-Service
ip route-static vpn-instance Nextel_O&M 10.251.61.168 255.255.255.255 10.252.54.54 description LMEX0060/LTE-O&M
ip route-static vpn-instance Nextel_O&M 10.251.61.169 255.255.255.255 10.252.54.58 description LMEX0494/LTE-O&M
ip route-static vpn-instance Nextel_O&M 10.251.61.170 255.255.255.255 10.252.54.62 description LMEX0520/LTE-O&M
ip route-static vpn-instance Nextel_O&M 10.251.61.171 255.255.255.255 10.252.54.66 description LMEX0724/LTE-O&M
ip route-static vpn-instance Nextel_eNodeB 10.62.98.226 255.255.255.255 10.62.66.226 description to IPsec / VLAN-3100 HMEX0589
ip route-static vpn-instance Nextel_eNodeB 10.62.98.227 255.255.255.255 10.62.66.227 description to IPsec / VLAN-3101 HMEX0520
ip route-static vpn-instance Nextel_eNodeB 10.62.98.228 255.255.255.255 10.62.66.228 description to IPsec / VLAN-3102 HMEX0724
"""
    results = config_grammar.parse_string(huawei_config)
    results.pprint()
    for data in results:
        if data.get("interface_name"):
            interface_name = data.as_dict().get("interface_name")
            if "Vlanif" in data.as_dict().get("interface_name"):
                print(f"\nVLAN INTERFACE Name: {interface_name}")
                print("Description:", data.get('description'))
                print("VRF:", data.get('vrf'))
                print("IP Address:", data.get('ip_address'))
                print("Subnet Mask:", data.get('mask'))
            elif data.get("link_type") == "access":
                print(f"\nACCESS INTERFACE Name: {interface_name}")
                print("Description:", data.get('description'))
                print("Type:", data.get("link_type"))


        elif data.get("aggregate_vlan"):
            vlan_name = data.get("vlan_name")
            print(f"\nAGGREGATE VLAN: {vlan_name}")
            print("Description:", data.get("description"))
            print("Aggregated:", "True" if data.get("aggregate-vlan") else "False")
            print("Start access VLAN: ", data.get("vlan_start"))
            print("End access VLAN: ", data.get("vlan_end"))

        elif data.get("static"):
            static_route = data.get("static")
            print("\nSTATIC ROUTE:", data.get("destination"), r"/", data.get("destination_mask"))
            print("Next Hop:", data.get("next_hop"))
            print("Description:", data.get("description"))


