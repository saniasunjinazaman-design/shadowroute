"""Lesson 2 - Crafting your first packets (nothing is sent on the network).
Run:  sudo python3 02_craft_packets.py
"""
from scapy.all import IP, TCP

# 1) A default IP packet
my_packet = IP()
print("Source IP:", my_packet.src)        # 127.0.0.1 (because dst defaults to localhost)
print("Destination IP:", my_packet.dst)   # 127.0.0.1
print("TTL:", my_packet.ttl)              # 64

# 2) Customising fields when creating the packet
custom_ip = IP(dst="8.8.8.8", ttl=128)
print("Custom Dest:", custom_ip.dst)
print("Custom TTL:", custom_ip.ttl)

# 3) A default TCP layer
t = TCP(dport=443)
print("Source Port:", t.sport)            # 20 (Scapy's default)
print("Destination Port:", t.dport)       # 443
