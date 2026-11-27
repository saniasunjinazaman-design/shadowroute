"""Lesson 7 (C) - Real-time processing with a prn callback.
Run:  sudo python3 08_sniff_callback.py      (Ctrl+C to stop)
"""
from scapy.all import sniff, IP, TCP


def packet_handler(packet):
    if packet.haslayer(IP):
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        proto = packet[IP].proto          # 6 = TCP, 17 = UDP, 1 = ICMP

        info = f"[IP] {src_ip} -> {dst_ip} (Proto: {proto})"
        if packet.haslayer(TCP):
            info += (f" | TCP Port: {packet[TCP].sport} -> {packet[TCP].dport}"
                     f" | Flags: {packet[TCP].flags}")
        print(info)


print("Sniffing started. Press Ctrl+C to stop...")
try:
    # store=False -> do not keep packets in RAM (safe for long runs)
    sniff(filter="ip", prn=packet_handler, store=False)
except KeyboardInterrupt:
    print("\nStopped.")
