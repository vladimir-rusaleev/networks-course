import socket
import struct
import time
import os
import sys

ICMP_ECHO_REQUEST = 8
ICMP_ECHO_REPLY = 0
TIMEOUT = 1.0
PAYLOAD_SIZE = 56

def checksum(data):
    s = 0
    if len(data) % 2:
        data += b"\x00"
    for i in range(0, len(data), 2):
        w = (data[i] << 8) + data[i+1]
        s += w
    s = (s >> 16) + (s & 0xffff)
    s += s >> 16
    return ~s & 0xffff

def create_icmp_packet(seq, payload):
    pid = os.getpid() & 0xffff
    header = struct.pack("!BBHHH", ICMP_ECHO_REQUEST, 0, 0, pid, seq)
    check_sum = checksum(header + payload)
    header = struct.pack("!BBHHH", ICMP_ECHO_REQUEST, 0, check_sum, pid, seq)
    return header + payload

def ping(host, count):
    dst = socket.gethostbyname(host)
    print(f"Обмен пакетами с {host} [{dst}] с {PAYLOAD_SIZE} байтами данных:")
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
    sent, recv = 0, 0
    rtts = []
    for seq in range(1, count + 1):
        payload = struct.pack("d", time.time()) + b"\x00" * (PAYLOAD_SIZE - 8)
        packet = create_icmp_packet(seq, payload)
        sock.sendto(packet, (dst, 0))
        send_time = time.time()
        sent += 1

        while True:
            remaining = TIMEOUT - (time.time() - send_time)
            if remaining <= 0:
                print(f"Запрос превысил время ожидания для icmp_seq {seq}")
                break

            try:
                data, addr = sock.recvfrom(1024)
                recv_time = time.time()
                ttl = data[8]
                icmp_header = data[20:28]
                type, _, _, _, rseq = struct.unpack("!BBHHH", icmp_header)
                if type == ICMP_ECHO_REPLY and rseq == seq:
                    tstamp = struct.unpack("d", data[28:36])[0]
                    rtt = (recv_time - tstamp) * 1000.0
                    rtts.append(rtt)
                    recv += 1
                    print(f"Ответ от {addr[0]}: число байт={PAYLOAD_SIZE} время={rtt:.0f}мс TTL={ttl}")
                    break
            except:
                continue
        if seq < count:
            time.sleep(1)

    sock.close()
    print()
    print(f"Статистика Ping для {dst}:")
    loss = ((sent - recv) / sent * 100) if sent > 0 else 0
    print(f"Пакетов: отправлено = {sent}, получено = {recv}, потеряно = {sent - recv}")
    print(f"({loss:.0f}% потерь)")
    if rtts:
        avg = sum(rtts) / len(rtts)
        print("Приблизительное время приема-передачи в мс:")
        print(f"Минимальное = {min(rtts):.0f}мсек, Максимальное = {max(rtts):.0f} мсек, Среднее = {avg:.0f} мсек")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("invalid arguments")
    else:
        host  = sys.argv[1]
        count = int(sys.argv[2])
        ping(host, count)