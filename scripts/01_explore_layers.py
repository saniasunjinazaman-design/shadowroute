"""Lesson 1 - Explore Scapy from the inside out.
Run:  sudo python3 01_explore_layers.py
"""
from scapy.all import ls, lsc, IP, TCP, ICMP

# lsc() lists every Scapy command (send, sniff, rdpcap, sr1, ...)
print("--- Scapy commands ---")
lsc()

# ls(Layer) shows every field of a protocol, its type and its default value
print("\n--- Fields in an IP Header ---")
ls(IP)

print("\n--- Fields in a TCP Header ---")
ls(TCP)

print("\n--- Fields in an ICMP Header ---")
ls(ICMP)
