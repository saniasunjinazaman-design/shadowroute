"""Bonus - Very simple TCP SYN port scanner (ports 20-100).

!!! Only scan machines you own or have written permission to test !!!
(e.g. your own lab VM or 127.0.0.1)

Run:  sudo python3 13_bonus_port_scanner.py
"""
from scapy.all import IP, TCP, sr1

target = input("Target IP (e.g. 127.0.0.1): ").strip() or "127.0.0.1"

for port in range(20, 101):
    pkt = IP(dst=target) / TCP(dport=port, flags="S")      # S = SYN
    reply = sr1(pkt, timeout=1, verbose=0)

    # SYN-ACK (0x12) -> port is OPEN.  RST -> closed.  No reply -> filtered / host down.
    if reply is not None and reply.haslayer(TCP) and reply[TCP].flags == 0x12:
        print(f"{port}: open")
