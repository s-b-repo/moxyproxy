import socket
import random
import struct
import socks

def get_random_proxy(proxy_servers):
    random_index = random.randint(0, len(proxy_servers) - 1)
    return proxy_servers[random_index]

def handle_client(client_socket, proxy_servers):
    client_socket.recv(2)  # Version identifier/method selection message
    client_socket.sendall(struct.pack("BB", 0x05, 0x00))  # SOCKS5 version and No authentication required

    data = client_socket.recv(4)
    mode = data[1]
    if mode != 0x01:
        print("Only CONNECT mode is supported")
        client_socket.close()
        return

    addr_type = data[3]
    if addr_type == 0x01:  # IPv4
        address = socket.inet_ntoa(client_socket.recv(4))
    elif addr_type == 0x03:  # Domain name
        domain_length = client_socket.recv(1)[0]
        address = client_socket.recv(domain_length)
    else:
        print("Address type not supported")
        client_socket.close()
        return

    port = struct.unpack('!H', client_socket.recv(2))[0]

    random_proxy = get_random_proxy(proxy_servers)
    proxy_host, proxy_port = random_proxy.split(":")
    print(f"Forwarding request to: {random_proxy}")

    proxy_socket = socks.socksocket()
    proxy_socket.set_proxy(socks.HTTP, proxy_host, int(proxy_port))

    try:
        proxy_socket.connect((address, port))
        client_socket.sendall(struct.pack("BBBB", 0x05, 0x00, 0x00, addr_type))
        if addr_type == 0x01:
            client_socket.sendall(socket.inet_aton(address))
        elif addr_type == 0x03:
            client_socket.sendall(struct.pack("B", len(address)) + address)
        client_socket.sendall(struct.pack("!H", port))

        while True:
            data = client_socket.recv(4096)
            if len(data) > 0:
                proxy_socket.sendall(data)
                response = proxy_socket.recv(4096)
                client_socket.sendall(response)
            else:
                break
    except Exception as e:
        print(f"Error: {e}")

    proxy_socket.close()
    client_socket.close()

def start_server(proxy_servers, server_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', server_port))
    server_socket.listen(5)
    print(f"SOCKS5 proxy server is running on port {server_port}")

    while True:
        client_socket, _ = server_socket.accept()
        handle_client(client_socket, proxy_servers)

# Read proxy servers from a file
with open('proxy-servers.txt', 'r') as file:
    proxy_servers = file.read().splitlines()

# Define the server port
server_port = int(input("Enter the server port: "))

# Start the SOCKS5 proxy server
start_server(proxy_servers, server_port)
