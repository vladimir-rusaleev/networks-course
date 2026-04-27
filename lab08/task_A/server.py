import random
import socket

HOST = '127.0.0.1'
PORT = 8888
OUTPUT_FILE = "received_file.bin"


def parse_data_packet(packet):
    if len(packet) < 2:
        raise ValueError()
    seq = packet[0]
    eof = packet[1]
    chunk = packet[2:]
    return seq, eof, chunk


def make_ack_packet(seq):
    return bytes([seq])


def send_ack_with_loss(sock, seq, address):
    if random.random() < 0.3:
        print(f"ACK {seq} потерялся")
        return
    sock.sendto(make_ack_packet(seq), address)


def main():
    expected_seq = 0
    output_name = OUTPUT_FILE
    output_file = None
    transfer_complete = False

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((HOST, PORT))
        print(f"cервер запущен на {HOST}:{PORT}")

        while True:
            try:
                raw_data, client_address = sock.recvfrom(4096)
            except OSError as e:
                print(e)
                break

            try:
                seq, eof, chunk = parse_data_packet(raw_data)
            except ValueError as e:
                print(e)
                continue

            if seq == expected_seq and not transfer_complete:
                if output_file is None:
                    output_file = open(output_name, "wb")
                    print(f"Пишем в файл {output_name}")

                output_file.write(chunk)
                output_file.flush()
                print(f"получен пакет с seq={seq}, bytes={len(chunk)}")
                send_ack_with_loss(sock, seq, client_address)

                if eof == 1:
                    output_file.close()
                    output_file = None
                    transfer_complete = True
                    print(f"Файл записан")

                expected_seq = 1 - expected_seq
            else:
                print(f"Повторно получен пакет с seq={seq}, заново отправляем ACK")
                send_ack_with_loss(sock, seq, client_address)
    finally:
        if output_file is not None:
            output_file.close()


if __name__ == "__main__":
    main()