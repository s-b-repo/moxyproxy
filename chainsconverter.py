import socket

def test_proxy(proxy):
    try:
        # Create a socket and attempt to connect through the proxy
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)  # Set a timeout for the connection attempt
        s.connect(proxy)
        s.close()
        return True
    except Exception as e:
        return False

def convert_to_proxychains(input_file, output_file):
    proxychains_config = ""
    with open(input_file, "r") as f:
        for socks_url in f:
            socks_url = socks_url.strip()
            if not socks_url.startswith("socks"):
                continue  # Ignore URLs that don't start with "socks"
            
            protocol, address_port = socks_url.split("://")
            address, port = address_port.split(":")
            proxy = (address, int(port))
            
            if protocol == "socks4":
                proxychains_config += f"socks4 {address} {port}\n"
            elif protocol == "socks5":
                proxychains_config += f"socks5 {address} {port}\n"
            
            if test_proxy(proxy):
                print(f"Proxy {socks_url} is working.")
            else:
                print(f"Proxy {socks_url} is not working.")
    
    with open(output_file, "w") as f:
        f.write(proxychains_config)

# Example usage
input_file = "socks_urls.txt"
output_file = "proxychains_config.txt"
convert_to_proxychains(input_file, output_file)
print(f"ProxyChains configuration saved to {output_file}.")
