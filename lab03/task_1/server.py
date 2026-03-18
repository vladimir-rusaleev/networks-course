import socket
from pathlib import Path
import sys

def main():
    port = int(sys.argv[1])
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("localhost", port))
    server_socket.listen(1)
    try:
        while True:
            con, _ = server_socket.accept()
            req = con.recv(1024).decode()

            try:
                path = req.split('\r\n')[0].split(' ')[1]
                file = Path('.' + path)
            except:
                file = None
            
            if file and file.is_file():
                with file.open('rb') as f:
                    content = f.read()
                res = b'HTTP/1.0 200 OK\r\n\r\n' + content
            else:
                res = b'HTTP/1.0 404 NOT FOUND\r\n\r\nNot found'

            con.sendall(res)
            con.close()
    except:
        pass
    finally:
        server_socket.close()

if __name__ == '__main__':
    main()