import socket
import ssl
import base64
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SMTP_SERVER = "smtp.mail.ru"
SMTP_PORT = 465
SENDER_EMAIL = "rusaleevv05@mail.ru"
SENDER_PASSWORD = input().strip()

def send_email(recipient, body_file, format):
    file_path = os.path.join(SCRIPT_DIR, body_file)
    with open(file_path, "r", encoding="utf-8") as f:
        body = f.read()

    context = ssl.create_default_context()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssl_sock = context.wrap_socket(sock, server_hostname=SMTP_SERVER)
    ssl_sock.connect((SMTP_SERVER, SMTP_PORT))

    ssl_sock.recv(1024)
    ssl_sock.send(b"EHLO test\r\n")
    ssl_sock.recv(1024)
    
    ssl_sock.send(b"AUTH LOGIN\r\n")
    ssl_sock.recv(1024)

    login_b64 = base64.b64encode(SENDER_EMAIL.encode()).decode()
    ssl_sock.send((login_b64 + "\r\n").encode())
    ssl_sock.recv(1024)

    pass_b64 = base64.b64encode(SENDER_PASSWORD.encode()).decode()
    ssl_sock.send((pass_b64 + "\r\n").encode())
    ssl_sock.recv(1024)

    ssl_sock.send(f"MAIL FROM:<{SENDER_EMAIL}>\r\n".encode())
    ssl_sock.recv(1024)

    ssl_sock.send(f"RCPT TO:<{recipient}>\r\n".encode())
    ssl_sock.recv(1024)

    ssl_sock.send(b"DATA\r\n")
    ssl_sock.recv(1024)

    if format == "txt":
        content_type = "text/plain"
    else:
        content_type = "text/html"

    message = f"""From: {SENDER_EMAIL}
To: {recipient}
Subject: test email
Content-Type: {content_type}; charset=utf-8

{body}
"""
    ssl_sock.send((message + "\r\n.\r\n").encode())
    ssl_sock.recv(1024)
    ssl_sock.send(b"QUIT\r\n")
    ssl_sock.close()
    
    print("Письмо отправлено через сокеты")

if __name__ == "__main__":
    print("Получатель: ")
    recipient = input()
    print("Файл с телом письма: ")
    body_file = input()
    print("Формат(txt/html): ")
    format = input()
    send_email(recipient, body_file, format)