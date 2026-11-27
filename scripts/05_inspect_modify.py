"""Lesson 5 - Reading, checking and changing fields of an existing packet.
Run:  sudo python3 05_inspect_modify.py
"""
from scapy.all import IP, TCP, ICMP

pkt = IP(src="10.0.0.1", dst="10.0.0.2") / TCP(sport=1234, dport=80, flags="S")

# Reading fields
print("Destination IP:", pkt[IP].dst)
print("Destination Port:", pkt[TCP].dport)
print("TCP Flags:", pkt[TCP].flags)

# Checking whether a layer exists
if pkt.haslayer(TCP):
    print("This packet contains TCP!")
if not pkt.haslayer(ICMP):
    print("This packet does NOT contain ICMP!")

# Changing a value on the fly
pkt[TCP].dport = 443

# Adding a payload to an existing packet
pkt = pkt / "New Payload Added Later"
pkt.show()
