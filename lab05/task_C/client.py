import socket

HOST = ""
PORT = 8888

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        while True:
            msg, addr = s.recvfrom(1024)
            print(f"получено: {msg}   от {addr}")