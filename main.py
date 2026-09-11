#!/usr/bin/env python3
"""Umbrella Network main launcher
This file is the command-line control center for the Umbrella Network project.
It routes commands to the other project files without doing all the networking logic here.

This launcher is safe:
- It does not change system network settings.
- It only calls helper functions from the other Umbrella Network modules.
- It uses safe defaults if config.json is missing or broken.
"""

import socket
import threading
import http.server
import socketserver
import argparse
import importlib
import json
from pathlib import Path
from datetime import datetime

BANNER = r"""
=======================================
        Umbrella Network
    A beginner-friendly Networking Toolkit
=======================================
"""

# These settings are used if config.json is missing or broken.
DEFAULT_CONFIG = {
    "project_name": "Umbrella Network",
    "version": "1.0",
    "description": "A beginner-friendly networking toolkit for safe diagnostics, DNS lookups, port checks, and IP configuration planning.",
    "default_ping_host": "8.8.8.8",
    "default_dns_host": "example.com",
    "traceroute_host": "example.com",
    "default_port_host": "example.com",
    "default_port": 80,
    "default_ports": [22, 53, 80, 443],
    "port_timeout": 2,
    "default_ip_address": "192.168.1.25",
    "default_subnet_mask": "255.255.255.0",
    "default_gateway": "192.168.1.1",
    "default_dns_server": "8.8.8.8",
    "web_host": "127.0.0.1",
    "web_port": 8080,
    "p2p_host": "127.0.0.1",
    "p2p_port": 9090,
    "allow_large_port_scans": False,
    "max_common_ports_only": True,
    "requires_permission_reminder": True
}

def print_banner():
    """Print the Umbrella Network startup banner"""

    print(BANNER)

def load_config(config_path = "config.json"):
    """
    Load settings from config.json when it exists.

    If the file is missing, unreadable, or broken JSON, this function
    returns a safe copy of DEFAULT_CONFIG instead.
    """

    # Starts with safe defaults so missing keys don't break the launcher.
    config = DEFAULT_CONFIG.copy()

    # Converts the config file name into a Path object.
    path = Path(config_path)

    # If config.json does not exist, use defaults.
    if not path.exists():
        return config
    
    try:
        # Open and read the JSON config file.
        with path.open("r", encoding="utf-8") as file:
            user_config = json.load(file)

        # Only merge the file if it contains a JSON object/dictionary.
        if isinstance(user_config, dict):
            config.update(user_config)
        else:
            print("Warning: config.json must contain a JSON object using defaults.")

    except json.JSONDecodeError:
        # This catches broken JSON syntax.
        print("Warning: config.json has invalid JSON using defaults.")

    except OSError:
        # This catches file permission/read errors.
        print("Warning: Could not read config.json using defaults.")

    # Returns the final config dictionary
    return config

def safe_import(module_name):
    """
    Import a project module safely.

    If a module like net_diag.py is missing, this prints a clear message
    instead of crashing with a giant traceback.
    """

    try:
        # Try importing the requested module by name.
        return importlib.import_module(module_name)
    
    except ModuleNotFoundError as error:
        # Only handle the exact missing module we tried to import.
        if error.name == module_name:
            print(f"Missing project file: {module_name}.py")
            print("Make sure this file exists in the same folder as main.py")
            return None
        
        # If the missing module is something inside that file, re-raise it.
        raise

def print_result(result):
    """
    Print returned text from helper functions.

    Some project functions may print directly and return None.
    That is okay, so this function only prints when there is something to print.
    """

    if result is not None:
        print(result)

def get_int_config(config, key, fallback):
    """
    Get an integer value from the config.

    This is mainly used for ports, because command-line ports and JSON ports
    should always become integers before being used.
    """

    try:
        return int(config.get(key, fallback))
    except (TypeError, ValueError):
        return fallback
    
def handle_dns(args, config):
    """
    Handle:
    python3 main.py dns

    This calls dns_tools.run_dns_tools(config)
    """

    dns_tools = safe_import("tools.dns_tools")

    if dns_tools is None:
        return
    
    if not hasattr(dns_tools, "run_dns_tools"):
        print("dns_tools.py is missing the function run_dns_tools(config)")
        return
    
    result = dns_tools.run_dns_tools(config)
    print_result(result)

def handle_ports(args, config):
    """
    Handle:
    python3 main.py ports

    This calls port_tools.run_port_tools(config)
    """

    port_tools = safe_import("tools.port_tools")

    if port_tools is None:
        return
    
    if not hasattr(port_tools, "run_port_tools"):
        print("port_tools.py is missing the function run_port_tools(config)")
        return
    
    result = port_tools.run_port_tools(config)
    print_result(result)

