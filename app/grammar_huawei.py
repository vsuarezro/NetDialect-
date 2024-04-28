import argparse

import pyparsing as pp
from ir import IR

# DEFINITIONS
interface_name = pp.Word(pp.alphas + "_" + "-") + pp.Word(pp.nums + "/")
vlanif = pp.Word("Vlanif")
interface_type = pp.Word(pp.alphas + "-" + "_")
interface_id = pp.Word(pp.nums + "/")
description = pp.Combine(
    pp.Suppress("description") + pp.Suppress(pp.Literal(" ")) + pp.restOfLine
)

vrf = pp.Word(pp.alphas + "_" + "&")
ip_address = pp.Combine(
    pp.Word(pp.nums)
    + "."
    + pp.Word(pp.nums)
    + "."
    + pp.Word(pp.nums)
    + "."
    + pp.Word(pp.nums)
)
mask = pp.Combine(
    pp.Word(pp.nums)
    + "."
    + pp.Word(pp.nums)
    + "."
    + pp.Word(pp.nums)
    + "."
    + pp.Word(pp.nums)
)

portswitch = pp.Word("portswitch")
link_type = pp.Suppress("port link-type") + pp.Word(pp.alphas)
link_type_trunk = pp.Literal("port link-type trunk")
link_type_access = pp.Suppress("port link-type access")

vlans_allowed = pp.OneOrMore(
    pp.Suppress("port trunk allow-pass vlan")
    + pp.OneOrMore(
        pp.Combine(pp.Word(pp.nums) + " " + pp.Literal("to") + " " + pp.Word(pp.nums))
        | pp.Word(pp.nums)
    )
)

vlan = pp.Suppress("port default vlan") + pp.Word(pp.nums)
vlan_id = pp.Word(pp.nums)
lag_id = pp.Word(pp.nums)
aggregate_vlan_str = pp.Word("aggregate-vlan")

static_route_starter = pp.Literal("ip route-static vpn-instance")

ignore_line = pp.Regex(r".*\r?\n")

# BLOCK DEFINITIONS
vlan_interface_block = (
    "interface"
    + vlanif("vlanif")
    + interface_id("interface_id")
    + pp.Optional(description("description"))
    + pp.Optional(pp.Suppress("ip binding vpn-instance") + vrf("vrf"))
    + pp.Suppress("ip address")
    + ip_address("ip_address")
    + mask("mask")
)

trunk_interface_block = (
    "interface"
    + interface_type("trunk")
    + interface_id("interface_id")
    + pp.Optional(portswitch("portswitch"))
    + pp.Optional(description("description"))
    + pp.Optional(pp.Optional(pp.Word("undo")) + pp.Word("shutdown"))
    + link_type_trunk("link_type_trunk")
    + vlans_allowed("vlans")
)

trunk_member_interface_block = (
    "interface"
    + interface_type("trunk_member")
    + interface_id("interface_id")
    + pp.Optional(description("description"))
    + pp.Optional(pp.Optional(pp.Word("undo")) + pp.Word("shutdown"))
    + pp.Suppress("eth-trunk")
    + lag_id("lag_id")
)

access_interface_block = (
    "interface"
    + interface_type("access")
    + interface_id("interface_id")
    + pp.Optional(portswitch("portswitch"))
    + pp.Optional(description("description"))
    + pp.Optional(pp.Optional(pp.Word("undo")) + pp.Word("shutdown"))
    + link_type_access("link_type_access")
    + pp.Suppress(pp.Literal("port default vlan"))
    + vlan_id("vlan")
)

l3_interface_block = (
    "interface"
    + interface_type("l3")
    + interface_id("interface_id")
    + pp.Optional(description("description"))
    + pp.Optional(pp.Optional(pp.Word("undo")) + pp.Word("shutdown"))
    + pp.Suppress("ip binding vpn-instance")
    + vrf("vrf")
    + pp.Suppress("ip address")
    + ip_address("ip_address")
    + mask("mask")
)


