"""Bonus - Send our own DNS request to 8.8.8.8 and show the answer.
Run:  sudo python3 12_bonus_dns_request.py
"""
from scapy.all import IP, UDP, DNS, DNSQR, sr1

dns_pkt = (
    IP(dst="8.8.8.8")
    / UDP(dport=53)
    / DNS(rd=1, qd=DNSQR(qname="google.com"))   # rd=1 -> "recursion desired"
)

response = sr1(dns_pkt, timeout=3, verbose=0)
if response:
    response.show()
else:
    print("[-] No DNS response received.")
