"""
Umbrella Network - net_diag.py

This file contains safe network diagnostic functions for the 
Umbrella Network Project

Important:
- This file does NOT change system network settings.
- It only reads information and runs safe tests.
- It uses only Python standard library modules.
- main.py should be able to call net_diag.run_diagnostics(config)
"""

import platform
import socket
import subprocess

def get_hostname():
    """
    Return the computer's hostname as a string.

    A hostname is the name your computer uses on a network.
    """
    try:
        return socket.gethostname()
    except OSError as error:
        return f"Error getting hostname: {error}"
    
def get_local_ip():
    """
    Return the most likely local LAN IP address.

    This uses the safe UDP socket trick:
    - Create a UDP socket.
    - Connect it to an outside address.
    - No data is actually sent.
    - Python lets us see which local IP would be used.

    If that fails, fall back to socket.gethostbyname()
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            # This does not actually send data.
            # It only asks the operating system what route it would use.
            sock.connect(("8.8.8.8", 80))

            local_ip = sock.getsockname()[0]
            return local_ip
        
    except OSError:
        # Fall back to a simpler hostname lookup if the UDP trick fails.
        try:
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except OSError as error:
            return f"Error getting local IP: {error}"
        
def get_interfaces():
    """
    Return a list of detected local IP addresses.
    
    This function tries to find IP addresses assigned to the computer.
    Uses socket.getaddrinfo(), which asks the operating system
    for network address information linked to the hostname.

    It filters duplicates so the same IP is not listed multiple times.
    """
    addresses = []

    try:
        hostname = socket.gethostname()

        # Ask the operating system for address information.
        # This may return the IPv4 and IPv6 addresses.
        info_list = socket.getaddrinfo(hostname, None)

        for info in info_list:
            address = info[4][0]

            # Avoid duplicate addresses
            if address not in addresses:
                addresses.append(address)

        if addresses:
            return addresses
        
        return["No local interfaces found."]

    except OSError as error:
        return[f"Error getting interfaces: {error}"]
    
def get_system_info():
    """
    Return basic operating system information
    """
    return{
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }

def ping_host(host):
    """
    Safely ping a host and return the result as a string.

    The ping test checks whether another computer or server can be reached across the network.

    This function does NOT change network settings.
    It only runs the system ping command.

    Windows uses:
        ping -n 4 host

    macOS/Linux uses:
        ping -c 4 host
    """
    try:
        system_name = platform.system().lower()

        if system_name == "windows":
            command = ["ping", "-n", "4", host]
        else:
            command = ["ping", "-c", "4", host]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            return result.stdout
        else:
            return result.stderr or result.stdout or "Ping failed with no output."
    
    except subprocess.TimeoutExpired:
        return f"Ping test to {host} timed out."
    except OSError as error:
        return f"Error running ping test: {error}"
    
def dns_lookup(hostname):
    """
    Perform a DNS lookup for a hostname.

    DNS turns a human-readable name like example.com into an IP address.
    
    This function does NOT change DNS settings.
    It only asks the system to resolve the hostname.
    """

    try:
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except socket.gaierror as error:
        return f"DNS lookup for {hostname}: {error}"
    except OSError as error:
        return f"Error during DNS lookup: {error}"
    
def check_port(host, port):
    """
    Check whether a TCP port is open on a host

    A port check tests whether service may be reachable.
    For example:
    - Port 80 is commonly used for HTTP.
    - Port 443 is commonly used for HTTPS.

    This function does NOT scan a network range.
    It only checks one host and one port provided by the config.
    """
    try:
        port = int(port)

        with socket.create_connection((host, port), timeout=5):
            return f"Port {port} on {host} is open."
        
    except ValueError:
        return f"Invalid port number: {port}"
    except socket.timeout:
        return f"Connection to {host}: {port} timed out."
    except OSError as error:
        return f"Port {port} on {host} appears closed or unreachable."
    
def run_diagnostics(config):
    """
    Run safe network diagnostics using values from the config dictionary.

    main.py should call this function like this:

        net_diag.run_diagnostics(config)

    The config dictionary may contain:

        {
            "default_ping_host": "8.8.8.8",
            "default_dns_host": "example.com",
            "default_port_host": "google.com",
            "default_port": "80",
        }

    This function returns a dictionary of results.
    It does not generate a written report file.
    """
    ping_host_value = config.get("default_ping_host", "8.8.8.8")
    dns_host_value = config.get("default_dns_host", "example.com")
    port_host_value = config.get("default_port_host", "google.com")
    port_value = config.get("default_port", "80")
    
    results = {
        "hostname": get_hostname(),
        "local_ip": get_local_ip(),
        "interfaces": get_interfaces(),
        "system_info": get_system_info(),
        "ping_test": ping_host(ping_host_value),
        "dns_lookup": dns_lookup(dns_host_value),
        "port_check": check_port(port_host_value, port_value)
    }

    return results

