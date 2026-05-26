import json
import sys
import time
import threading
from collections import defaultdict

def load_file(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    routers = data["routers"]
    edges = data["edges"]
    neighbours = defaultdict(set)
    for a, b in edges:
        neighbours[a].add(b)
        neighbours[b].add(a)
    return routers, neighbours

lock = threading.Lock()

def router_thread(ip, neighbours, tables, stop_event, step_counter):
    while not stop_event.is_set():
        changed = False
        with lock:
            for nb_ip in neighbours[ip]:
                for dst_ip, (metric, _) in tables[nb_ip].items():
                    new_metric = metric + 1
                    if dst_ip not in tables[ip] or new_metric < tables[ip][dst_ip][0]:
                        tables[ip][dst_ip] = (new_metric, nb_ip)
                        changed = True
        if changed:
            with lock:
                step_counter[0] += 1
                step = step_counter[0]
            with lock:
                print(f"Simulation step {step} of router {ip}")
                print(f"{'Source IP':<16} {'Destination IP':<18} {'Next Hop':<16} {'Metric':>6}")
                table = tables[ip]
                for dest, (metric, next_hop) in sorted(table.items(), key=lambda x: x[0]):
                    print(f"{ip:<16} {dest:<18} {next_hop:<16} {metric:>6}")
                print()
        
        time.sleep(0.1)

def run_rip(routers, neighbours):
    tables = {}
    for ip in routers:
        tables[ip] = {ip: (0, ip)}
    for ip in routers:
        for nb in neighbours[ip]:
            tables[ip][nb] = (1, nb)

    for ip, table in tables.items():
        print(f"Simulation step 0 of router {ip}")
        print(f"{'Source IP':<16} {'Destination IP':<18} {'Next Hop':<16} {'Metric':>6}")
        for dest, (metric, next_hop) in sorted(table.items(), key=lambda x: x[0]):
            print(f"{ip:<16} {dest:<18} {next_hop:<16} {metric:>6}")
        print()

    stop_event = threading.Event()
    step_counter = [0]
    
    threads = []
    for ip in routers:
        t = threading.Thread(target=router_thread, args=(ip, neighbours, tables, stop_event, step_counter), daemon=True)
        threads.append(t)
        t.start()

    time.sleep(2.0)
    stop_event.set()

    for t in threads:
        t.join(timeout=0.5)

    for ip, table in tables.items():
        print(f"Final table of router {ip}:")
        print(f"{'Source IP':<16} {'Destination IP':<18} {'Next Hop':<16} {'Metric':>6}")
        for dest, (metric, next_hop) in sorted(table.items(), key=lambda x: x[0]):
            print(f"{ip:<16} {dest:<18} {next_hop:<16} {metric:>6}")
        print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("invalid arguments")
        sys.exit(1)
    routers, neighbours = load_file(sys.argv[1])
    run_rip(routers, neighbours)