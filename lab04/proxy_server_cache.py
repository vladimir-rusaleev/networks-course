from urllib.parse import urlparse
import socket
import threading
import requests
import urllib3
import os
import json
import hashlib
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PROXY_HOST = "localhost"
PROXY_PORT = 8888
LOG_FILE = "log.txt"
CACHE_DIR = "cache"
CACHE_FILE = os.path.join(CACHE_DIR, "cache.json")
BLACKLIST_FILE = "blacklist.txt"

os.makedirs(CACHE_DIR, exist_ok=True)

def load_blacklist():
    with open(BLACKLIST_FILE, 'r') as f:
        return set(line.strip() for line in f if line.strip())

def write_log(url, status_code, from_cache):
    source = "CACHE" if from_cache else "WEB"
    msg = f"url: {url}; status_code: {status_code}; source: {source}\n"
    print(msg)
    with open(LOG_FILE, 'a') as f:
        f.write(msg)
    
def url_to_filename(url):
    return hashlib.md5(url.encode()).hexdigest()

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

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

        assert target[0] == '/'
        url = target[1:]

        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        blacklist = load_blacklist()
        if hostname in blacklist:
            write_log(url, "blocked", False)
            msg = f"{hostname} is blocked."
            resp = f'HTTP/1.1 403 Forbidden\r\nContent-Length: {len(msg)}\r\nContent-Type: text/plain\r\n\r\n{msg}'.encode()
            client.sendall(resp)
            return

        if method.upper() == "GET":
            cache = load_cache()
            filename = url_to_filename(url)
            cache_path = os.path.join(CACHE_DIR, filename)
            headers = {}

            if os.path.exists(cache_path) and filename in cache:
                meta = cache[filename]
                if meta.get("Last-Modified"):
                    headers["If-Modified-Since"] = meta["Last-Modified"]
                if meta.get("ETag"):
                    headers["If-None-Match"] = meta["ETag"]
                if not headers:
                    with open(cache_path, 'rb') as f:
                        content = f.read()
                    write_log(url, 200, from_cache=True)
                    resp = f'HTTP/1.1 200 OK\r\nContent-Length: {len(content)}\r\n\r\n'.encode() + content
                    client.sendall(resp)
                    return
    
                try:
                    response = requests.get(url, headers=headers, verify=False, timeout=10)
                except requests.exceptions.ConnectionError:
                    client.send(b'HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n')
                    return

                if response.status_code == 304:
                    with open(cache_path, 'rb') as f:
                        content = f.read()
                    
                    write_log(url, 304, from_cache=True)
                    resp = f'HTTP/1.1 200 OK\r\nContent-Length: {len(content)}\r\n\r\n'.encode() + content
                    client.sendall(resp)
                    return
                else:
                    content = response.content
                    with open(cache_path, 'wb') as f:
                        f.write(content)
                    cache[filename] = {
                        "url": url,
                        "Last-Modified": response.headers.get("Last-Modified", ""),
                        "ETag": response.headers.get("ETag", ""),
                    }
                    save_cache(cache)
                    write_log(url, response.status_code, from_cache=False)
            else:
                try:
                    response = requests.get(url, verify=False, timeout=10)
                except requests.exceptions.ConnectionError:
                    client.send(b'HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n')
                    return

                content = response.content
                with open(cache_path, 'wb') as f:
                    f.write(content)
                cache[filename] = {
                    "url": url,
                    "Last-Modified": response.headers.get("Last-Modified", ""),
                    "ETag": response.headers.get("ETag", ""),
                }
                save_cache(cache)
                write_log(url, response.status_code, from_cache=False)

            if response.status_code == 404:
                client.send(b'HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n')
            else:
                resp = f'HTTP/1.1 200 OK\r\nContent-Length: {len(content)}\r\n\r\n'.encode() + content
                client.sendall(resp)
        
        elif method.upper() == "POST":
            body = data.split(b'\r\n\r\n', 1)[1].decode(errors='replace')
            try:
                response = requests.post(url, data=body, verify=False, timeout=10)
            except requests.exceptions.ConnectionError:
                client.send(b'HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n')
                return

            write_log(url, response.status_code)
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