def handle_diagnose(args, config):
    """
    Handle:
    python3 main.py diagnose

    This calls net_diag.run_diagnostics(config)
    """

    #Safely import net_diag.py
    net_diag = safe_import("tools.net_diag")

    #Stop if the file is missing.
    if net_diag is None:
        return
    
    # Make sure the required function exists
    if not hasattr(net_diag, "run_diagnostics"):
        print("net_diag.py is missing the function run_diagnostics(config).")
        return
    
    # Call the diagnostics function from net_diag.py.
    result = net_diag.run_diagnostics(config)

    # Print a clean, readable diagnostics report.
    if isinstance(result, dict):
        print("\nUmbrella Network Diagnostics")
        print("-" * 32)

        print(f"\nHostname: {result.get('hostname', 'Unknown')}")
        print(f"Local IP: {result.get('local_ip', 'Unknown')}")

        print("\nNetwork Interfaces")
        interfaces = result.get("interfaces", [])
        if interfaces:
            for interface in interfaces:
                print(f"- {interface}")
        else:
            print("- None found")

        print("\nSystem Information")
        system_info = result.get("system_info", {})
        if system_info:
            for key, value in system_info.items():
                print(f"- {key.replace('_', ' ').title()}: {value}")
        else:
            print("- No system information available")

        print("\nPing Test")
        print(result.get("ping_test", "No ping result available"))

        print("\nDNS Lookup")
        print(result.get("dns_lookup", "No DNS result available"))

        print("\nPort Check")
        print(result.get("port_check", "No port check result available"))

    else:
        print_result(result)

def handle_config(args, config):
    """
    Handle:
    python3 main.py config --mode dhcp
    python3 main.py config --mode static --ip ... --subnet ... --gateway ... --dns ...

    This does not change real system network settings.
    It only builds and prints a safe plan.
    """
    # Safely import config_planner.py
    config_planner = safe_import("tools.config_planner")

    # Stop if the file is missing.
    if config_planner is None:
        return
    
    # DHCP mode means the user wants an automatic network settings plan.
    if args.mode == "dhcp":
        if not hasattr(config_planner, "build_dhcp_plan"):
            print("config_planner.py is missing the function build_dhcp_plan().")
            return
        
        result = config_planner.build_dhcp_plan()
        print_result(result)
        return
    
    # Static mode means the user wants a manual IP configuration plan.
    if args.mode == "static":
        if not hasattr(config_planner, "build_static_ip_plan"):
            print("config_planner.py is missing the function build_static_ip_plan(...).")
            return
        
        
        ip = args.ip or config.get("default_ip_address", DEFAULT_CONFIG["default_ip_address"])
        subnet = args.subnet or config.get("default_subnet_mask", DEFAULT_CONFIG["default_subnet_mask"])
        gateway = args.gateway or config.get("default_gateway", DEFAULT_CONFIG["default_gateway"])
        dns = args.dns or config.get("default_dns_server", DEFAULT_CONFIG["default_dns_server"])

        # Build the safe static IP plan.
        result = config_planner.build_static_ip_plan(
            ip=ip,
            subnet=subnet,
            gateway=gateway,
            dns=dns,
        )

        print_result(result)
        return
    
    # This should rarely happen because argparse controls the choices.
    print("Unknown config mode. Use --mode dhcp or --mode static.")

def handle_p2p_server(args, config):
    """
    Handle:
    python3 main.py p2p-server

    This starts the simple rendezvous server from p2p_lab.py.
    """

    # Safely import p2p_lab.py.
    p2p_lab = safe_import("labs.p2p_lab")

    # Stop if the file is missing.
    if p2p_lab is None:
        return
    
    # Make sure the required function exists.
    if not hasattr(p2p_lab, "run_p2p_server"):
        print("p2p_lab.py is missing the function run_p2p_server(config).")
        return
    
    if args.host:
        config["p2p_host"] = args.host 

    if args.port is not None:
        config["p2p_port"] = args.port 

    # Start the rendezvous server.
    result = p2p_lab.run_p2p_server(config)
    print_result(result)

def handle_p2p_peer(args, config):
    """
    Handle:
    python3 main.py p2p-peer

    This starts a simple peer from p2p_lab.py.
    """

    # Safely import p2p_lab.py.
    p2p_lab = safe_import("labs.p2p_lab")

    # Stop if the file is missing
    if p2p_lab is None:
        return
    
    # Make sure the required function exists.
    if not hasattr(p2p_lab, "run_p2p_peer"):
        print("p2p_lab.py is missing the function run_p2p_peer(config).")
        return
    
    if args.server_host:
        config["p2p_host"] = args.server_host

    if args.server_port is not None:
        config["p2p_port"] = args.server_port

    result = p2p_lab.run_p2p_peer(config)
    print_result(result)

