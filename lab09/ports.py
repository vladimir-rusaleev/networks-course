import socket
import sys

def main():
    if len(sys.argv) != 4:
        print("invalid arguments")
    ip = sys.argv[1]
    st = int(sys.argv[2])
    end = int(sys.argv[3])

    for p in range(st, end):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.3)
        res = sock.connect_ex((ip, p))
        if res != 0:
            print(p)
        sock.close()

if __name__ == "__main__":
    main()