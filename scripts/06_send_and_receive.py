"""Lesson 6 - send() (fire and forget) and sr1() (send one, get first reply).
Needs root and a working network.
Run:  sudo python3 06_send_and_receive.py
"""
from scapy.all import IP, ICMP, send, sr1

pkt = IP(dst="8.8.8.8") / ICMP()

# ---- send(): Layer 3, does NOT wait for an answer ----
print("[*] Sending one ping packet...")
send(pkt, verbose=False)
print("[+] Sent!")

# ---- sr1(): Layer 3, waits for the FIRST matching reply ----
print("\n[*] Sending ping and waiting for reply...")
reply = sr1(pkt, timeout=2, verbose=False)   # timeout stops it hanging forever

if reply is None:
    print("[-] No response received (host down or filtered).")
else:
    print(f"[+] Received reply from: {reply.src}")
    print(f"[+] Response TTL: {reply.ttl}")
    print(f"[+] ICMP Type: {reply[ICMP].type}")   # 0 = Echo Reply
