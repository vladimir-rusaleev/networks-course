import sys
import socket

def main():
    host = sys.argv[1]
    port = int(sys.argv[2])
    filename = sys.argv[3]

    if not filename.startswith('/'):
        filename = '/' + filename

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))

        req = f"GET {filename} HTTP/1.0\r\nHost: {host}\r\n\r\n"
        client_socket.sendall(req.encode())
        
        response = b''
        while True:
            part = client_socket.recv(4096)
            if not part:
                break
            response += part
            
        print(response.decode())
        
    except:
        pass
    finally:
        client_socket.close()

if __name__ == '__main__':
    main()