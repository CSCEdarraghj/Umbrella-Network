"""
Umbrella Network - port_tools.py

This file provides safe port checking tools for the Umbrella Network project.

Important:
- This file does NOT change system network settings.
- It does NOT require administrator/root permissions.
- It only performs small, safe connection checks.
- It does NOT scan large port ranges.
- It reminds users to only test hosts they own or have permission to test.
- It uses only Python standard library modules.

main.py should be able to call:

    port_tools.run_port_tools(config)

"""

import socket

def is_valid_port(port):
    """
    Return True if port is a valid TCP port number.

    A valid TCP port:
    - Can be an integer or a string containing a number
    - Must be from 1 to 65535
    - Cannot be empty
    - Cannot be negative
    - Cannot be 0
    - Cannot be above 65535
    - Cannot be text like "about"

    Examples:
        22  -> True
        "80"  -> True
        0  -> False
        -1  -> False
        "abc"  -> False
        70000  -> False
    """

    normalized_port = normalize_port(port)
    return normalized_port is not None

def normalize_port(port):
    """
    Convert a valid port into an integer.

    If the port is valid, return it as an integer.
    If the port is invalid, return None.

    This helps the rest of the program safely work with ports.
    """

    if isinstance(port, str):
        port = port.strip()

        if port == "":
            return None
        
        if not port.isdigit():
            return None
        
    try:
        port_number = int(port)
    except (ValueError, TypeError):
        return None
    
    if 1 <= port_number <= 65535:
        return port_number
    
    return None

def get_common_ports():
    """
    Return a small dictionary of beginner-friendly ports.

    This project intentionally checks only a small safe list.
    It does NOT scan all possible ports.
    """

    return{
        22: "SSH",
        53: "DNS",
        80: "HTTP",
        443: "HTTPS",
    }

def normalize_timeout(timeout):
    """
    Safely convert timeout into a number.

    If the timeout is invalid, use 2 seconds as a safe default.
    A timeout controls how long Python waits before giving up on a connection.
    """

    try:
        timeout_number = float(timeout)
    except (ValueError, TypeError):
        return 2
    
    if timeout_number <= 0:
        return 2
    
    return timeout_number

def check_port(hostname, port, timeout=2):
    """
    Safely check whether one TCP port is reachable on a hostname/IP address.

    This function uses socket.create_connection(), which attempts to open a TCP connection to the given host and port.

    Important:
    - This does NOT prove a service is fully working
    - This does NOT prove a host is down if the port is unreachable.
    - Firewalls, security settings, closed services, or network rules can block ports.
    - Only test hosts you own or have permission to test.
    """
    
    common_ports = get_common_ports()
    normalized_port = normalize_port(port)
    timeout = normalize_timeout(timeout)

    result = {
        "hostname": hostname,
        "port": normalized_port if normalized_port is not None else port,
        "service": "Unknown",
        "valid_port": normalized_port is not None,
        "reachable": False,
        "error": None,
        "summary": []
    }

    if normalized_port is not None:
        result["service"] = common_ports.get(normalized_port, "Unknown")

    if not isinstance(hostname, str) or hostname.strip() == "":
        result["error"] = "Hostname/IP address cannot be empty."
        result["summary"].append("No connection was attempted because the hostname/IP address was empty.")
        result["summary"].append("Enter a hostname like example.com or an IP address like 192.168.1.1.")
        return result
    
    hostname = hostname.strip()
    result["hostname"] = hostname

    if normalized_port is None:
        result["error"] = "Invalid port number."
        result["summary"].append("No connection was attempted because the port was invalid")
        result["summary"].append("A valid TCP port must be a number from 1 to 65535.")
        return result
    
    try:
        with socket.create_connection((hostname, normalized_port), timeout=timeout):
            result["reachable"] = True
            result["summary"].append(f"Port {normalized_port} on {hostname} accepted a TCP connection.")
            result["summary"].append("This usually means something is listening on that port.")
    
    except socket.timeout:
        result["error"] = "Connection timed out."
        result["summary"].append(f"Port {normalized_port} on {hostname} did not respond before the timeout.")
        result["summary"].append("This does not always mean the host is down. A firewall or network rule may be blocking the connection.")

    except ConnectionRefusedError:
        result["error"] = "Connection refused."
        result["summary"].append(f"The host was reached, but port {normalized_port} refused the connection.")
        result["summary"].append("This usually means the host is online, but nothing is accepting the connections on that port.")

    except socket.gaierror:
        result["error"] = "Hostname could not be resolved."
        result["summary"].append(f"Python could not resolve the hostname/IP address: {hostname}.")
        result["summary"].append("Check the spelling of the hostname or try using an IP address.")

    except OSError as error:
        result["error"] = str(error)
        result["summary"].append(f"Python could not connect to port {normalized_port} on {hostname}")
        result["summary"].append("Unreachable does not always mean the host is down. Firewalls, closed ports, or network rules may block the connection.")

    return result

