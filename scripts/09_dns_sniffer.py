"""Lesson 7 (E) - Live DNS request sniffer.
Open websites in a browser while this runs.
Run:  sudo python3 09_dns_sniffer.py         (Ctrl+C to stop)
"""
from scapy.all import sniff, DNS, DNSQR, IP


def handle_packet(pkt):
    # Needs a DNS layer AND a DNS Question Record (DNSQR)
    if pkt.haslayer(DNS) and pkt.haslayer(DNSQR):
        query = pkt[DNSQR].qname.decode("utf-8", errors="ignore")  # bytes -> text
        src_ip = pkt[IP].src
        print(f"[DNS Query] {src_ip} -> {query}")


print("[*] Starting DNS Sniffer... Press Ctrl+C to stop.")
try:
    sniff(filter="udp port 53", prn=handle_packet, store=0)
except KeyboardInterrupt:
    print("\nStopped.")
