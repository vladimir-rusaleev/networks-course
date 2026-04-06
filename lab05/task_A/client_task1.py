import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SMTP_SERVER = "smtp.mail.ru"
SMTP_PORT = 465
SENDER_EMAIL = "rusaleevv05@mail.ru"
SENDER_PASSWORD = input().strip()

def send_email(recipient, body_file, format):
    file_path = os.path.join(SCRIPT_DIR, body_file)
    with open(file_path, "r", encoding="utf-8") as f:
        body = f.read()

    if format == "txt":
        msg = MIMEText(body, "plain", "utf-8")
    else:
        msg = MIMEText(body, "html", "utf-8")

    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient
    msg["Subject"] = "test email"

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        print("Письмо отправлено")

if __name__ == "__main__":
    print("Получатель: ")
    recipient = input()
    print("Файл с телом письма: ")
    body_file = input()
    print("Формат(txt/html): ")
    format = input()
    send_email(recipient, body_file, format)