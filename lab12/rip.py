import json
import sys
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

def run_rip(routers, neighbours):
    tables = {}
    for ip in routers:
        tables[ip] = {ip: (0, ip)}

    for ip in routers:
        for nb in neighbours[ip]:
            tables[ip][nb] = (1, nb)

    for ip, table in tables.items():
        print(f"Simulation step 1 of router {ip}")
        print(f"{'Source IP':<16} {'Destination IP':<18} {'Next Hop':<16} {'Metric':>6}")
        for dest, (metric, next_hop) in sorted(table.items(), key=lambda x: x[0]):
            print(f"{ip:<16} {dest:<18} {next_hop:<16} {metric:>6}")
        print()

    step = 2
    changed = True
    while changed:
        changed = False
        for my_ip in routers:
            for nb_ip in neighbours[my_ip]:
                for dst_ip, (metric, _) in tables[nb_ip].items():
                    new_metric = metric + 1
                    if dst_ip not in tables[my_ip] or new_metric < tables[my_ip][dst_ip][0]:
                        tables[my_ip][dst_ip] = (new_metric, nb_ip)
                        changed = True
        if changed:
            for ip, table in tables.items():
                print(f"Simulation step {step} of router {ip}")
                print(f"{'Source IP':<16} {'Destination IP':<18} {'Next Hop':<16} {'Metric':>6}")
                for dest, (metric, next_hop) in sorted(table.items(), key=lambda x: x[0]):
                    print(f"{ip:<16} {dest:<18} {next_hop:<16} {metric:>6}")
                print()
            step += 1

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
    tables = run_rip(routers, neighbours)