def check_common_ports(hostname, timeout=2):
    """
    Check only the small common port list from get_common_ports()

    This function intentionally does NOT scan:
    - All 65535 ports
    - Large port ranges
    - Random ports

    It only checks:
    - 22 SSH
    - 53 DNS
    - 80 HTTP
    - 443 HTTPS
    """

    results = []

    for port in get_common_ports():
        result = check_port(hostname, port, timeout)
        results.append(result)

    return results

def print_port_result(result):
    """
    Nicely print one result from check_port()

    This keeps the output clean and easy for beginners to read.
    """

    print()
    print("=" * 50)
    print("Port Check Result")
    print("=" * 50)

    print(f"Hostname/IP:      {result.get('hostname')}")
    print(f"Port:             {result.get('port')}")
    print(f"Service:          {result.get('service')}")
    print(f"Valid Port input: {result.get('valid_port')}")
    print(f"Reachable:        {result.get('reachable')}")

    error = result.get("error")
    if error:
        print(f"Error:      {error}")

    print()
    print("Summary:")

    summary_items = result.get("summary", [])

    if summary_items:
        for item in summary_items:
            print(f"- {item}")
    
    else:
        print("- No summary was provided.")

    print("=" * 50)

def print_port_results(results):
    """
    Nicely print multiple port check results.

    This calls print_port_result() for each result.
    """

    if not results:
        print()
        print("No port check results to display.")
        return
    
    for result in results:
        print_port_result(result)

def get_config_ports(config):
    """
    Safely get default ports from the config dictionary.

    If config does not contain a valid default_ports list,
    use the safe common ports instead.
    """

    default_ports = config.get("default_ports", list(get_common_ports().keys()))

    if not isinstance(default_ports, list):
        return list(get_common_ports().keys())
    
    safe_ports = []

    for port in default_ports:
        normalized_port = normalize_port(port)

        if normalized_port is not None:
            safe_ports.append(normalized_port)
    
    if not safe_ports:
        return list(get_common_ports().keys())
    
    return safe_ports

def run_port_tools(config):
    """
    Main menu for the Umbrella Network port tools.
    
    main.py can call:

        port_tools.run_port_tools(config)

    This menu lets the user:
    1. Check one port on a host
    2. Check common ports on a host
    3. Use default host and default ports from config
    4. Exit
    """

    if config is None:
        config = {}

    print()
    print("=" * 60)
    print("Umbrella Network - Safe Port Tools")
    print("=" * 60)
    print("This tool performs safe, limited TCP port checks.")
    print("It does NOT change network settings.")
    print("It does NOT require admin/root permissions.")
    print("It does NOT scan large port ranges.")
    print()
    print("Only test hosts you own or have permission to test.")
    print("=" * 60)

    while True:
        try:
            print()
            print("Menu:")
            print("1. Check one port on a host")
            print("2. Check common ports on a host")
            print("3. Use default host and common/default ports from config")
            print("4. Exit")
            print()

            choice = input("Choose an option: ").strip()

            if choice == "1":
                hostname = input("Enter hostname or IP address: ").strip()
                port = input("Enter one TCP port number: ").strip()
                timeout = config.get("port_timeout", 2)

                result = check_port(hostname, port, timeout)
                print_port_result(result)

            elif choice == "2":
                hostname = input("Enter hostname or IP address: ").strip()
                timeout = config.get("port_timeout", 2)

                print()
                print("Checking only safe common ports: 22, 53, 80, 443")
                results = check_common_ports(hostname, timeout)
                print_port_results(results)

            elif choice == "3":
                hostname = config.get("default_port_host", "example.com")
                timeout = config.get("port_timeout", 2)
                ports = get_config_ports(config)

                print()
                print(f"Using default host: {hostname}")
                print(f"Using timeout: {normalize_timeout(timeout)} seconds")
                print(f"Using safe configured ports: {ports}")
                print()
                print("Reminder: only test hosts you own or have permission to test.")

                results = []

                for port in ports:
                    result = check_port(hostname, port, timeout)
                    results.append(result)

                print_port_results(results)

            elif choice == "4":
                print()
                print("Exiting Umbrella Network port tools.")
                break

            else:
                print()
                print("Invalid menu option.")
                print("Please choose 1, 2, 3, or 4.")
        
        except KeyboardInterrupt:
            print()
            print()
            print("Port tools stopped by user.")
            break

        except EOFError:
            print()
            print()
            print("Input ended. Exiting port tools safely.")
            break

        except Exception as error:
            print()
            print("An unexpected error occurred, but the program did not crash.")
            print(f"Error: {error}")
            print("Returning to the menu safely.")

if __name__ == "__main__":
    run_port_tools({})

