import pytest

from .grammar_huawei import vlan_interface_block, trunk_interface_block, trunk_member_interface_block, access_interface_block, l3_interface_block, vlan_block, static_route_block, config_grammar 


@pytest.fixture
def aggregate_vlan_string():
    return """vlan 3200
 description Host Service Vlans
 aggregate-vlan
 access-vlan 3100 to 3199
"""

@pytest.fixture
def interface_vlan_string():
    return """interface Vlanif623
 description To-microwave_operations&maintenance
 ip binding vpn-instance O&M
 ip address 10.60.70.1 255.255.255.240
"""

@pytest.fixture
def interface_trunk_string():
    return """interface Eth-Trunk1
 portswitch
 description Destination-name_code
 port link-type trunk
 port trunk allow-pass vlan 185 to 198 485 to 498 624 
 port trunk allow-pass vlan 1000 1024 to 1025 
 traffic-policy qos_cs2 inbound vlan 486 to 498
 traffic-policy qos_cs2 inbound vlan 626
 traffic-policy qos_cs2 inbound vlan 1416 to 1419
 traffic-policy qos_cs2 inbound vlan 1425
 traffic-policy qos_cs2 inbound vlan 3401 to 3414
 mode lacp-static
 trust upstream default vlan 186 to 198 1000 1002 to 1004 1016 to 1019 1025 1200 1202 to 1204 1216 to 1219 1225 1600
 trust upstream default vlan 1602 to 1604 1616 to 1619 1625 2100 2102 to 2104 2116 to 2119 2125 3101 to 3114
"""

@pytest.fixture
def interface_trunk_member_string():
    return """interface GigabitEthernet1/1/10
 description To-L2domain
 undo shutdown
 eth-trunk 1
"""

 
class TestHuawei:
    def test_vlan_aggregate(self, aggregate_vlan_string):
        result = vlan_block.parse_string(aggregate_vlan_string)
        assert result.get("vlan_name") == "3200"
        assert result.get("description") == "Host Service Vlans"
        assert result.get("vlan_start") == "3100"
        assert result.get("vlan_end") == "3199"
        assert result.get("aggregate_vlan") != None

    def test_interface_vlanif(self, interface_vlan_string):
        result = vlan_interface_block.parse_string(interface_vlan_string)
        assert result.get("vlanif") ==  "Vlanif"
        assert result.get("interface_id") == "623" 
        assert result.get("description") == "To-microwave_operations&maintenance"
        assert result.get("vrf") == "O&M"
        assert result.get("ip_address") == "10.60.70.1"
        assert result.get("mask") == "255.255.255.240" 

    def test_interface_trunk(self, interface_trunk_string):
        result = trunk_interface_block.parse_string(interface_trunk_string)
        assert result.get("trunk") ==  "Eth-Trunk"
        assert result.get("interface_id") ==  "1"
        assert result.get("description") ==  "Destination-name_code"
        assert result.get("link_type_trunk") !=  None
        assert result.get("vlans").as_list() == ["185 to 198", "485 to 498", "624", "1000", "1024 to 1025"] 

    def test_interface_trunk_member(self, interface_trunk_member_string):
        result = trunk_member_interface_block.parse_string(interface_trunk_member_string)
        assert result.get("trunk_member") ==  "GigabitEthernet"
        assert result.get("interface_id") ==  r"1/1/10"
        assert result.get("description") ==  "To-L2domain"
        assert result.get("lag_id") == "1"
