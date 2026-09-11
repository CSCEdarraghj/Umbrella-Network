"""
Umbrella Network - mini_switch.py

This file provides a safe mini switch lab for the Umbrella Network Project.

It demonstrates:
- Basic switch behavior
- Mac address learning
- Frame forwarding
- FLooding unknown destinations
- Dropping frames that do not need forwarding
- Safe simulated networking without changing real system settings
"""

DEFAULT_SWITCH_PORTS = 4

def print_mac_table(mac_table):
    """
    Display the current MAC address table.

    A real switch uses a MAC address table to remember which device
    is connected to which switch port.
    """

    print("\nMAC Address Table")
    print("------------------")

    if not mac_table:
        print("No MAC addresses learned yet.")
        return
    
    for mac_address, port in mac_table.items():
        print(f"{mac_address} -> Port {port}")

def learn_source_mac(mac_table, source_mac, source_port):
    """
    Learn the source MAC address from an incoming frame.

    Switches learn by looking at the source MAC address of traffic.
    """

    mac_table[source_mac] = source_port
    print(f"[LEARN] Learned {source_mac} on Port {source_port}")

def get_flood_ports(source_port, total_ports):
    """
    Return every port except the incoming source port.

    When a switch does not know where the destination MAC address is,
    it floods the frame out all other ports.
    """

    flood_ports = []

    for port in range(1, total_ports + 1):
        if port != source_port:
            flood_ports.append(port)

    return flood_ports

def forward_frame(mac_table, source_mac, destination_mac, source_port, total_ports=DEFAULT_SWITCH_PORTS):
    """
    Simulate how a learning switch handles one Ethernet frame.
    """

    print("\nIncoming Ethernet Frame")
    print("---------------------")
    print(f"Source MAC:      {source_mac}")
    print(f"Destination MAC: {destination_mac}")
    print(f"Incoming Port:   {source_port}")

    # Step 1: Learn where the source device is.
    learn_source_mac(mac_table, source_mac, source_port)

    # Step 2: Check if the destination is already known.
    if destination_mac in mac_table:
        destination_port = mac_table[destination_mac]

        if destination_port == source_port:
            print("[DROP] Destination is on the same port.")
            print("[DROP] No forwarding needed.")

        else:
            print(f"[FORWARD] Destination known.")
            print(f"[FORWARD] Sending frame out Port {destination_port}")
    
    else:
        flood_ports = get_flood_ports(source_port, total_ports)

        print("[FLOOD] Destination unknown.")
        print(f"[FLOOD] Sending frame out Ports: {flood_ports}")

def run_switch_demo():
    """
    Run the Umbrella Network mini switch demo.
    """

    print("=" * 60)
    print("Umbrella Network - Mini Switch Demo")
    print("=" * 60)
    print()
    print("This lab simulates how an Ethernet switch learns MAC addresses.")
    print("It is safe and does not change real network settings.")
    print()

    mac_table = {}

    demo_frames = [
        {
            "source_mac": "AA:AA:AA:AA:AA:01",
            "destination_mac": "BB:BB:BB:BB:BB:02",
            "source_port": 1
        },
        {
            "source_mac": "BB:BB:BB:BB:BB:02",
            "destination_mac": "AA:AA:AA:AA:AA:01",
            "source_port": 2
        },
        {
            "source_mac": "CC:CC:CC:CC:CC:03",
            "destination_mac": "AA:AA:AA:AA:AA:01",
            "source_port": 3
        },
        {
            "source_mac": "AA:AA:AA:AA:AA:01",
            "destination_mac": "CC:CC:CC:CC:CC:03",
            "source_port": 1
        },
        {
            "source_mac": "CC:CC:CC:CC:CC:03",
            "destination_mac": "CC:CC:CC:CC:CC:03",
            "source_port": 3
        }
    ]


    for frame in demo_frames:
        forward_frame(
            mac_table=mac_table,
            source_mac=frame["source_mac"],
            destination_mac=frame["destination_mac"],
            source_port=frame["source_port"],
            total_ports=DEFAULT_SWITCH_PORTS
        )

        print_mac_table(mac_table)
    
    print("\n[+] Mini switch demo complete.")