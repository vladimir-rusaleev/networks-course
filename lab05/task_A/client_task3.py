import socket
import ssl
import base64
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SMTP_SERVER = "smtp.mail.ru"
SMTP_PORT = 465
SENDER_EMAIL = "rusaleevv05@mail.ru"
SENDER_PASSWORD = input().strip()

def send_email(recipient, body_file, image_file):
    file_path = os.path.join(SCRIPT_DIR, body_file)
    with open(file_path, "r", encoding="utf-8") as f:
        body = f.read()
    image_path = os.path.join(SCRIPT_DIR, image_file)
    with open(image_path, "rb") as f:
        image_data = f.read()
        encoded_image = base64.b64encode(image_data).decode()

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

    boundary = "12345678"

    message = f"""From: {SENDER_EMAIL}
To: {recipient}
Subject: test email
Content-Type: multipart/mixed; boundary="{boundary}"

--{boundary}
Content-Type: text/plain; charset=utf-8

{body}

--{boundary}
Content-Type: image/jpeg; name="{os.path.basename(image_file)}"
Content-Transfer-Encoding: base64
Content-Disposition: attachment; filename="{os.path.basename(image_file)}"

{encoded_image}

--{boundary}--
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
    print("Файл с картинкой ")
    image_file = input()
    send_email(recipient, body_file, image_file)