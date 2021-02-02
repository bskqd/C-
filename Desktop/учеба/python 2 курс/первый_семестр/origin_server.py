import socket
import re

EMAIL_PATTERN = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'


def run_server(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen()
    print("=== Сервер запущено ===")
    while True:
        emails = []
        conn, address = s.accept()
        print("Під'єднано", address)
        try:
            while True:
                inp_bytes = conn.recv(1024)
                if not inp_bytes:
                    break
                inp_string = str(inp_bytes, encoding="utf-8")
                out_string = inp_string
                participant = out_string.split(':')[0]
                if re.match(EMAIL_PATTERN, participant) and participant not in emails:
                    emails.append(participant)
                    out_bytes = bytes(participant, encoding="utf-8")
                    conn.sendall(out_bytes)
                else:
                    out_bytes = bytes('existed email', encoding="utf-8")
                    conn.sendall(out_bytes)
        except socket.error as e:
            print(e)
        finally:
            conn.close()
            print("Розірвано зв'язок з", address)

    s.close()
    print("Сервер завершив роботу")


HOST = ""
PORT = 20000


if __name__ == '__main__':
    run_server(HOST, PORT)
