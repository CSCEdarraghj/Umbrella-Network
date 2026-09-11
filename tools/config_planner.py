"""
Umbrella Network - config_planner.py

This file helps users safely plan network/IP settings for the Umbrella Network project.

IMPORTANT:
- This file does NOT change system network settings.
- It does NOT require administrator/root permissions.
- It only validates information, explains it, and prints a safe plan.
- It uses only Python standard library modules.

main.py should be able to call:

     config_planner.run_config_planner(config)

"""

import ipaddress

def is_valid_ip(ip_address):
    """
    Return True if ip_address is a valid IPv4 address.
    
    Example valid IPv4 address:
    192.168.1.25
   
    Example invalid IPv4 address:
    999.999.999.999
    """

    try:
        ipaddress.IPv4Address(ip_address)
        return True
    except (ipaddress.AddressValueError, ValueError, TypeError):
        return False

def is_valid_subnet_mask(mask):
    """
    Return True if mask is a valid IPv4 subnet mask.

    A subnet mask must have all 1 bits first, followed by all 0 bits.

    Valid examples:
        255.255.255.0
        255.255.0.0
        255.0.0.0
        255.255.255.128
        255.255.255.192
        255.255.255.224
        255.255.255.240
        255.255.255.248
        255.255.255.252

    Invalid examples:
        255.0.255.0
        255.255.300.0
        hello
    """
    try:
        # ipaddress can validate subnet masks when used this way.
        ipaddress.IPv4Network(f"0.0.0.0/{mask}", strict=False)
        return True
    except (ipaddress.NetmaskValueError, ValueError, TypeError):
        return False

def is_valid_gateway(gateway):
    """
    Return True if gateway is a valid IPv4 address.

    A gateway is usually the router IP address on the local network.
    Example:
        
        192.168.1.1
    
    """
    
    return is_valid_ip(gateway)

def is_valid_dns(dns_server):
    """
    Return True if dns_server is a valid IPv4 address.

    A DNS server turns website names like example.com into IP addresses

    Example:

        8.8.8.8
    
    """
    
    return is_valid_ip(dns_server)

def subnet_mask_to_cidr(mask):
    """
    Convert a valid subnet mask to CIDR notation.

    Example:

        255.255.255.0 -> 24
    
    Return None if the mask is invalid.
    """
    if not is_valid_subnet_mask(mask):
        return None
    
    try:
        network = ipaddress.IPv4Network(f"0.0.0.0/{mask}", strict=False)
        return network.prefixlen
    except (ipaddress.NetmaskValueError, ValueError, TypeError):
        return None
    
def cidr_to_subnet_mask(cidr):
    """
    Convert CIDR notation to a subnet mask.

    Example:

        24 -> 255.255.255.0

    Accept CIDR values from 0 to 32.
    Return None if invalid.
    """

    try:
        cidr_number = int(cidr)

        if cidr_number < 0 or cidr_number > 32:
            return None
        
        network = ipaddress.IPv4Network(f"0.0.0.0/{cidr_number}", strict=False)
        return str(network.netmask)
    
    except (ValueError, TypeError):
        return None
    
def are_in_same_subnet(ip_address, gateway, subnet_mask):
    """
    Return True if the IP address and gateway are in the same subnet.

    Return False if they are valid but not in the same subnet.

    Return None if any input is invalid.
    """
    
    if not is_valid_ip(ip_address):
        return None
    
    if not is_valid_gateway(gateway):
        return None
    
    if not is_valid_subnet_mask(subnet_mask):
        return None
    
    try:
        ip_interface = ipaddress.IPv4Interface(f"{ip_address}/{subnet_mask}")
        gateway_interface = ipaddress.IPv4Interface(f"{gateway}/{subnet_mask}")

        return ip_interface.network == gateway_interface.network
    
    except (ipaddress.AddressValueError, ipaddress.NetmaskValueError, ValueError):
        return None
    
def explain_private_or_public_ip(ip_address):
    """
    Return a beginner-friendly explanation of whether an IP is private or public.

    Private IP addresses are usually inside homes, schools, and labs. 
    Public IP addresses are used on the internet.
    """
    
    if not is_valid_ip(ip_address):
        return "Private/public explanation unavailable because the IP address is invalid."
    
    try:
        ip_obj = ipaddress.IPv4Address(ip_address)

        if ip_obj.is_private:
            return (
                "This is a private IP address. That usually means it is meant for a local network, " 
                "like a home, school, office, or lab."
            )
        
        if ip_obj.is_loopback:
            return (
                "This is a loopback IP address. It points back to this same " 
                "computer and is usually used for local testing."
            )
        
        if ip_obj.is_link_local:
            return(
                "This is a link-local IP address. This can appear when a device "
                "does not receive a normal address from DHCP."
            )
        
        return(
            "This appears to be a public IP address. Be careful: public IP "
            "settings are usually assigned by an ISP or network administrator."
        )
    
    except(ipaddress.AddressValueError, ValueError, TypeError):
        return "Private/public IP explanation unavailable because the IP address is invalid."
    
