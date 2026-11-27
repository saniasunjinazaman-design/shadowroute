"""Hands-on challenges 1-3 (solutions).
Run:  sudo python3 10_challenges.py
"""
from scapy.all import IP, UDP, ICMP, Raw, hexdump, sr1

# ---------- Challenge 1: The Detective ----------
print("=== Challenge 1 ===")
p = IP(dst="192.168.1.254", ttl=42)
print("Default proto number:", p.proto)   # 0 (not set yet; Scapy fills it when a layer is stacked on top)
print("TTL is:", p.ttl)

# ---------- Challenge 2: Layer Assembly ----------
print("\n=== Challenge 2 ===")
pkt = IP(dst="8.8.8.8") / UDP(dport=53) / Raw(b"test query")
print(pkt.summary())
hexdump(pkt)

# ---------- Challenge 3: Response Inspector ----------
# (the lab text uses 127.0.0.1; change the dst below to test localhost)
print("\n=== Challenge 3 ===")
response = sr1(IP(dst="8.8.8.8") / ICMP(), timeout=2, verbose=False)

if response and response.haslayer(ICMP):
    if response[ICMP].type == 0:
        print("[+] Host is alive!")
    else:
        print("Got reply but not an Echo Reply, type is:", response[ICMP].type)
else:
    print("No response received")
