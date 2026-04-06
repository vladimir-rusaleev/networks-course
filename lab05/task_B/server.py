import socket
import subprocess
import sys

HOST = "127.0.0.1"
PORT = 8888

def exec_cmd(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True,  encoding="cp866")
    if res.stdout:
         return res.stdout
    elif res.stderr:
        return res.stderr
    else:
        return "no output"

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            with conn:
                data = conn.recv(4096).decode("utf-8")
                if not data:
                    break
                print(f"команда: {data}")
                output = exec_cmd(data)
                conn.sendall(output.encode("utf-8"))
                print("ответ отправлен")