def build_config_plan(ip_address, subnet_mask, gateway, dns_servers):
    """
    Validate network settings and build a safe configuration plan.

    This function does NOT change system settings.

    Parameters:
        ip_address:
            Planned device IP address as a string

        subnet_mask:
            Planned subnet mask as a string.

        gateway:
            Planned gateway/router IP address as a string.

        dns_servers:
            List of DNS server IP addresses as a string
    
    Return:
        A dictionary containing the planned settings, validity status,
        warnings, and beginner-friendly summary notes.
    """

    warnings = []
    summary = []

    # Make sure bad dns_servers input does not crash the program.
    if dns_servers is None:
        dns_servers = []
    elif not isinstance(dns_servers, list):
        dns_servers = [dns_servers]

    # Strip accidental spaces from user input.
    ip_address = str(ip_address).strip()
    subnet_mask = str(subnet_mask).strip()
    gateway = str(gateway).strip()

    cleaned_dns_servers = []
    for dns_server in dns_servers:
        dns_server = str(dns_server).strip()

        if dns_server:
            cleaned_dns_servers.append(dns_server)

    cidr = subnet_mask_to_cidr(subnet_mask)

    if is_valid_ip(ip_address):
        summary.append(f"IP address {ip_address} is a valid IPv4 address.")
        summary.append(explain_private_or_public_ip(ip_address))
    else:
        warnings.append(f"Invalid IP address: {ip_address}")

    if is_valid_subnet_mask(subnet_mask):
         summary.append(f"Subnet mask {subnet_mask} is valid.")
         summary.append(f"The subnet mask {subnet_mask} is CIDR /{cidr}.")
    else:
        warnings.append(f"Invalid subnet mask: {subnet_mask}")

    if is_valid_gateway(gateway): 
        summary.append(f"Gateway {gateway} is a valid IPv4 address.")
    else:
        warnings.append(f"Invalid gateway: {gateway}")

    if cleaned_dns_servers:
        for dns_server in cleaned_dns_servers:
            if is_valid_dns(dns_server):
                summary.append(f"DNS server {dns_server} is a valid IPv4 address.")
            else:
                warnings.append(f"Invalid DNS server: {dns_server}")
    else:
        warnings.append("No DNS servers were provided.")

    same_subnet = are_in_same_subnet(ip_address, gateway, subnet_mask)

    if same_subnet is True:
        summary.append("The IP address and gateway are in the same subnet.")
    elif same_subnet is False:
        warnings.append(
            "The gateway is not in the same subnet as the IP address. "
            "Usually, your gateway should be on the same local network."
        )
    else:
        warnings.append(
            "Could not check whether the IP address and gateway are in the "
            "same subnet because one or more values are invalid."
        )

    valid = len(warnings) == 0

    return {
        "ip_address": ip_address,
        "subnet_mask": subnet_mask,
        "cidr": cidr,
        "gateway": gateway,
        "dns_servers": cleaned_dns_servers,
        "valid": valid,
        "warnings": warnings,
        "summary": summary,
    }

def print_config_plan(plan):
    """
    Nicely print the safe configuration plan.

    This function only prints information. It does not change settings.
    """

    print()
    print("=" * 60)
    print("Umbrella Network - Safe Configuration Plan")
    print("=" * 60)

    if not isinstance(plan, dict):
        print("Error: plan is not a valid dictionary.")
        return
    
    print()
    print("Planned Settings")
    print("-" * 60)
    print(f"IP Address:     {plan.get('ip_address')}")
    print(f"Subnet Mask:     {plan.get('subnet_mask')}")

    cidr = plan.get("cidr")

    if cidr is not None:
        print(f"CIDR:       /{cidr}")
    else:
        print("CIDR:        unavailable")

    print(f"Gateway:        {plan.get('gateway')}")

    dns_servers = plan.get("dns_servers", [])

    if dns_servers:
        print(f"DNS Servers: {', '.join(dns_servers)}")
    else:
        print("DNS Servers: none provided")

    print()
    print("Plan Status")
    print("-" * 60)

    if plan.get("valid"):
        print("VALID: This plan passed the safety checks.")
    else:
        print("NOT VALID YET: Review the warnings below.")

    warnings = plan.get("warnings", [])

    if warnings:
        print()
        print("Warnings")
        print("-" * 60)

        for number, warning in enumerate(warnings, start=1):
            print(f"{number}. {warning}")

    summary = plan.get("summary", [])

    if summary:
        print()
        print("Beginner-Friendly Explanation")
        print("-" * 60)

        for item in summary:
            print(f"- {item}")

    print()
    print("Safety Reminder")
    print("-" * 60)
    print(
        "This tool only creates a plan. It does not apply settings, change your "
        "network adapter, edit system files, or require administrator access."
    )
    print("=" * 60)
    print()

