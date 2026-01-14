import socket
import threading
import os
import struct  # per lunghezza file

HOST = "0.0.0.0"
PORT = 5001
STORAGE_DIR = "cloud_storage"

# utenti hardcoded
USERS = {"Henric Ione": "1234a", "Poe Raccho": "1234a", "Frank Obbollo": "1234a"}

# crea la cartella se non esiste
if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

def handle_client(client_socket, client_address):
    username = None
    try:
        client_socket.send(b"Benvenuto nel Mini Cloud!\nUsername: ")
        username = client_socket.recv(1024).decode().strip()
        print(f"[CONNESSIONE INIZIATA] {client_address} sta provando a loggare come '{username}'")

        client_socket.send(b"Password: ")
        password = client_socket.recv(1024).decode().strip()

        if USERS.get(username) != password:
            client_socket.send(b"Login fallito. Connessione chiusa.\n")
            client_socket.close()
            print(f"[LOGIN FALLITO] {client_address} ha tentato di loggare come '{username}'")
            return

        client_socket.send(b"Login riuscito!\nComandi: UPLOAD <file>, DOWNLOAD <file>, LIST, EXIT\n")
        print(f"[LOGIN RIUSCITO] {username} ({client_address}) si è connesso al server")

        while True:
            client_socket.send(b"\n> ")
            data = client_socket.recv(1024).decode().strip()
            if not data:
                print(f"[DISCONNESSIONE FORZATA] {username} ({client_address}) ha chiuso la connessione improvvisamente")
                break

            command = data.split()[0].upper()

            # ----------------- UPLOAD -----------------
            if command == "UPLOAD":
                if len(data.split()) < 2:
                    client_socket.send(b"Specifica il nome del file.\n")
                    continue
                filename = data.split()[1]
                client_socket.send(b"Pronto a ricevere il file.\n")
                print(f"[UPLOAD INIZIATO] {username} sta caricando '{filename}'")

                # legge la lunghezza del file
                raw_size = client_socket.recv(8)
                filesize = struct.unpack(">Q", raw_size)[0]

                received = 0
                with open(os.path.join(STORAGE_DIR, filename), "wb") as f:
                    while received < filesize:
                        chunk = client_socket.recv(min(1024, filesize - received))
                        if not chunk:
                            break
                        f.write(chunk)
                        received += len(chunk)

                client_socket.send(b"File caricato!\n")
                print(f"[UPLOAD COMPLETATO] {username} ha caricato '{filename}' ({filesize} byte)")

            # ----------------- DOWNLOAD -----------------
            elif command == "DOWNLOAD":
                if len(data.split()) < 2:
                    client_socket.send(b"Specifica il nome del file.\n")
                    continue
                filename = data.split()[1]
                filepath = os.path.join(STORAGE_DIR, filename)
                if not os.path.exists(filepath):
                    client_socket.send(b"File non trovato.\n")
                    print(f"[DOWNLOAD FALLITO] {username} ha tentato di scaricare '{filename}', file inesistente")
                    continue

                client_socket.send(b"Inizio trasferimento file...\n")
                filesize = os.path.getsize(filepath)
                client_socket.send(struct.pack(">Q", filesize))
                print(f"[DOWNLOAD INIZIATO] {username} sta scaricando '{filename}' ({filesize} byte)")

                with open(filepath, "rb") as f:
                    while True:
                        chunk = f.read(1024)
                        if not chunk:
                            break
                        client_socket.sendall(chunk)

                client_socket.send(b"\nFile scaricato!\n")
                print(f"[DOWNLOAD COMPLETATO] {username} ha scaricato '{filename}' ({filesize} byte)")

            # ----------------- LIST -----------------
            elif command == "LIST":
                files = os.listdir(STORAGE_DIR)
                if files:
                    client_socket.send("\n".join(files).encode() + b"\n")
                else:
                    client_socket.send(b"Nessun file presente.\n")
                print(f"[LIST] {username} ha richiesto la lista dei file: {files}")

            # ----------------- EXIT -----------------
            elif command == "EXIT":
                client_socket.send(b"Chiusura connessione.\n")
                print(f"[DISCONNESSIONE] {username} ({client_address}) ha chiuso la connessione volontariamente")
                break

            # ----------------- COMANDO NON RICONOSCIUTO -----------------
            else:
                client_socket.send(b"Comando non riconosciuto.\n")
                print(f"[COMANDO SCONOSCIUTO] {username} ha digitato '{data}'")

    except Exception as e:
        print(f"[ERRORE] con {client_address} ({username}): {e}")
    finally:
        client_socket.close()
        print(f"[CONNESSIONE CHIUSA] {client_address} ({username}) chiusa correttamente")


# ---- MAIN SERVER ----
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()
server_socket.settimeout(1)  # <-- timeout per permettere Ctrl+C
print(f"[SERVER IN ASCOLTO] Mini Cloud su {HOST}:{PORT}")

running = True

try:
    while running:
        try:
            client_socket, client_address = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            thread.start()
        except socket.timeout:
            continue  # timeout scaduto, ricontrolla il ciclo
except KeyboardInterrupt:
    print("\n[SERVER FERMIATO] Manualmente")
    running = False
finally:
    server_socket.close()
