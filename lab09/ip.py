import psutil
import socket

def main():
    for interface, addresses in psutil.net_if_addrs().items():
        for addr in addresses:
            if addr.family == socket.AF_INET:
                print(f"interface: {interface}\nip: {addr.address}\nmask: {addr.netmask}")
                
if __name__ == "__main__":
    main()