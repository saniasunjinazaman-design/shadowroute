"""Lesson 7 (A + B) - Simple sniffing and BPF filters.
While this runs, create traffic: open a website, or run `ping 8.8.8.8`
in a second terminal.
Run:  sudo python3 07_sniff_basics.py
"""
from scapy.all import sniff

# A) Capture 5 packets of any kind
print("[*] Capturing 5 packets (open a website to create traffic)...")
packets = sniff(count=5)
packets.summary()

# B1) Only ICMP packets (run `ping 8.8.8.8` in another terminal)
print("\n[*] Capturing 3 ICMP packets (run: ping 8.8.8.8)...")
icmp_pkts = sniff(filter="icmp", count=3)
icmp_pkts.summary()

# B2) Only TCP traffic on port 80 or 443 (browse a website)
print("\n[*] Capturing 10 web packets (browse a website)...")
web_pkts = sniff(filter="tcp and (port 80 or port 443)", count=10)
web_pkts.summary()
