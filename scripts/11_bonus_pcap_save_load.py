"""Bonus - Save captured packets to a .pcap file and load them back.
The .pcap file can also be opened in Wireshark.
Run:  sudo python3 11_bonus_pcap_save_load.py
"""
from scapy.all import sniff, wrpcap, rdpcap

print("[*] Capturing 10 packets (create some traffic)...")
pkts = sniff(count=10)

wrpcap("captured_traffic.pcap", pkts)      # save
print("[+] Saved captured_traffic.pcap")

saved_pkts = rdpcap("captured_traffic.pcap")   # load
print(f"Loaded {len(saved_pkts)} packets.")
saved_pkts.summary()
