from collections import defaultdict

import yaml

# Intermediate representation of the YAML configuration file on the router
test_yaml = """
---
config:
  hostname: HOSTNAME
  aggregate_vlans:
    VLAN_AGGREGATE_1:
      start: VLAN_AGGREGATE_1_START
      end: VLAN_AGGREGATE_1_END
    VLAN_AGGREGATE_2:
      start: VLAN_AGGREGATE_2_START
      end: VLAN_AGGREGATE_2_END
  aggregated_vlans:
    vlan1: VLAN_AGGREGATE_1
    vlan2: VLAN_AGGREGATE_1
    vlan3: VLAN_AGGREGATE_2
  LAG:
    LAG1_NAME: 
      members:
        INTERFACE5_NAME:
          description: INTERFACE5_DESCRIPTION
        INTERFACE6_NAME:
          description: INTERFACE6_DESCRIPTION
    LAG2_NAME: 
      members:
        INTERFACE7_NAME:
          description: INTERFACE7_DESCRIPTION
        INTERFACE8_NAME:
          description: INTERFACE8_DESCRIPTION
  VRF:
    VRF_NAME:
      interfaces:
        INTERFACE1_NAME:
          description: INTERFACE1_DESCRIPTION
          type: l3
          ipv4: INTERFACE1_IPV4
          mask_ipv4: INTERFACE1_MASK_IPV4
        INTERFACE2_NAME:
          description: INTERFACE2_DESCRIPTION
          type: rvpls
          has_aggregation: true / false
          ipv4: INTERFACE2_IPV4
          mask_ipv4: INTERFACE2_MASK_IPV4
          l2_interface:
            INTERFACE3_NAME:
              description: INTERFACE3_DESCRIPTION
              type: access
            INTERFACE4_NAME:
              description: INTERFACE4_DESCRIPTION
              type: trunk
      routes:
        DESTINATION_IP/MASK_IP:
          description: DESCRIPTION
          next_hop: NEXT_HOP_IP
        DESTINATION2_IP/MASK_IP:
          description: DESCRIPTION2
          next_hop: NEXT_HOP_IP2
  """
    
class IR(object):
    def __init__(self, parsing_result = None):
        self.config = defaultdict(dict)
        self.config["config"] = defaultdict(dict)
        if parsing_result is not None:
            self.load_config(parsing_result)
        
    def __str__(self):
        return yaml.dump(self.config)


    def load_config(self, list_of_dicts: list):
        for data in list_of_dicts:
            if data.get("trunk_member"):
                self._load_trunk_member(data, interface=data.get("trunk_member"))
            if data.get("vlanif"):
                self._load_l3_interface(data, interface=data.get("vlanif"), interface_type="rvpls")
            if data.get("l3"):
                self._load_l3_interface(data, interface=data.get("l3"), interface_type="l3")
            if data.get("static"):
              self._load_static(data)
          
    def _load_l3_interface(self, data: dict, interface: str, interface_type: str):
        """
        This functions will load a single interface from the parsing result and add it to the YAML config file.
        The parsing result will look like this for interface_type "l3":
          {
            'l3': 'GigabitEthernet', 
            'interface_id': '1/1/9', 
            'description': 'NS-O&M', 
            'vrf': 'O&M', 
            'ip_address': 
            '10.224.71.191', 
            'mask': '255.255.255.254'
          }
        
        The parsing result will look like this for interface_type "rvpls":
          {
            'vlanif': 'Vlanif', 
            'interface_id': '623', 
            'description': 'To-microwave_operations&maintenance', 
            'vrf': 'O&M', 
            'ip_address': '10.60.70.1', 
            'mask': '255.255.255.240'
          }

        """
        
        vrf = data.get("vrf").strip() if data.get("vrf") else "default"
        interface_id = str(data.get("interface_id")).strip() if data.get("interface_id") else None
        description = data.get("description").strip() if data.get("description") else None
        ip_address = data.get("ip_address").strip() if data.get("ip_address") else "0.0.0.0"
        mask = data.get("mask").strip() if data.get("mask") else "0"
        if self.config["config"].get("VRF") is None:
            self.config["config"]["VRF"] = {}
        if self.config["config"]["VRF"].get(vrf) is None:
            self.config["config"]["VRF"][vrf] = {}
        if self.config["config"]["VRF"][vrf].get("interface") is None:
            self.config["config"]["VRF"][vrf] = {"interface": {}}
        self.config["config"]["VRF"][vrf]["interface"][interface_id] = {
            "type" : interface_type,
            "description": description,
            "ipv4": ip_address + "/" + mask,
        }

    def _load_trunk_member(self, data: dict, interface: str,):
        """
        This method will load a single trunk member from the parsing result and add it to the YAML config file.
        The parsing result will look like this:
        {
          'trunk_member': 'GigabitEthernet', 
          'interface_id': '1/1/10', 
          'description': 'To-L2domain', 
          'lag_id': '1'
        }
        """
        lag_id = data.get("lag_id").strip() if data.get("lag_id") else "0"
        interface_id = data.get("interface_id").strip() if data.get("interface_id") else None
        description = data.get("description").strip() if data.get("description") else ""
        
        self.config["config"]["LAGS"] = { lag_id : {}}
        self.config["config"]["LAGS"][lag_id]["members"] = {
            interface_id : {
            "interface_type" : data.get("trunk_member"), 
            "description": description,
            }
          }



    def _load_static(self, data: dict):
        """
        This method will load all static routes from the parsing result and add them to the YAML config file.
        Parsing static route will look like this:
          {
            'static': 'ip route-static vpn-instance ', 
            'vrf': 'VRF_eNodeB', 
            'destination': '10.62.98.228', 
            'destination_mask': '255.255.255.255', 
            'next_hop': '10.62.66.228', 
            'description': 'to IPsec / VLAN-3102'
          }
        """
        description = data.get("description").strip() if data.get("description") else ""
        vrf = data.get("vrf").strip() if data.get("vrf") else "default"
        destination_ip_address = data.get("destination").strip() if data.get("destination") else "0.0.0.0"
        destination_mask = data.get("destination_mask").strip() if data.get("destination_mask") else "0"
        next_hop = data.get("next_hop").strip() if data.get("next_hop") else "0.0.0.0"
        
        if self.config["config"]["VRF"].get(vrf) is None:
            self.config["config"]["VRF"][vrf] = {}
        if self.config["config"]["VRF"][vrf].get("routes") is None:
            self.config["config"]["VRF"][vrf]["routes"] = {}
        self.config["config"]["VRF"][vrf]["routes"][f"{destination_ip_address}/{destination_mask}"] = {
            "description" : description,
            "next_hop" : next_hop,
        }

    def _load_access_interface(self, data: dict, interface: str):
        """
        This method will load an access interface from the parsing result and add it to the YAML config file.
        Access interface have VLAN tag information and no L3 information
        Parsing result will look like:
          {
            'access': 'GigabitEthernet', 
            'interface_id': '1/1/6', 
            'portswitch': 'portswitch', 
            'description': 'To-MICROWAVEx', 
            'vlan': '622'
          }
        and must be associated with a L3 interface that uses the VLAN 622 in the example.
        """
        pass




          

