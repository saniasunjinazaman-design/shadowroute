"""Lesson 4 - Viewing a packet as raw bytes and as a hex dump.
Run:  sudo python3 04_bytes_hexdump.py
"""
from scapy.all import IP, ICMP, hexdump

pkt = IP(dst="192.168.1.1") / ICMP()

raw_bytes = bytes(pkt)
print("Raw Bytes:", raw_bytes)
print("Packet Length in bytes:", len(raw_bytes))   # 28 = 20 (IP) + 8 (ICMP)

print("\n--- Hex Dump ---")
hexdump(pkt)
