import socket
import struct
import time
import sys
import os

ICMP_ECHO_REQUEST = 8
ICMP_ECHO_REPLY = 0
ICMP_TIME_EXCEEDED = 11
MAX_HOPS = 30
COUNT = 3

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

def create_packet(seq, pid):
    header = struct.pack("!BBHHH", ICMP_ECHO_REQUEST, 0, 0, pid, seq)
    payload = struct.pack("!d", time.time())
    packet = header + payload
    cksum = checksum(packet)
    header = struct.pack("!BBHHH", ICMP_ECHO_REQUEST, 0, cksum, pid, seq)
    return header + payload

def parse_ip_header(data):
    header_len = (data[0] & 0x0F) * 4
    src = socket.inet_ntoa(data[12:16])
    return src, header_len

def get_hostname(ip):
    try:
        hostname = socket.gethostbyaddr(ip)[0]
        return f"{hostname} ({ip})"
    except socket.herror:
        return ip

def main():
    if len(sys.argv) < 2:
        print("invalid arguments")
        sys.exit(1)
    dest_name = sys.argv[1]

    try:
        dest_addr = socket.gethostbyname(dest_name)
    except socket.gaierror:
        print("cant resolve address")
        sys.exit(1)

    print(f"traceroute to {dest_name} ({dest_addr}), {MAX_HOPS} hops, {COUNT} probes")

    pid = os.getpid() & 0xFFFF
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    recv_sock.settimeout(2.0)

    reached = False
    for ttl in range(1, MAX_HOPS + 1):
        send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)

        send_times = {}
        for i in range(COUNT):
            seq = (ttl << 8) + i
            pkt = create_packet(seq, pid)
            t = time.time()
            try:
                send_sock.sendto(pkt, (dest_addr, 0))
                send_times[seq] = t
            except socket.error:
                continue

        responses = {}
        deadline = time.time() + 2.0
        while time.time() < deadline:
            try:
                rem = max(0, deadline - time.time())
                recv_sock.settimeout(rem)
                pkt, _ = recv_sock.recvfrom(2048)
                recv_time = time.time()

                src_ip, header_len = parse_ip_header(pkt)
                icmp = pkt[header_len:]
                if len(icmp) < 8:
                    continue
                itype, icode, _, rid, rseq = struct.unpack("!BBHHH", icmp[:8])

                if itype == ICMP_TIME_EXCEEDED and icode == 0:
                    emb_header_len = (icmp[8] & 0x0F) * 4
                    orig = icmp[8 + emb_header_len : 8 + emb_header_len + 8]
                    if len(orig) < 8:
                        continue
                    oid, oseq = struct.unpack("!HH", orig[4:8])
                    if oid == pid and oseq in send_times:
                        rtt = (recv_time - send_times[oseq]) * 1000
                        responses.setdefault(src_ip, []).append(rtt)
                elif itype == ICMP_ECHO_REPLY and icode == 0:
                    if rid == pid and rseq in send_times:
                        rtt = (recv_time - send_times[rseq]) * 1000
                        responses.setdefault(src_ip, []).append(rtt)
            except socket.timeout:
                break

        if responses:
            for ip in responses:
                rtt_str = "  ".join(f"{v:.3f} ms" for v in responses[ip])
                name = get_hostname(ip)
                print(f"{ttl:2d}  {name}  {rtt_str}")
            if dest_addr in responses:
                reached = True
        else:
            print(f"{ttl:2d} ---")

        if reached:
            break

    send_sock.close()
    recv_sock.close()

if __name__ == "__main__":
    main()