vlan_block = (
    "vlan"
    + vlan_id("vlan_name")
    + pp.Optional(description("description"))
    + aggregate_vlan_str("aggregate_vlan")
    + "access-vlan"
    + vlan_id("vlan_start")
    + "to"
    + vlan_id("vlan_end")
)

static_route_block = (
    static_route_starter("static")
    + vrf("vrf")
    + ip_address("destination")
    + ip_address("destination_mask")
    + ip_address("next_hop")
    + pp.Optional(description("description"))
)

config_grammar = pp.OneOrMore(
    pp.Group(vlan_interface_block)
    | pp.Group(trunk_interface_block)
    | pp.Group(access_interface_block)
    | pp.Group(trunk_member_interface_block)
    | pp.Group(l3_interface_block)
    | pp.Group(vlan_block)
    | pp.Group(static_route_block)
    | pp.Suppress(pp.AtLineStart("#") + pp.rest_of_line)
    | pp.Suppress(ignore_line)
)


def run_example():

    EXAMPLE_huawei_config = """
#
sysname HOSTNAME_STRING
#
ip vpn-instance Service_VRF
 ipv4-family
  route-distinguisher 28469:1700
  vpn-target 28469:1700 28469:1792 export-extcommunity
  vpn-target 28469:1700 28469:1792 import-extcommunity
#
vlan 3200
 description Host Service Vlans
 aggregate-vlan
 access-vlan 3100 to 3199
vlan 3500
 description Host operations and maintenance
 aggregate-vlan
 access-vlan 3400 to 3499
#
interface Vlanif622
  description Downlink_host 
  ip binding vpn-instance O&M
  ip address 10.60.71.1 255.255.255.240
#
interface Vlanif623
  description To-microwave_operations&maintenance
  ip binding vpn-instance O&M
  ip address 10.60.70.1 255.255.255.240
#
interface Eth-Trunk1
 portswitch
 description Destination-name_code
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
  description To-MICROWAVEx
  undo shutdown
  port link-type access
  port default vlan 622
  traffic-policy qos_name inbound vlan 622
  undo dcn 
#
interface GigabitEthernet1/1/9
 description NS-O&M
 shutdown
 ip binding vpn-instance O&M
 ip address 10.224.71.191 255.255.255.254
 traffic-policy qos_cs2 inbound
#
interface GigabitEthernet1/1/10
 description To-L2domain
 undo shutdown
 eth-trunk 1
#
interface Virtual-Template0
 ppp authentication-mode auto
# 
interface GigabitEthernet2/1/2
 description Uplink_hostname_&_port
 undo shutdown
 ip address 10.33.100.130 255.255.255.252
 ospf cost 100
 ospf network-type p2p
 mpls
 mpls te
 mpls rsvp-te
 mpls rsvp-te hello
 undo dcn
 trust upstream default
 port shaping 900
 shaping service-template QosService
 qos-profile Service outbound identifier none
#
ip community-filter 191 permit 64218:921
ip community-filter 192 permit 64218:922
#
ip route-static vpn-instance VRF_NodeB 10.246.17.192 255.255.255.252 10.247.17.194 description HOST1/Service
ip route-static vpn-instance VRF_NodeB 10.246.17.196 255.255.255.252 10.247.17.198 description Host2
ip route-static vpn-instance VRF_NodeB 10.246.17.200 255.255.255.252 10.247.17.202 description HOST3/Service
ip route-static vpn-instance VRF_NodeB 10.246.17.204 255.255.255.252 10.247.17.206 description Host4/Service
ip route-static vpn-instance VRF_NodeB 10.246.17.208 255.255.255.252 10.247.17.210 description customer computer/Service
ip route-static vpn-instance VRF_O&M 10.251.61.168 255.255.255.255 10.252.54.54 description customer100/Broadband-O&M
ip route-static vpn-instance VRF_O&M 10.251.61.169 255.255.255.255 10.252.54.58 description Customer-premium!@#$%/Broadband-O&M
ip route-static vpn-instance VRF_O&M 10.251.61.170 255.255.255.255 10.252.54.62 description Description/Broadband-O&M
ip route-static vpn-instance VRF_O&M 10.251.61.171 255.255.255.255 10.252.54.66 description Broadband-O&M
ip route-static vpn-instance VRF-eNodeB 10.62.98.226 255.255.255.255 10.62.66.226 description to IPsec / VLAN-3100 
ip route-static vpn-instance VRF&eNodeB 10.62.98.227 255.255.255.255 10.62.66.227 description to IPsec / VLAN-3101
ip route-static vpn-instance VRF_eNodeB 10.62.98.228 255.255.255.255 10.62.66.228 description to IPsec / VLAN-3102
"""

    results = config_grammar.parse_string(EXAMPLE_huawei_config)
    print(EXAMPLE_huawei_config)
    input("Press a key to continue...")
    print(results)
    input("Press a key to continue...")
    # print(intermediate_representation_yaml)


    for data in results:
        if data.get("vlanif"):
            interface_id = data.get("interface_id")
            print(f"\nVLAN INTERFACE Name: {interface_id}")
            print("Description:", data.get("description"))
            print("VRF:", data.get("vrf"))
            print("IP Address:", data.get("ip_address"))
            print("Subnet Mask:", data.get("mask"))

        elif data.get("trunk"):
            interface_name = data.get("trunk") + data.get("interface_id")
            print(f"\nTRUNK INTERFACE Name: {interface_name}")
            print("Description:", data.get("description"))
            print("TRUNK:", data.get("trunk"))
            print("Vlans allowed:", data.get("vlans"))

        elif data.get("access"):
            interface_name = data.get("access") + data.get("interface_id")
            print(f"\nACCESS INTERFACE Name: {interface_name}")
            print("Description:", data.get("description"))
            print("ACCESS:", data.get("access"))
            print("Vlan allowed:", data.get("vlan"))

        elif data.get("trunk_member"):
            interface_name = data.get("trunk_member") + data.get("interface_id")
            print(f"\nTRUNK MEMBER INTERFACE Name: {interface_name}")
            print("Description:", data.get("description"))
            print("LAG ID:", data.get("lag_id"))

        elif data.get("l3"):
            interface_name = data.get("l3") + data.get("interface_id")
            print(f"\nL3 INTERFACE Name: {interface_name}")
            print("Description:", data.get("description"))
            print("VRF:", data.get("vrf"))
            print("IP Address:", data.get("ip_address"))
            print("Subnet Mask:", data.get("mask"))

        elif data.get("aggregate_vlan"):
            vlan_name = data.get("vlan_name")
            print(f"\nAGGREGATE VLAN: {vlan_name}")
            print("Description:", data.get("description"))
            print("Aggregate vlan:", data.get("aggregate_vlan"))
            print("VRF:", data.get("vrf"))
            print("Start access VLAN: ", data.get("vlan_start"))
            print("End access VLAN: ", data.get("vlan_end"))

        elif data.get("static"):
            static_route = data.get("static")
            print(
                "\nSTATIC ROUTE:",
                data.get("destination"),
                r"/",
                data.get("destination_mask"),
            )
            print("Next Hop:", data.get("next_hop"))
            print("Description:", data.get("description"))
    return results    

def run_parsing(data:str) -> pp.ParseResults:
    results = config_grammar.parse_string(data)
    return results

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Test Huawei grammar.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--file', help='The file to parse.')
    group.add_argument('--test', help='The parser block and string to test.')
    group.add_argument('--example', help='Run the example with using embedded config', action='store_true')

    args = parser.parse_args()

    if args.file:
        with open(args.file, 'r') as open_file:
            config = open_file.read()
        results = run_parsing(config)
        ir = IR(results)
        print(ir)
    elif args.test:
        pass
    elif args.example:
        results = run_example()