def handle_switch_demo(args, config):
    """
    Handle:
    python3 main.py switch-demo

    This runs the learning switch demo from mini_switch.py.
    """

    # Safely import mini_switch.py
    mini_switch = safe_import("labs.mini_switch")

    # Stop if the file is missing
    if mini_switch is None:
        return
    
    # Make sure the required function exists.
    if not hasattr(mini_switch, "run_switch_demo"):
        print("mini_switch.py is missing the function run_switch_demo().")
        return
    
    # Run the switch demo.
    result = mini_switch.run_switch_demo()

    # Print returned output if the function returned text.
    print_result(result)

def handle_web(args, config):
    """
    Handle:
    python3 main.py web

    This starts the simple web server from web_server.py.
    """

    # Safely import web_server.py
    web_server = safe_import("web.web_server")

    if web_server is None:
        return
    
    if not hasattr(web_server, "run_web_server"):
        print("web_server.py is missing the function run_web_server(config).")
        return
     
    if args.host: 
        config["web_host"] = args.host

    if args.port is not None: 
        config["web_port"] = args.port


    # Run the web server.
    result = web_server.run_web_server(config)
    print_result(result)

def build_parser():
    """
    Build and return the command-line argument parser.
    """

    parser = argparse.ArgumentParser(
        description="Umbrella Network: a beginner-friendly networking portfolio toolkit."
    )

    # Create subcommands like diagnose, config, p2p-server, etc.
    subparsers = parser.add_subparsers(dest="command")

    # Diagnose command
    subparsers.add_parser(
        "diagnose",
        help="Run safe network diagnostics"
    )

    # config command
    config_parser = subparsers.add_parser(
        "config",
        help="Build a safe network configuration plan."
    )

    config_parser.add_argument(
        "--mode",
        choices=["dhcp", "static"],
        required=True,
        help="Choose dhcp for automatic settings or static for manual IP settings."
    )

    config_parser.add_argument("--ip", help="Static IP address, example: 192.168.1.50")
    config_parser.add_argument("--subnet", help= "Subnet mask, example: 255.255.255.0")
    config_parser.add_argument("--gateway", help="Gateway IP, example: 192.168.1.1")
    config_parser.add_argument("--dns", help="DNS server, example: 8.8.8.8")

    # p2p-server command
    p2p_server_parser = subparsers.add_parser(
        "p2p-server",
        help="Start the Umbrella Network rendezvous server."
    )

    p2p_server_parser.add_argument("--host", help="Host/IP to bind the server to.")
    p2p_server_parser.add_argument("--port", type=int, help="Port to run the server on.")

    # p2p-peer command
    p2p_peer_parser = subparsers.add_parser(
        "p2p-peer",
        help = "Start an Umbrella Network peer."
    )

    p2p_peer_parser.add_argument("--name", help="Peer name.")
    p2p_peer_parser.add_argument("--server-host", help="Rendezvous server host/IP.")
    p2p_peer_parser.add_argument("--server-port", type=int, help="Rendezvous server port.")
    p2p_peer_parser.add_argument("--message", help="Message to send from the peer")
    
    # switch-demo command
    subparsers.add_parser(
        "switch-demo",
        help="Run the learning switch demo."
    )

    # web command
    web_parser = subparsers.add_parser(
        "web",
        help= "Start the Umbrella Network web server."
    )

    # DNS tools command
    subparsers.add_parser(
        "dns",
        help="Run safe DNS lookup tools"
    )

    # Port tools command
    subparsers.add_parser(
        "ports",
        help="Run safe port checking tools"
    )

    web_parser.add_argument("--host", help="Host/IP to bind the web server to.")
    web_parser.add_argument("--port", type=int, help="Port to run the web server on.")

    return parser

def main():
    """
    Main program entry point.
    """

    # Always print the banner first.
    print_banner()

    # Load safe config settings.
    config = load_config()

    # Build the command-line parser.
    parser = build_parser()

    # Read command-line arguments.
    args = parser.parse_args()

    # If no command was given, print help and stop safely.
    if args.command is None:
        parser.print_help()
        return
    
    # Route each command to its handler
    if args.command == "diagnose":
        handle_diagnose(args, config)

    elif args.command == "config":
        handle_config(args, config)

    elif args.command == "dns":
        handle_dns(args, config)

    elif args.command == "ports":
        handle_ports(args, config)

    elif args.command == "p2p-server":
        handle_p2p_server(args, config)

    elif args.command == "p2p-peer":
        handle_p2p_peer(args, config)

    elif args.command == "switch-demo":
        handle_switch_demo(args, config)

    elif args.command == "web":
        handle_web(args, config)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()



