import socket
import random

def main():
    HOST = '127.0.0.1'
    PORT = 8888

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((HOST, PORT))
    print(f"cервер запущен на {HOST}:{PORT}")

    while True:
        data, client_addr = server_socket.recvfrom(1024)
        msg = data.decode()

        if random.random() < 0.2:
            print(f"потерян пакет {msg}")
            continue

        resp = msg.upper()
        server_socket.sendto(resp.encode(), client_addr)
        print(f"отправлен ответ {resp}")

if __name__ == "__main__":
    main()
