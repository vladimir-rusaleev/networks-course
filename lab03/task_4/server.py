import socket
from pathlib import Path
import sys
import threading

def handle_client(conn, semaphore):
    with semaphore:
        try:
            req = conn.recv(1024).decode()
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

            conn.sendall(res)
        except:
            pass
        finally:
            conn.close()

def main():
    port = int(sys.argv[1])
    concurrency_level = int(sys.argv[2])
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("localhost", port))
    server_socket.listen(5)
    semaphore = threading.Semaphore(concurrency_level)
    try:
        while True:
            con, _ = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(con, semaphore))
            thread.daemon = True
            thread.start()
    except:
        pass
    finally:
        server_socket.close()

if __name__ == '__main__':
    main()