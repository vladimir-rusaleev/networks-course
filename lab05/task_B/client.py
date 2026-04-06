import socket

HOST = "127.0.0.1"
PORT = 8888

if __name__ == "__main__":
    cmd = input()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(cmd.encode("utf-8"))
        res = s.recv(4096).decode("utf-8")
        print(res)