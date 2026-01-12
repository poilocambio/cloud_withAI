import socket
import os
import struct  # per lunghezza file

HOST = input("Inserisci l'IP del server: ")
PORT = 5001

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.settimeout(10)  # timeout 10 secondi su operazioni di ricezione
client_socket.connect((HOST, PORT))

def safe_recv(size=1024):
    """Recv con gestione timeout"""
    try:
        return client_socket.recv(size)
    except socket.timeout:
        print("[ATTENZIONE] Timeout: il server non ha risposto")
        return b""

def receive_prompt():
    data = safe_recv().decode()
    print(data, end="")

# ----------------- LOGIN -----------------
receive_prompt()
username = input()
client_socket.send(username.encode())

receive_prompt()
password = input()
client_socket.send(password.encode())

# riceve esito login
data = safe_recv().decode()
print(data)

if "fallito" in data:
    client_socket.close()
    exit()

# ----------------- LOOP COMANDI -----------------
while True:
    prompt = safe_recv().decode()
    command = input(prompt + "> ")
    client_socket.send(command.encode())

    cmd_type = command.split()[0].upper()

    # ----------------- UPLOAD -----------------
    if cmd_type == "UPLOAD":
        if len(command.split()) < 2:
            print("Specifica il file da caricare.")
            continue
        filename = command.split()[1]
        if not os.path.exists(filename):
            print("File non trovato.")
            continue

        safe_recv()  # messaggio "Pronto a ricevere il file"

        filesize = os.path.getsize(filename)
        client_socket.send(struct.pack(">Q", filesize))  # invia lunghezza file 8 byte

        sent = 0
        with open(filename, "rb") as f:
            while sent < filesize:
                chunk = f.read(1024)
                if not chunk:
                    break
                client_socket.sendall(chunk)
                sent += len(chunk)

        print(safe_recv().decode())

    # ----------------- DOWNLOAD -----------------
    elif cmd_type == "DOWNLOAD":
        if len(command.split()) < 2:
            print("Specifica il file da scaricare.")
            continue
        filename = command.split()[1]

        response = safe_recv().decode()
        print(response)
        if "File non trovato" in response:
            continue

        # legge i primi 8 byte con la lunghezza del file
        raw_filesize = safe_recv(8)
        if not raw_filesize:
            print("[ERRORE] Non è stato possibile leggere la dimensione del file")
            continue
        filesize = struct.unpack(">Q", raw_filesize)[0]

        received = 0
        with open(filename, "wb") as f:
            while received < filesize:
                chunk = safe_recv(min(1024, filesize - received))
                if not chunk:
                    break
                f.write(chunk)
                received += len(chunk)

        print(safe_recv().decode())

    # ----------------- LIST -----------------
    elif cmd_type == "LIST":
        files = safe_recv().decode()
        print(files)

    # ----------------- EXIT -----------------
    elif cmd_type == "EXIT":
        print(safe_recv().decode())
        break

    # ----------------- COMANDO NON RICONOSCIUTO -----------------
    else:
        print(safe_recv().decode())

client_socket.close()
