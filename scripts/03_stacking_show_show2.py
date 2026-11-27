"""Lesson 3 - Stacking layers with '/' and show() vs show2().
Run:  sudo python3 03_stacking_show_show2.py
"""
from scapy.all import IP, ICMP, Raw

# Layer 3 / Layer 4 / Payload
ping_pkt = IP(dst="1.1.1.1") / ICMP() / Raw(b"Hello World")

print("--- Summary ---")
print(ping_pkt.summary())

print("\n--- Detailed Tree View ---")
ping_pkt.show()

# show()  -> only what YOU defined (checksums / lengths are still None)
print("\n--- show() ---")
ping_pkt.show()

# show2() -> Scapy builds the packet, fills lengths + checksums,
#            then re-reads it as if it came off the wire
print("\n--- show2() ---")
ping_pkt.show2()
