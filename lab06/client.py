import ftplib
import os

def show(ftp):
    try:
        items = []
        ftp.dir(items.append)
        for i in items:
            print(i)
    except Exception as e:
        print(e)

def upload(ftp, filepath, remote_filename):
    if not os.path.isfile(filepath):
        print("Файл не найден")
        return
    if not remote_filename:
        remote_filename = os.path.basename(filepath)

    try:
        with open(filepath, 'rb') as f:
            ftp.storbinary(f'STOR {remote_filename}', f)
        print("файл загружен")
    except Exception as e:
        print(e)

def download(ftp, remote_filename, filepath):
    if not filepath:
        filepath = remote_filename
    
    try:
        with open(filepath, 'wb') as f:
            ftp.retrbinary(f'RETR {remote_filename}', f.write)
        print(f"файл {remote_filename} скачан")
    except Exception as e:
        print(e)

def main():
    host = input("Host: ").strip()
    user = input("User: ").strip()
    pwd = input("Password ").strip()

    try:
        ftp = ftplib.FTP(host)
        ftp.login(user, pwd)
        print("список действий:\n" \
        "show\n" \
        "upload filepath remote_filename\n" \
        "download remote_filename filepath\n\n")

        while True:
            try:
                cmds = input().split()
                if cmds[0].lower() == "show":
                    show(ftp)
                elif cmds[0].lower() == "upload":
                    upload(ftp, cmds[1], cmds[2])
                elif cmds[0].lower() == "download":
                    download(ftp, cmds[1], cmds[2])
                else:
                    print("invalid arguments")
            except Exception as e:
                print("invalid arguments")
    except Exception as e:
        print(e)
    finally:
        if ftp:
            ftp.quit()

if __name__ == "__main__":
    main()