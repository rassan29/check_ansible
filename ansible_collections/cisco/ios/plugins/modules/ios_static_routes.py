#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2023 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for ios_static_routes
"""

from __future__ import absolute_import, division, print_function


__metaclass__ = type

DOCUMENTATION = """
module: ios_static_routes
short_description: Resource module to configure static routes.
description: This module configures and manages the static routes on IOS platforms.
version_added: 1.0.0
author:
  - Sagar Paul (@KB-perByte)
  - Sumit Jaiswal (@justjais)
notes:
  - Tested against Cisco IOSXE Version 17.3 on CML.
  - This module works with connection C(network_cli).
    See U(https://docs.ansible.com/ansible/latest/network/user_guide/platform_ios.html)
options:
  config:
    description: A dictionary of static route options
    type: list
    elements: dict
    suboptions:
      vrf:
        description:
        - IP VPN Routing/Forwarding instance name.
        - NOTE, In case of IPV4/IPV6 VRF routing table should pre-exist before configuring.
        - NOTE, if the vrf information is not provided then the routes shall be configured
          under global vrf.
        type: str
      address_families:
        elements: dict
        description:
        - Address family to use for the static routes
        type: list
        suboptions:
          afi:
            description:
            - Top level address family indicator.
            required: true
            type: str
            choices:
            - ipv4
            - ipv6
          routes:
            description: Configuring static route
            type: list
            elements: dict
            suboptions:
              dest:
                description: Destination prefix with its subnet mask
                type: str
                required: true
              topology:
                description:
                - Configure static route for a Topology Routing/Forwarding instance
                - NOTE, VRF and Topology can be used together only with Multicast
                  and Topology should pre-exist before it can be used
                type: str
              next_hops:
                description:
                - next hop address or interface
                type: list
                elements: dict
                suboptions:
                  forward_router_address:
                    description: Forwarding router's address
                    type: str
                  interface:
                    description: Interface for directly connected static routes
                    type: str
                  dhcp:
                    description: Default gateway obtained from DHCP
                    type: bool
                  distance_metric:
                    description: Distance metric for this route
                    type: int
                  global:
                    description: Next hop address is global
                    type: bool
                  name:
                    description: Specify name of the next hop
                    type: str
                  multicast:
                    description: multicast route
                    type: bool
                  unicast:
                    description: unicast route (ipv6 specific)
                    type: bool
                  permanent:
                    description: permanent route
                    type: bool
                  tag:
                    description:
                    - Set tag for this route
                    - Refer to vendor documentation for valid values.
                    type: int
                  track:
                    description:
                    - Install route depending on tracked item with tracked object
                      number.
                    - Tracking does not support multicast
                    - Refer to vendor documentation for valid values.
                    type: int
  running_config:
    description:
      - This option is used only with state I(parsed).
      - The value of this option should be the output received from the IOS
        device by executing the command B(show running-config | include ip route|ipv6 route).
      - The state I(parsed) reads the configuration from C(running_config)
        option and transforms it into Ansible structured data as per the
        resource module's argspec and the value is then returned in the
        I(parsed) key within the result.
    type: str
  state:
    description:
      - The state the configuration should be left in
      - The states I(rendered), I(gathered) and I(parsed) does not perform any change
        on the device.
      - The state I(rendered) will transform the configuration in C(config) option to
        platform specific CLI commands which will be returned in the I(rendered) key
        within the result. For state I(rendered) active connection to remote host is
        not required.
      - The state I(gathered) will fetch the running configuration from device and transform
        it into structured data in the format as per the resource module argspec and
        the value is returned in the I(gathered) key within the result.
      - The state I(parsed) reads the configuration from C(running_config) option and
        transforms it into JSON format as per the resource module parameters and the
        value is returned in the I(parsed) key within the result. The value of C(running_config)
        option should be the same format as the output of command I(show running-config
        | include ip route|ipv6 route) executed on device. For state I(parsed) active
        connection to remote host is not required.
    type: str
    choices:
    - merged
    - replaced
    - overridden
    - deleted
    - gathered
    - rendered
    - parsed
    default: merged
"""

EXAMPLES = """
# Using merged

# Before state:
# -------------
# vios#show running-config | include ip route|ipv6 route

- name: Merge provided configuration with device configuration
  cisco.ios.ios_static_routes:
    config:
    - vrf: blue
      address_families:
      - afi: ipv4
        routes:
        - dest: 192.0.2.0/24
          next_hops:
          - forward_router_address: 192.0.2.1
            name: merged_blue
            tag: 50
            track: 150
    - address_families:
      - afi: ipv4
        routes:
        - dest: 198.51.100.0/24
          next_hops:
          - forward_router_address: 198.51.101.1
            name: merged_route_1
            distance_metric: 110
            tag: 40
            multicast: true
          - forward_router_address: 198.51.101.2
            name: merged_route_2
            distance_metric: 30
          - forward_router_address: 198.51.101.3
            name: merged_route_3
      - afi: ipv6
        routes:
        - dest: 2001:DB8:0:3::/64
          next_hops:
          - forward_router_address: 2001:DB8:0:3::2
            name: merged_v6
            tag: 105
    state: merged

# Task Output
# -----------
# before:
# - {}
# commands:
# - ipv6 route 2001:DB8:0:3::/64 2001:DB8:0:3::2 tag 105 name merged_v6
# - ip route 198.51.100.0 255.255.255.0 198.51.101.1 110 tag 40 name merged_route_1 multicast
# - ip route 198.51.100.0 255.255.255.0 198.51.101.2 30 name merged_route_2
# - ip route 198.51.100.0 255.255.255.0 198.51.101.3 name merged_route_3
# - ip route vrf blue 192.0.2.0 255.255.255.0 192.0.2.1 tag 50 name merged_blue track 150
# after:
# - address_families:
#   - afi: ipv4
#     routes:
#     - dest: 198.51.100.0/24
#       next_hops:
#       - forward_router_address: 198.51.101.3
#         name: merged_route_3
#       - distance_metric: 30
#         forward_router_address: 198.51.101.2
#         name: merged_route_2
#       - distance_metric: 110
#         forward_router_address: 198.51.101.1
#         multicast: true
#         name: merged_route_1
#         tag: 40
#   - afi: ipv6
#     routes:
#     - dest: 2001:DB8:0:3::/64
#       next_hops:
#       - forward_router_address: 2001:DB8:0:3::2
#         name: merged_v6
#         tag: 105
# - address_families:
#   - afi: ipv4
#     routes:
#     - dest: 192.0.2.0/24
#       next_hops:
#       - forward_router_address: 192.0.2.1
#         name: merged_blue
#         tag: 50
#         track: 150
#   vrf: blue

# After state:
# ------------
# vios#show running-config | include ip route|ipv6 route
# ip route vrf blue 192.0.2.0 255.255.255.0 192.0.2.1 tag 50 name merged_blue track 150
# ip route 198.51.100.0 255.255.255.0 198.51.101.3 name merged_route_3
# ip route 198.51.100.0 255.255.255.0 198.51.101.2 30 name merged_route_2
# ip route 198.51.100.0 255.255.255.0 198.51.101.1 110 tag 40 name merged_route_1 multicast
# ipv6 route 2001:DB8:0:3::/64 2001:DB8:0:3::2 tag 105 name merged_v6

# Using replaced

# Before state:
# -------------
# vios#show running-config | include ip route|ipv6 route
# ip route vrf blue 192.0.2.0 255.255.255.0 192.0.2.1 tag 50 name merged_blue track 150
# ip route 198.51.100.0 255.255.255.0 198.51.101.3 name merged_route_3
# ip route 198.51.100.0 255.255.255.0 198.51.101.2 30 name merged_route_2
# ip route 198.51.100.0 255.255.255.0 198.51.101.1 110 tag 40 name merged_route_1 multicast
# ipv6 route 2001:DB8:0:3::/64 2001:DB8:0:3::2 tag 105 name merged_v6

- name: Replace provided configuration with device configuration
  cisco.ios.ios_static_routes:
    config:
    - address_families:
      - afi: ipv4
        routes:
        - dest: 198.51.100.0/24
          next_hops:
          - forward_router_address: 198.51.101.1
            name: replaced_route
            distance_metric: 175
            tag: 70
            multicast: true
    state: replaced

# Task Output
# -----------
# before:
# - address_families:
#   - afi: ipv4
#     routes:
#     - dest: 198.51.100.0/24
#       next_hops:
#       - forward_router_address: 198.51.101.3
#         name: merged_route_3
#       - distance_metric: 30
#         forward_router_address: 198.51.101.2
#         name: merged_route_2
#       - distance_metric: 110
#         forward_router_address: 198.51.101.1
#         multicast: true
#         name: merged_route_1
#         tag: 40
#   - afi: ipv6
#     routes:
#     - dest: 2001:DB8:0:3::/64
#       next_hops:
#       - forward_router_address: 2001:DB8:0:3::2
#         name: merged_v6
#         tag: 105
# - address_families:
#   - afi: ipv4
#     routes:
#     - dest: 192.0.2.0/24
#       next_hops:
#       - forward_router_address: 192.0.2.1
#         name: merged_blue
#         tag: 50
#         track: 150
#   vrf: blue
# commands:
# - ip route 198.51.100.0 255.255.255.0 198.51.101.1 175 tag 70 name replaced_route multicast
# - no ip route 198.51.100.0 255.255.255.0 198.51.101.3 name merged_route_3
# - no ip route 198.51.100.0 255.255.255.0 198.51.101.2 30 name merged_route_2
# after:
# - address_families:
#   - afi: ipv4
#     routes:
#     - dest: 198.51.100.0/24
#       next_hops:
#       - distance_metric: 175
#         forward_router_address: 198.51.101.1
#         multicast: true
#         name: replaced_route
#         tag: 70
#   - afi: ipv6
#     routes:
#     - dest: 2001:DB8:0:3::/64
#       next_hops:
#       - forward_router_address: 2001:DB8:0:3::2
#         name: merged_v6
#         tag: 105
# - address_families:
#   - afi: ipv4
#     routes:
#     - dest: 192.0.2.0/24
#       next_hops:
#       - forward_router_address: 192.0.2.1
#         name: merged_blue
#         tag: 50
#         track: 150
#   vrf: blue

# After state:
# ------------
# vios#show running-config | include ip route|ipv6 route
# ip route vrf blue 192.0.2.0 255.255.255.0 192.0.2.1 tag 50 name merged_blue track 150
# ip route 198.51.100.0 255.255.255.0 198.51.101.1 175 tag 70 name replaced_route multicast
# ipv6 route 2001:DB8:0:3::/64 2001:DB8:0:3::2 tag 105 name merged_v6

# Using overridden

# Before state:
# -------------
# vios#show running-config | include ip route|ipv6 route
# ip route vrf blue 192.0.2.0 255.255.255.0 192.0.2.1 tag 50 name merged_blue track 150
# ip route 198.51.100.0 255.255.255.0 198.51.101.1 175 tag 70 name replaced_route multicast
# ipv6 route 2001:DB8:0:3::/64 2001:DB8:0:3::2 tag 105 name merged_v6

- name: Override provided configuration with device configuration
  cisco.ios.ios_static_routes:
    config:
    - vrf: blue
      address_families:
      - afi: ipv4
        routes:
        - dest: 192.0.2.0/24
          next_hops:
          - forward_router_address: 192.0.2.1
            name: override_vrf
            tag: 50
            track: 150
    state: overridden

# Task Output
# -----------
# before:
# - address_families:
#   - afi: ipv4
#     routes:
#     - dest: 198.51.100.0/24
#       next_hops:
#       - distance_metric: 175
#         forward_router_address: 198.51.101.1
#         multicast: true
#         name: replaced_route
#         tag: 70
#   - afi: ipv6
#     routes:
#     - dest: 2001:DB8:0:3::/64
#       next_hops:
#       - forward_router_address: 2001:DB8:0:3::2
#         name: merged_v6
#         tag: 105
# - address_families:
#   - afi: ipv4
#     routes:
#     - dest: 192.0.2.0/24
#       next_hops:
#       - forward_router_address: 192.0.2.1
#         name: merged_blue
#         tag: 50
#         track: 150
#   vrf: blue
# commands:
# - ip route vrf blue 192.0.2.0 255.255.255.0 192.0.2.1 tag 50 name override_vrf track 150
# - no ip route 198.51.100.0 255.255.255.0 198.51.101.1 175 tag 70 name replaced_route multicast
# - no ipv6 route 2001:DB8:0:3::/64 2001:DB8:0:3::2 tag 105 name merged_v6
# after:
# - address_families:
#   - afi: ipv4
#     routes:
#     - dest: 192.0.2.0/24
#       next_hops:
#       - forward_router_address: 192.0.2.1
#         name: override_vrf
#         tag: 50
#         track: 150
#   vrf: blue

# After state:
# ------------
# vios#show running-config | include ip route|ipv6 route
# ip route vrf blue 192.0.2.0 255.255.255.0 192.0.2.1 tag 50 name override_vrf track 150

# Using Deleted

# Before state:
# -------------
#
# vios#show running-config | include ip route|ipv6 route
# ip route vrf blue 192.0.2.0 255.255.255.0 192.0.2.1 name test_vrf track 150 tag 50
# ip route 198.51.100.0 255.255.255.0 198.51.101.1 110 multicast name route_1 tag 40
# ip route 198.51.100.0 255.255.255.0 198.51.101.2 30 name route_2
# ip route 198.51.100.0 255.255.255.0 198.51.101.3 name route_3
# ipv6 route 2001:DB8:0:3::/64 2001:DB8:0:3::2 name test_v6 tag 105

- name: Delete the exact static routes, with all the static routes explicitly mentioned in want
  cisco.ios.ios_static_routes:
    config:
    - vrf: blue
      address_families:
      - afi: ipv4
        routes:
        - dest: 192.0.2.0/24
          next_hops:
          - forward_router_address: 192.0.2.1
            name: test_vrf
            tag: 50
            track: 150
    - address_families:
      - afi: ipv4
        routes:
        - dest: 198.51.100.0/24
          next_hops:
          - forward_router_address: 198.51.101.1
            name: route_1
            distance_metric: 110
            tag: 40
            multicast: true
          - forward_router_address: 198.51.101.2
            name: route_2
            distance_metric: 30
          - forward_router_address: 198.51.101.3
            name: route_3
      - afi: ipv6
        routes:
        - dest: 2001:DB8:0:3::/64
          next_hops:
          - forward_router_address: 2001:DB8:0:3::2
            name: test_v6
            tag: 105
    state: deleted

# Task Output
# -----------
# before:
# - address_families:
#   - afi: ipv4
#     routes:
#     - dest: 198.51.100.0/24
#       next_hops:
#       - forward_router_address: 198.51.101.3
#         name: route_3
#       - distance_metric: 30
#         forward_router_address: 198.51.101.2
#         name: route_2
#       - distance_metric: 110
#         forward_router_address: 198.51.101.1
#         multicast: true
#         name: route_1
#         tag: 40
#   - afi: ipv6
#     routes:
#     - dest: 2001:DB8:0:3::/64
#       next_hops:
#       - forward_router_address: 2001:DB8:0:3::2
#         name: test_v6
#         tag: 105
# - address_families:
#   - afi: ipv4
#     routes:
#     - dest: 192.0.2.0/24
#       next_hops:
#       - forward_router_address: 192.0.2.1
#         name: test_vrf
#         tag: 50
#         track: 150
#   vrf: blue
# commands:
# - no ip route vrf blue 192.0.2.0 255.255.255.0 192.0.2.1 tag 50 name test_vrf track 150
# - no ip route 198.51.100.0 255.255.255.0 198.51.101.3 name route_3
# - no ip route 198.51.100.0 255.255.255.0 198.51.101.2 30 name route_2
# - no ip route 198.51.100.0 255.255.255.0 198.51.101.1 110 tag 40 name route_1 multicast
# - no ipv6 route 2001:DB8:0:3::/64 2001:DB8:0:3::2 tag 105 name test_v6
# after: {}

# After state:
# ------------
# vios#show running-config | include ip route|ipv6 route

# Before state:
# -------------
# vios#show running-config | include ip route|ipv6 route
# ip route vrf blue 192.0.2.0 255.255.255.0 192.0.2.1 name test_vrf track 150 tag 50
# ip route 198.51.100.0 255.255.255.0 198.51.101.1 110 multicast name route_1 tag 40
# ip route 198.51.100.0 255.255.255.0 198.51.101.2 30 name route_2
# ip route 198.51.100.0 255.255.255.0 198.51.101.3 name route_3
# ipv6 route 2001:DB8:0:3::/64 2001:DB8:0:3::2 name test_v6 tag 105

- name: Delete destination specific static routes
  cisco.ios.ios_static_routes:
    config:
    - address_families:
      - afi: ipv4
        routes:
        - dest: 198.51.100.0/24
    state: deleted

# Task Output
# -----------
# before:
# - address_families:
#   - afi: ipv4
#     routes:
#     - dest: 198.51.100.0/24
#       next_hops:
#       - forward_router_address: 198.51.101.3
#         name: route_3
#       - distance_metric: 30
#         forward_router_address: 198.51.101.2
#         name: route_2
#       - distance_metric: 110
#         forward_router_address: 198.51.101.1
#         multicast: true
#         name: route_1
#         tag: 40
#   - afi: ipv6
#     routes:
#     - dest: 2001:DB8:0:3::/64
#       next_hops:
#       - forward_router_address: 2001:DB8:0:3::2
#         name: test_v6
#         tag: 105
# - address_families:
#   - afi: ipv4
#     routes:
#     - dest: 192.0.2.0/24
#       next_hops:
#       - forward_router_address: 192.0.2.1
#         name: test_vrf
#         tag: 50
#         track: 150
#   vrf: blue
# commands:
# - no ip route 198.51.100.0 255.255.255.0 198.51.101.3 name route_3
# - no ip route 198.51.100.0 255.255.255.0 198.51.101.2 30 name route_2
# - no ip route 198.51.100.0 255.255.255.0 198.51.101.1 110 tag 40 name route_1 multicast
# after:
# - address_families:
#   - afi: ipv6
#     routes:
#     - dest: 2001:DB8:0:3::/64
#       next_hops:
#       - forward_router_address: 2001:DB8:0:3::2
#         name: test_v6
#         tag: 105
# - address_families:
#   - afi: ipv4
#     routes:
#     - dest: 192.0.2.0/24
#       next_hops:
#       - forward_router_address: 192.0.2.1
#         name: test_vrf
#         tag: 50
#         track: 150
#   vrf: blue

# After state:
# ------------
# vios#show running-config | include ip route|ipv6 route
# ip route vrf blue 192.0.2.0 255.255.255.0 192.0.2.1 tag 50 name test_vrf track 150
# ipv6 route 2001:DB8:0:3::/64 2001:DB8:0:3::2 tag 105 name test_v6

# Before state:
# -------------
# vios#show running-config | include ip route|ipv6 route
# ip route vrf blue 192.0.2.0 255.255.255.0 192.0.2.1 name test_vrf track 150 tag 50
# ip route 198.51.100.0 255.255.255.0 198.51.101.1 110 multicast name route_1 tag 40
# ip route 198.51.100.0 255.255.255.0 198.51.101.2 30 name route_2
# ip route 198.51.100.0 255.255.255.0 198.51.101.3 name route_3
# ipv6 route 2001:DB8:0:3::/64 2001:DB8:0:3::2 name test_v6 tag 105

- name: Delete vrf specific static routes
  cisco.ios.ios_static_routes:
    config:
    - vrf: blue
    state: deleted

# Task Output
# -----------
# before:
# - address_families:
#   - afi: ipv4
#     routes:
#     - dest: 198.51.100.0/24
#       next_hops:
#       - forward_router_address: 198.51.101.3
#         name: route_3
#       - distance_metric: 30
#         forward_router_address: 198.51.101.2
#         name: route_2
#       - distance_metric: 110
#         forward_router_address: 198.51.101.1
#         multicast: true
#         name: route_1
#         tag: 40
#   - afi: ipv6
#     routes:
#     - dest: 2001:DB8:0:3::/64
#       next_hops:
#       - forward_router_address: 2001:DB8:0:3::2
#         name: test_v6
#         tag: 105
# - address_families:
#   - afi: ipv4
#     routes:
#     - dest: 192.0.2.0/24
#       next_hops:
#       - forward_router_address: 192.0.2.1
#         name: test_vrf
#         tag: 50
#         track: 150
#   vrf: blue
# commands:
# - no ip route vrf blue 192.0.2.0 255.255.255.0 192.0.2.1 tag 50 name test_vrf track 150
# after:
# - address_families:
#   - afi: ipv4
#     routes:
#     - dest: 198.51.100.0/24
#       next_hops:
#       - forward_router_address: 198.51.101.3
#         name: route_3
#       - distance_metric: 30
#         forward_router_address: 198.51.101.2
#         name: route_2
#       - distance_metric: 110
#         forward_router_address: 198.51.101.1
#         multicast: true
#         name: route_1
#         tag: 40
#   - afi: ipv6
#     routes:
#     - dest: 2001:DB8:0:3::/64
#       next_hops:
#       - forward_router_address: 2001:DB8:0:3::2
#         name: test_v6
#         tag: 105

# After state:
# ------------
# vios#show running-config | include ip route|ipv6 route
# ip route 198.51.100.0 255.255.255.0 198.51.101.3 name route_3
# ip route 198.51.100.0 255.255.255.0 198.51.101.2 30 name route_2
# ip route 198.51.100.0 255.255.255.0 198.51.101.1 110 tag 40 name route_1 multicast
# ipv6 route 2001:DB8:0:3::/64 2001:DB8:0:3::2 tag 105 name test_v6

# Before state:
# -------------
# vios#show running-config | include ip route|ipv6 route
# ip route vrf blue 192.0.2.0 255.255.255.0 192.0.2.1 name test_vrf track 150 tag 50
# ip route 198.51.100.0 255.255.255.0 198.51.101.1 110 multicast name route_1 tag 40
# ip route 198.51.100.0 255.255.255.0 198.51.101.2 30 name route_2
# ip route 198.51.100.0 255.255.255.0 198.51.101.3 name route_3
# ipv6 route 2001:DB8:0:3::/64 2001:DB8:0:3::2 name test_v6 tag 105

- name: Delete ALL configured static routes
  cisco.ios.ios_static_routes:
    state: deleted

# Task Output
# -----------
# before:
# - address_families:
#   - afi: ipv4
#     routes:
#     - dest: 198.51.100.0/24
#       next_hops:
#       - forward_router_address: 198.51.101.3
#         name: route_3
#       - distance_metric: 30
#         forward_router_address: 198.51.101.2
#         name: route_2
#       - distance_metric: 110
#         forward_router_address: 198.51.101.1
#         multicast: true
#         name: route_1
#         tag: 40
#   - afi: ipv6
#     routes:
#     - dest: 2001:DB8:0:3::/64
#       next_hops:
#       - forward_router_address: 2001:DB8:0:3::2
#         name: test_v6
#         tag: 105
# - address_families:
#   - afi: ipv4
#     routes:
#     - dest: 192.0.2.0/24
#       next_hops:
#       - forward_router_address: 192.0.2.1
#         name: test_vrf
#         tag: 50
#         track: 150
#   vrf: blue
# commands:
# - no ip route 198.51.100.0 255.255.255.0 198.51.101.3 name route_3
# - no ip route 198.51.100.0 255.255.255.0 198.51.101.2 30 name route_2
# - no ip route 198.51.100.0 255.255.255.0 198.51.101.1 110 tag 40 name route_1 multicast
# - no ipv6 route 2001:DB8:0:3::/64 2001:DB8:0:3::2 tag 105 name test_v6
# - no ip route vrf blue 192.0.2.0 255.255.255.0 192.0.2.1 tag 50 name test_vrf track 150
# after: {}

# After state:
# -------------
# vios#show running-config | include ip route|ipv6 route


# Using gathered

# Before state:
# -------------
# vios#show running-config | include ip route|ipv6 route
# ip route vrf blue 192.0.2.0 255.255.255.0 192.0.2.1 name test_vrf track 150 tag 50
# ip route 198.51.100.0 255.255.255.0 198.51.101.1 110 multicast name route_1 tag 40
# ip route 198.51.100.0 255.255.255.0 198.51.101.2 30 name route_2
# ip route 198.51.100.0 255.255.255.0 198.51.101.3 name route_3
# ipv6 route 2001:DB8:0:3::/64 2001:DB8:0:3::2 name test_v6 tag 105

- name: Gather facts of static routes
  cisco.ios.ios_static_routes:
    config:
    state: gathered

# Task Output
# -----------
# gathered:
# - address_families:
#   - afi: ipv4
#     routes:
#     - dest: 198.51.100.0/24
#       next_hops:
#       - forward_router_address: 198.51.101.3
#         name: route_3
#       - distance_metric: 30
#         forward_router_address: 198.51.101.2
#         name: route_2
#       - distance_metric: 110
#         forward_router_address: 198.51.101.1
#         multicast: true
#         name: route_1
#         tag: 40
#   - afi: ipv6
#     routes:
#     - dest: 2001:DB8:0:3::/64
#       next_hops:
#       - forward_router_address: 2001:DB8:0:3::2
#         name: test_v6
#         tag: 105
# - address_families:
#   - afi: ipv4
#     routes:
#     - dest: 192.0.2.0/24
#       next_hops:
#       - forward_router_address: 192.0.2.1
#         name: test_vrf
#         tag: 50
#         track: 150
#   vrf: blue

# Using rendered

- name: Render the commands for provided configuration
  cisco.ios.ios_static_routes:
    config:
    - vrf: blue
      address_families:
      - afi: ipv4
        routes:
        - dest: 192.0.2.0/24
          next_hops:
          - forward_router_address: 192.0.2.1
            name: test_vrf
            tag: 50
            track: 150
    - address_families:
      - afi: ipv4
        routes:
        - dest: 198.51.100.0/24
          next_hops:
          - forward_router_address: 198.51.101.1
            name: route_1
            distance_metric: 110
            tag: 40
            multicast: true
          - forward_router_address: 198.51.101.2
            name: route_2
            distance_metric: 30
          - forward_router_address: 198.51.101.3
            name: route_3
      - afi: ipv6
        routes:
        - dest: 2001:DB8:0:3::/64
          next_hops:
          - forward_router_address: 2001:DB8:0:3::2
            name: test_v6
            tag: 105
    state: rendered

# Task Output
# -----------
# rendered:
# - ip route vrf blue 192.0.2.0 255.255.255.0 192.0.2.1 tag 50 name test_vrf track 150
# - ip route 198.51.100.0 255.255.255.0 198.51.101.1 110 tag 40 name route_1 multicast
# - ip route 198.51.100.0 255.255.255.0 198.51.101.2 30 name route_2
# - ip route 198.51.100.0 255.255.255.0 198.51.101.3 name route_3
# - ipv6 route 2001:DB8:0:3::/64 2001:DB8:0:3::2 tag 105 name test_v6
"""

RETURN = """
before:
  description: The configuration as structured data prior to module invocation.
  returned: always
  type: list
  sample: The configuration returned will always be in the same format of the parameters above.
after:
  description: The configuration as structured data after module completion.
  returned: when changed
  type: list
  sample: The configuration returned will always be in the same format of the parameters above.
commands:
  description: The set of commands pushed to the remote device
  returned: always
  type: list
  sample: ['ip route vrf test 172.31.10.0 255.255.255.0 10.10.10.2 name new_test multicast']
rendered:
  description: The set of CLI commands generated from the value in C(config) option
  returned: When C(state) is I(rendered)
  type: list
  sample:
    - ip route 198.51.100.0 255.255.255.0 198.51.101.3 name route_3
    - ipv6 route 2001:DB8:0:3::/64 2001:DB8:0:3::2 tag 105 name test_v6
gathered:
  description:
  - The configuration as structured data transformed for the running configuration
    fetched from remote host
  returned: When C(state) is I(gathered)
  type: list
  sample: >
    The configuration returned will always be in the same format
    of the parameters above.
parsed:
  description:
  - The configuration as structured data transformed for the value of
    C(running_config) option
  returned: When C(state) is I(parsed)
  type: list
  sample: >
    The configuration returned will always be in the same format
    of the parameters above.
"""


from ansible.module_utils.basic import AnsibleModule

from ansible_collections.cisco.ios.plugins.module_utils.network.ios.argspec.static_routes.static_routes import (
    Static_routesArgs,
)
from ansible_collections.cisco.ios.plugins.module_utils.network.ios.config.static_routes.static_routes import (
    Static_routes,
)


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(
        argument_spec=Static_routesArgs.argument_spec,
        mutually_exclusive=[["config", "running_config"]],
        required_if=[
            ["state", "merged", ["config"]],
            ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]],
            ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )

    result = Static_routes(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()