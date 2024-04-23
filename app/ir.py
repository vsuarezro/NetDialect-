import yaml

"""
Intermediate representation of the YAML configuration file on the router
---
config:
  hostname: HOSTNAME
  aggregate_vlans:
  - VLAN_AGGREGATE_1:
    start: VLAN_AGGREGATE_1_START
    end: VLAN_AGGREGATE_1_END
  - VLAN_AGGREGATE_2:
    start: VLAN_AGGREGATE_2_START
    end: VLAN_AGGREGATE_2_END
  aggregated_vlans:
  - vlan1: VLAN_AGGREGATE_1
  - vlan2: VLAN_AGGREGATE_1
  - vlan3: VLAN_AGGREGATE_2
  lags:
  - LAG1_NAME
    members:
      - INTERFACE5_NAME
      - INTERFACE6_NAME
  - LAG2_NAME
    members:
      - INTERFACE7_NAME
      - INTERFACE8_NAME
  VRFs:
  - VRF_NAME
    interfaces:
      - INTERFACE1_NAME
        description: INTERFACE1_DESCRIPTION
        type: l3
        ipv4: INTERFACE1_IPV4
        mask_ipv4: INTERFACE1_MASK_IPV4
      - INTERFACE2_NAME
        description: INTERFACE2_DESCRIPTION
        type: vpls
        has_aggregation: true / false
        ipv4: INTERFACE2_IPV4
        mask_ipv4: INTERFACE2_MASK_IPV4
        interfaces:
          - INTERFACE3_NAME
            description: INTERFACE3_DESCRIPTION
            type: access
          - INTERFACE4_NAME
            description: INTERFACE4_DESCRIPTION
            type: trunk
    routes:
      - DESTINATION_IP/MASK_IP
        description: DESCRIPTION
        next_hop: NEXT_HOP_IP
      - DESTINATION2_IP/MASK_IP
        description: DESCRIPTION2
        next_hop: NEXT_HOP_IP2

  """
    
