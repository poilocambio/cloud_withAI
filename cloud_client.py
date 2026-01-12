import socket
import os

HOST = input("Inserisci l'IP del server: ")
PORT = 5001

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

def receive_prompt():
    data = client_socket.recv(1024).decode()
    print(data, end="")

# login
receive_prompt()
username = input()
client_socket.send(username.encode())

receive_prompt()
password = input()
client_socket.send(password.encode())

# riceve esito login
data = client_socket.recv(1024).decode()
print(data)

if "fallito" in data:
    client_socket.close()
    exit()

# loop comandi
while True:
    prompt = client_socket.recv(1024).decode()
    command = input(prompt + "> ")
    client_socket.send(command.encode())

    cmd_type = command.split()[0].upper()

    if cmd_type == "UPLOAD":
        if len(command.split()) < 2:
            print("Specifica il file da caricare.")
            continue
        filename = command.split()[1]
        if not os.path.exists(filename):
            print("File non trovato.")
            continue
        client_socket.recv(1024)  # messaggio pronto
        with open(filename, "rb") as f:
            while True:
                bytes_read = f.read(1024)
                if not bytes_read:
                    break
                client_socket.send(bytes_read)
            client_socket.send(b"<END>")
        print(client_socket.recv(1024).decode())

    elif cmd_type == "DOWNLOAD":
        if len(command.split()) < 2:
            print("Specifica il file da scaricare.")
            continue
        filename = command.split()[1]
        response = client_socket.recv(1024).decode()
        print(response)
        if "File non trovato" in response:
            continue
        with open(filename, "wb") as f:
            while True:
                bytes_read = client_socket.recv(1024)
                if bytes_read.endswith(b"<END>"):
                    f.write(bytes_read[:-5])
                    break
                f.write(bytes_read)
        print(client_socket.recv(1024).decode())

    elif cmd_type == "LIST":
        files = client_socket.recv(1024).decode()
        print(files)

    elif cmd_type == "EXIT":
        print(client_socket.recv(1024).decode())
        break

    else:
        print(client_socket.recv(1024).decode())

client_socket.close()
