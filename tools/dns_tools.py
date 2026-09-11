"""
Umbrella Network - dns_tools.py

This file provides safe DNS lookup tools for the Umbrella Network project.

IMPORTANT:
- This file does NOT change system network settings.
- It does NOT require administrator/root permissions.
- It only performs safe DNS lookups and prints beginner-friendly explanations.
- It uses only Python standard library modules.

main.py should be able to call:

    dns_tools.run_dns_tools(config)

"""

import ipaddress
import socket

def is_valid_hostname(hostname):
    """
    Return True if hostname looks like a valid hostname/domain name.

    This is a beginner-friendly validation function.
    It checks for simple problems like:
    - empty input
    - spaces
    - labels that are too long
    - invalid characters

    Examples of valid hostnames:
        example.com
        google.com
        subdomain.example.com

    This does not need to be perfect. DNS rules can get very detailed,
    but this is good enough for a beginner networking project.
    """

    if not isinstance(hostname, str):
        return False
    
    hostname = hostname.strip()

    if not hostname:
        return False
    
    if " " in hostname:
        return False
    
    # Hostnames should not be longer than 253 characters total.
    if len(hostname) > 253:
        return False
    
    # Remove one final dot if the user enters a fully qualified domain name.
    # Example: example.com.
    if hostname.endswith("."):
        hostname = hostname[:-1]

    labels = hostname.split(".")

    for label in labels:
        if not label:
            return False
        
        # Each part between dots should be 1 to 63 characters.
        if len(label) > 63:
            return False
        
        # Labels should not start or end with a hyphen.
        if label.startswith("-") or label.endswith("-"):
            return False
        
        # Allow letters, numbers, and hyphens.
        for character in label:
            if not (character.isalnum() or character == "-"):
                return False
            
    return True

def resolve_hostname(hostname):
    """
    Resolve a hostname into one or more IPv4 addresses.

    This function returns a dictionary instead of only printing output.
    That makes it easier for main.py or another file to reuse the result.

    The returned dictionary contains:

    {
        "hostname": ...,
        "valid_input": True or False,
        "resolved": True or False,
        "ip_addresses": [...],
        "error": None or error message,
        "summary": [...]
    }

    This function does not crash if DNS lookup fails.
    """

    result = {
        "hostname": hostname,
        "valid_input": False,
        "resolved": False,
        "ip_addresses": [],
        "error": None,
        "summary": [],
    }

    if not isinstance(hostname, str):
        result["error"] = "Hostname must be text."
        result["summary"].append("The hostname input was not valid text.")
        return result
    
    hostname = hostname.strip()
    result["hostname"] = hostname

    if not is_valid_hostname(hostname):
        result["error"] = "Invalid hostname."
        result["summary"].append("The hostname does not look valid. Try something like example.com.")
        return result
    
    result ["valid_input"] = True
    result ["summary"].append("The hostname input looks valid.")
    
    try:
        # getaddrinfo can return IPv4 and IPv6 results.
        # Because this beginner project asks for IPv4, we request AF_INET.
        lookup_results = socket.getaddrinfo(hostname, None, socket.AF_INET)

        unique_ips = []

        for item in lookup_results:
            # Each item contains several parts.
            # The last part includes the IP address and port.
            ip_address = item[4][0]

            if ip_address not in unique_ips:
                unique_ips.append(ip_address)

        result["ip_addresses"] = unique_ips

        if unique_ips:
            result["resolved"] = True
            result["summary"].append(
                "DNS successfully translated the hostname into IPv4 address information.")
        else:
            result["summary"].append("The lookup finished, but no IPv4 addresses were found.")

    except socket.gaierror as error:
        result["error"] = str(error)
        result["summary"].append("DNS lookup failed. The hostname may not exist or DNS may be unavailable.")

    except OSError as error:
        result["error"] = str(error)
        result["summary"].append("A system or network error happened during the DNS lookup.")

    return result

