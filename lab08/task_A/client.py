import socket
import random

HOST = '127.0.0.1'
PORT = 8888
PKT_SIZE = 64

def make_packet(seq, eof, chunk):
    return bytes([seq, eof]) + chunk


def parse_packet(packet):
    if len(packet) < 1:
        raise ValueError()
    return packet[0]

def send_with_loss(sock, packet, address, label):
    if random.random() < 0.3:
        print(f"{label} потерялся")
        return
    sock.sendto(packet, address)

def main():
    filename = input("Введите имя файла: ")
    timeout = float(input("Введите таймаут: "))
    print()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)

    try:
        with open(filename, "rb") as file:
            data = file.read()
    except OSError as e:
        print(e)
        return

    chunks = [data[i:i + PKT_SIZE] for i in range(0, len(data), PKT_SIZE)] or [b""]
    seq = 0

    try:
        for index, chunk in enumerate(chunks, start=1):
            eof = 1 if index == len(chunks) else 0
            packet = make_packet(seq, eof, chunk)

            while True:
                print(f"отправляем пакет {index}, seq={seq}, bytes={len(chunk)}")
                send_with_loss(sock, packet, (HOST, PORT), f"seq={seq}")

                try:
                    raw_ack, _ = sock.recvfrom(4096)
                    ack_seq = parse_packet(raw_ack)
                except socket.timeout:
                    print(f"таймаут: seq={seq}")
                    continue
                except OSError as e:
                    print(e)
                    continue

                if ack_seq == seq:
                    print(f"ACK {seq} получен")
                    seq = 1 - seq
                    break

                print(f"что-то пошло не так, seq={ack_seq}, отправим заново")

        print("файл отправлен")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()