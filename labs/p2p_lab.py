"""
Umbrella Network - p2p_lab.py

This file provides a safe local peer-to-peer socket lab for the
Umbrella Network.
"""

import socket
import threading

DEFAULT_P2P_HOST = "127.0.0.1"
DEFAULT_P2P_PORT = 5050
BUFFER_SIZE = 1024

def get_p2p_settings(config):
    """
    Read P2P settings from the project config.
    """

    if config is None:
        config = {}

    host = config.get("p2p_host", DEFAULT_P2P_HOST)
    port = config.get("p2p_port", DEFAULT_P2P_PORT)

    try:
        port = int(port)
    
    except (TypeError, ValueError):
        print("[!] Invalid p2p_port in config. Falling back to 5050.")
        port = DEFAULT_P2P_PORT
    
    return host, port

def handle_client(client_socket, client_address):
    """
    Handle one connected client.
    """

    try:
        print(f"\n[+] Connected peer: {client_address[0]}:{client_address[1]}")

        data = client_socket.recv(BUFFER_SIZE)

        if not data:
            print("[!] Peer connected but did not send any data.")
            return
        
        message = data.decode("utf-8", errors="replace")
        print(f"[Peer Message] {message}")

        response = (
            "Umbrella Network received your message. "
            "Local P2P lab communication successful."
        )

        client_socket.sendall(response.encode("utf-8"))

    except UnicodeDecodeError:
        print("[!] Could not decode the peer message as text.")

    except ConnectionResetError:
        print("[!] The peer disconnected unexpectedly.")

    except socket.error as error:
        print(f"[!] Socket error while handling peer: {error}")

    finally:
        # Always closes the client socket when finished.
        client_socket.close()
        print(f"[-] Closed connection with {client_address[0]}:{client_address[1]}")

def run_p2p_server(config):
    """
    Start the local P2P TCP server.
    Listens for peer/client connections and responds to messages.
    """

    host, port = get_p2p_settings(config)

    print("=" * 60)
    print("Umbrella Network - Local P2P Server")
    print("=" * 60)
    print(f"Host: {host}")
    print(f"Port: {port}")
    print()
    print("Beginner note:")
    print("127.0.0.1 means localhost, this computer only.")
    print("That keeps this lab safe and local by default")
    print()

    if host == "0.0.0.0":
        print("[!] Notice: You configured the server to bind to 0.0.0.0")
        print("[!] That can listen on all network interfaces.")
        print("[!] Only use that intentionally in a trusted lab network.")
        print()

    server_socket = None

    try:

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server_socket.bind((host, port))

        server_socket.listen(5)

        print("[+] Server started successfully.")
        print("[+] Waiting for peers to connect...")
        print()
        print("Open another terminal and run:")
        print("     python3 main.py p2p-peer")
        print()
        print("Press Ctrl+C to stop the server.")
        print()

        while True:
            try:

                client_socket, client_address = server_socket.accept()

                client_thread = threading.Thread(
                    target=handle_client,
                    args=(client_socket, client_address),
                    daemon=True
                )

                client_thread.start()
            
            except socket.error as error:
                print(f"[!] Socket error while accepting a peer: {error}")
    
    except KeyboardInterrupt:
        print("\n[!] Ctrl+C detected.")
        print("[+] Shutting down the P2P server.")

    except PermissionError:
        print("[!] Permission error.")
        print("[!] Try using a port above 1024, such as 5050.")
        print("[!] This project should not require administrator/root permissions.")

    except OSError as error:
        print(f"[!] Could not start the server: {error}")
        print("[!] Common causes:")
        print("     - The port is already in use.")
        print("     - The host address is invalid.")
        print("     - Another copy of the server is already running.")

    except socket.error as error:
        print(f"[!] Socket error while starting server: {error}")

    finally:
        if server_socket is not None:
            server_socket.close()
            print("[+] Server socket closed.")

def run_p2p_peer(config):
    """
    Start the local P2P peer/client.
    
    The peer connects to the local P2P server, sends one message,
    receives one response, and closes cleanly.
    """

    host, port = get_p2p_settings(config)

    print("=" * 60)
    print("Umbrella Network - Local P2P Peer")
    print("=" * 60)
    print(f"Connecting to server at {host}:{port}")
    print()

    peer_socket = None

    try:
        message = input("Type a message to send to the P2P server:  ").strip()

        if not message:
            print("[!] No message typed. Nothing was sent.")
            return
        
        # socket.AF_INET means IPv4.
        # socket.SOCK_STREAM means TCP.
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print("[+] Attempting to connect...")

        # connect() opens a TCP communication to the server.
        peer_socket.connect((host, port))

        print("[+] Connected to the P2P server.")

        # sends the user's full message to the server.
        peer_socket.sendall(message.encode("utf-8"))

        # recv() waits for the server's response.
        response = peer_socket.recv(BUFFER_SIZE)

        if response:
            print()
            print("[Server Response]")
            print(response.decode("utf-8", errors="replace"))
        else:
            print("[!] The server closed the connection without a response.")
    
    except ConnectionRefusedError:
        print("[!] Connection refused.")
        print("[!] The P2P server is probably not running yet.")
        print()
        print("Start it first in another terminal:")
        print("    python3 main.py p2p-server")

    except socket.gaierror:
        print("[!] Invalid host address.")
        print("[!] Check your p2p_host value in config.json.")

    except TimeoutError:
        print("[!] Connection timed out.")
        print("[!] Check that the server is running and the host/port are correct.")

    except KeyboardInterrupt:
        print("\n[!] Ctrl+C detected.")
        print("[+] Peer stopped before finishing.")

    except socket.error as error:
        print(f"[!] Socket error while running peer: {error}")

    finally:
        if peer_socket is not None:
            peer_socket.close()
            print("[+] Peer socket closed.")


    