def build_dhcp_plan():
    """
    Build a safe DHCP planning message.

    This does NOT enable DHCP or change any network settings.
    It only explains what a DHCP plan means for beginners.
    """

    return (
        "Umbrella Network - DHCP plan\n"
        "Mode: DHCP / automatic addressing\n\n"
        "Safe plan:\n"
        "- Let the router or DHCP server assign the IP address.\n"
        "- Let the router or DHCP server assign the subnet mask.\n"
        "- Let the router or DHCP server assign the gateway.\n"
        "- Let the router or DHCP server assign DNS servers, unless a trusted administrator says otherwise.\n\n"
        "Safety reminder: this program only prints a plan. It does not change your computer settings."
    )

def build_static_ip_plan(ip, subnet, gateway, dns):
    """
    Build a safe static IP planning report for main.py.

    This does NOT change system network settings.
    It only validates and explains the plan.
    """

    plan = build_config_plan (
        ip_address=ip,
        subnet_mask=subnet,
        gateway=gateway,
        dns_servers=[dns],
    )

    lines = [
        "Umbrella Network - Static IP Plan",
        "Mode: static / manual addressing",
        "",
        f"IP Address:  {plan.get('ip_address')}",
        f"Subnet Mask: {plan.get('subnet_mask')}",
        f"CIDR:        /{plan.get('cidr')}" if plan.get("cidr") is not None else "CIDR:       unavailable",
        f"Gateway:     {plan.get('gateway')}",
        f"DNS Servers: {', '.join(plan.get('dns_servers', [])) or 'none provided'}",
        "",
        "Status: VALID" if plan.get("valid") else "Status: NOT VALID YET",
    ]

    warnings = plan.get("warnings", [])
    if warnings:
        lines.append("")
        lines.append("Warnings:")
        for warning in warnings:
            lines.append(f"- {warning}")
    
    summary = plan.get("summary", [])
    if summary:
        lines.append("")
        lines.append("Explanation:")
        for item in summary:
            lines.append(f"- {item}")

    lines.append("")
    lines.append("Safety reminder: this program only prints a plan. It does not change your computer settings.")

    return "\n".join(lines)

def run_config_planner(config):
    """
    Main function called by main.py

    This function asks the user for planned network settings, builds a safe
    configuration plan, and prints the result.

    It handles Ctrl+C and unexpected input endings gracefully.
    """
    
    if config is None:
        config = {}

    print ()
    print("=" * 60)
    print ("Umbrella Network - Config Planner")
    print("=" * 60)
    print(
        "This tool helps you plan IP settings safely. It does NOT change your "
        "computer's network settings."
    )
    print(
        "Use it for learning, documentation, troubleshooting practice, and "
        "portfolio demonstrations."
    )
    print()

    default_dns_host = config.get("default_dns_host")

    if default_dns_host:
        print(f"Project note: default_dns_host is set to {default_dns_host!r}.")
        print("That is a hostname for DNS testing, not a DNS server IP address.")
        print()

    try:
        ip_address = input("Enter planned IP address: ").strip()
        subnet_mask = input("Enter planned subnet mask: ").strip()
        gateway = input("Enter planned gateway/router IP: ").strip()
        primary_dns = input("Enter primary DNS server IP: ").strip()
        secondary_dns = input("Enter secondary DNS server IP, optional: ").strip()

        dns_servers = []

        if primary_dns:
            dns_servers.append(primary_dns)

        if secondary_dns:
            dns_servers.append(secondary_dns)

        plan = build_config_plan(
            ip_address=ip_address,
            subnet_mask=subnet_mask,
            gateway=gateway,
            dns_servers=dns_servers
        )

        print_config_plan(plan)

    except KeyboardInterrupt:
        print()
        print()
        print("Config planner canceled by user. No settings were changed.")
        print()

    except EOFError:
        print()
        print()
        print("Input ended unexpectedly. No settings were changed.")
        print()
    
if __name__ == "__main__":
    run_config_planner({})


    