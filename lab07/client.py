import socket
import time

def main():
    HOST = '127.0.0.1'
    PORT = 8888
    TIMEOUT = 1.0
    ITERS = 10

    rtt_list = []
    received_cnt = 0
    lost_cnt = 0

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT)

    print(f"Обмен пакетами с {HOST}:")

    for i in range(ITERS):
        send_time = time.perf_counter()
        msg = f"Ping {i+1} {send_time}"

        try:
            sock.sendto(msg.encode(), (HOST, PORT))

            data, _ = sock.recvfrom(1024)
            recv_time = time.perf_counter()
            resp = data.decode()

            rtt_ms = (recv_time - send_time) * 1000
            rtt_list.append(rtt_ms)
            received_cnt += 1
            print(f"Ответ от {HOST}: число байт={len(data)} время={rtt_ms:.3f}мс")

        except socket.timeout:
            lost_cnt += 1
            print("Превышен интервал ожидания для запроса")

    sock.close()
    lost_percent = received_cnt / ITERS * 100
    mean_rtt = sum(rtt_list) / ITERS
    print(f"Статистика Ping для {HOST}:")
    print(f"Пакетов: отправлено = {ITERS}, получено = {received_cnt}, потеряно= {lost_cnt} ({lost_percent}% потерь)\n\
    Приблизительное время приема-передачи в мс:\n\
        Минимальное: = {min(rtt_list):.3f}мсек, Максимальное = {max(rtt_list):.3f}мсек, Среднее = {mean_rtt:.3f}мсек")

if __name__ == "__main__":
    main()