def reverse_dns_lookup(ip_address):
    """
    Perform a reverse DNS lookup on an IPv4 address.

    Reverse DNS tries to find a hostname for an IP address.

    Important beginner note:
    Not every IP address has a reverse DNS name. If this fails, it does not always mean the IP address is bad.

    The returned dictionary contains:
    {
        "ip_address": ...,
        "valid_input": True or False,
        "resolved": True or False,
        "hostnames": [...],
        "error": None or error message,
        "summary": [...],
    }
    """

    result = {
        "ip_address": ip_address,
        "valid_input": False,
        "resolved": False,
        "hostnames": [],
        "error": None,
        "summary": [],
    }

    if not isinstance(ip_address, str):
        result["error"] = "IP address must be text."
        result["summary"].append("The IP address input was not valid text.")
        return result
    
    ip_address = ip_address.strip()
    result["ip_address"] = ip_address

    try:
        # This validates that the input is a real IPv4 address.
        ipaddress.IPv4Address(ip_address)
        result["valid_input"] = True
        result["summary"].append("The IPv4 address input looks valid.")

    except (ipaddress.AddressValueError, ValueError):
        result["error"] = "Invalid IPv4 address."
        result["summary"].append("The IP address does not look valid. Try something like 8.8.8.8.")
        return result
    
    try:
        # gethostbyaddr returns:
        # hostname, alias list, IP address list
        hostname, aliases, _ = socket.gethostbyaddr(ip_address)

        hostnames = []

        if hostname:
            hostnames.append(hostname)

        for alias in aliases:
            if alias not in hostnames:
                hostnames.append(alias)
        
        result["hostnames"] = hostnames

        if hostnames:
            result["resolved"] = True
            result["summary"].append("Reverse DNS successfully found hostname information for this IP address.")
        else:
            result["summary"].append("The reverse lookup finished, but no hostnames were found.")
    
    except socket.herror as error:
        result["error"] = str(error)
        result["summary"].append("Reverse DNS lookup failed. Not every IP address has a reverse DNS name.")

    except OSError as error:
        result["error"] = str(error)
        result["summary"].append("A system or network error happened during the reverse DNS lookup.")

    return result

def print_dns_result(result):
    """
    Nicely print the result from resolve_hostname().

    This keeps the display logic separate from the lookup logic.
    That makes the program easier to understand and easier to reuse.
    """

    print("\n=========================")
    print("DNS Lookup Result")
    print("\n=========================")

    print(f"Hostname: {result.get('hostname')}")
    print(f"Valid input: {result.get('valid_input')}")
    print(f"Resolved: {result.get('resolved')}")

    ip_addresses = result.get("ip_addresses", [])

    if ip_addresses:
        print("\nIPv4 addresses found:")
        for ip_address in ip_addresses:
            print(f"    - {ip_address}")
    
    else:
        print("\nIPv4 addresses found: None")

    error = result.get("error")

    if error:
        print(f"\nError: {error}")

    summary = result.get("summary", [])

    if summary:
        print("\nSummary:")
        for message in summary:
            print(f"    - {message}")

    print()

def print_reverse_dns_result(result):
    """
    Nicely print the result from reverse_dns_lookup().

    Reverse DNS results are shown separately because they use an IP address
    as input and return hostname information.
    """

    print("\n=========================")
    print("Reverse DNS Lookup Result")
    print("\n=========================")

    print(f"IP address: {result.get('ip_address')}")
    print(f"Valid input: {result.get('valid_input')}")
    print(f"Resolved: {result.get('resolved')}")

    hostnames = result.get("hostnames", [])

    if hostnames:
        print("\nHostnames found:")
        for hostname in hostnames:
            print(f"    - {hostname}")
    
    else:
        print("\nHostnames found: None")

    error = result.get("error")

    if error:
        print(f"\nError: {error}")

    summary = result.get("summary", [])

    if summary:
        print("\nSummary:")
        for message in summary:
            print(f"    - {message}")

    print()

def run_dns_tools(config):
    """
    Main DNS tools menu.

    main.py can call this function with:

        dns_tools.run_dns_tools(config)

    The config dictionary may contain:

        {
            "default_dns_host": "example.com"
        }

    This menu keeps running until the user chooses Exit.
    """

    if config is None:
        config = {}

    print("\n=====================================")
    print("Umbrella Network - DNS Tools")
    print("=====================================")
    print("This tool performs safe DNS lookups.")
    print("It does not change network settings.")
    print("It does not require administrator/root permissions.")

    while True:
        try:
            print("\nChoose an option:")
            print("1. Resolve hostname to an IP address")
            print("2. Reverse lookup IP address to hostname")
            print("3. Use default DNS test host from config")
            print("4. Exit")

            choice = input("\nEnter your choice: ").strip()

            if choice == "1":
                hostname = input("Enter a hostname, like example.com: ").strip()
                result = resolve_hostname(hostname)
                print_dns_result(result)
                
            elif choice == "2": 
                ip_address = input("Enter an IPv4 address, like 8.8.8.8: ").strip()
                result = reverse_dns_lookup(ip_address)
                print_reverse_dns_result(result)

            elif choice == "3":
                default_host = config.get("default_dns_host", "example.com")
                print(f"\nUsing default DNS test host: {default_host}")
                result = resolve_hostname(default_host)
                print_dns_result(result)

            elif choice == "4":
                print("\nExiting DNS Tools.")
                break

            else:
                print("\nInvalid choice. Please enter 1, 2, 3, or 4.")
        
        except KeyboardInterrupt:
            print("\n\nDNS Tools stopped by user.")
            break

        except EOFError:
            print("\n\nNo more input available. Exiting DNS tools.")
            break

if __name__ == "__main__":
    run_dns_tools({})

            
    