import socket
import time
import datetime

HOST = "192.168.0.255"
PORT = 8888

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        print(F"host: {HOST}")
        while True:
            t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            msg = t.encode("utf-8")
            s.sendto(msg, (HOST, PORT))
            print(f"сообщение отправлено: {msg}")
            time.sleep(1)

