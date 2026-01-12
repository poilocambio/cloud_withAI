import socket
import threading

HOST = "localhost"
PORT = 5000

nickname = input("Inserisci il tuo nickname: ")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

def receive_messages():
    while True:
        try:
            message = client_socket.recv(1024).decode()
            print(message)
        except:
            print("Connessione chiusa dal server")
            client_socket.close()
            break

def send_messages():
    while True:
        message = input()
        full_message = f"{nickname}: {message}"
        client_socket.send(full_message.encode())

# Thread per ricevere messaggi
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

# Thread per inviare messaggi
send_thread = threading.Thread(target=send_messages)
send_thread.start()
