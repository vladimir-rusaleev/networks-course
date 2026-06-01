import psutil
import time
import sys

def get_traffic():
    net = psutil.net_io_counters()
    return net.bytes_sent, net.bytes_recv

def format_bytes(b):
    for u in ['B', 'KB', 'MB', 'GB']:
        if b < 1024:
            return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} TB"

sent_start, recv_start = get_traffic()
try:
    while True:
        time.sleep(1)
        sent_now, recv_now = get_traffic()
        sent = sent_now - sent_start
        recv = recv_now - recv_start
        print(f"Исходящий: {format_bytes(sent)}\tвходящий: {format_bytes(recv)}")
except KeyboardInterrupt:
    sys.exit(0)