from urllib.parse import urlparse
import socket
import threading
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PROXY_HOST = "localhost"
PROXY_PORT = 8888
LOG_FILE = "log.txt"

def write_log(url, status_code):
    with open(LOG_FILE, 'a') as f:
        f.write(f"url: {url}; status_code: {status_code}\n")

def handle_client(client):
    try:
        data = b''
        while b'\r\n\r\n' not in data:
            chunk = client.recv(4096)
            if not chunk:
                return
            data += chunk

        req = data.decode(errors='replace')
        method, target, _ = req.split('\r\n')[0].split()

        if method.upper() not in ("GET", "POST"):
            client.send(b'HTTP/1.1 405 Method Not Allowed\r\n\r\n')
            return
        print(method, target)
        assert target[0] == '/'
        url = target[1:]

        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        try:
            if method.upper() == "GET":
                response = requests.get(url, verify=False, timeout=10)
            elif method.upper() == "POST":
                body = data.split(b'\r\n\r\n', 1)[1].decode(errors='replace')
                response = requests.post(url, data=body, verify=False, timeout=10)
        except requests.exceptions.ConnectionError:
            client.send(b'HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n')
            return
        
        write_log(url, response.status_code)

        if response.status_code == 404:
            client.send(b'HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n')
        else:
            content = response.content
            resp = f'HTTP/1.1 200 OK\r\nContent-Length: {len(content)}\r\n\r\n'.encode() + content
            client.sendall(resp)

    except Exception as e:
        print(e)
        try:
            client.send(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
        except:
            pass
    finally:
        client.close()

def start_proxy():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((PROXY_HOST, PROXY_PORT))
    server.listen(5)
    print(f"Прокси запущен")
    while True:
        client, addr = server.accept()
        threading.Thread(target=handle_client, args=(client,), daemon=True).start()

if __name__ == "__main__":
    start_proxy()