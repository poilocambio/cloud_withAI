"""
bridge_ws.py

Bridge WebSocket <-> TCP socket

- NON modifica il protocollo TCP
- NON interpreta i dati
- inoltra byte identici in entrambe le direzioni
- una connessione WebSocket = una connessione TCP

Compatibile Python 3.x
"""

import asyncio
import socket
import websockets

# ===== CONFIGURAZIONE =====
TCP_SERVER_HOST = "127.0.0.1"   # IP del cloud_server.py
TCP_SERVER_PORT = 5001          # Porta del cloud_server.py

WS_HOST = "0.0.0.0"             # Dove ascolta il bridge
WS_PORT = 8080                  # Porta WebSocket


async def bridge_handler(websocket):
    """
    Gestisce una singola connessione WebSocket.
    Apre una socket TCP verso il server e inoltra i dati.
    """

    # Connessione TCP verso il server esistente
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.setblocking(True)

    try:
        tcp_sock.connect((TCP_SERVER_HOST, TCP_SERVER_PORT))
    except Exception as e:
        await websocket.close()
        return

    loop = asyncio.get_running_loop()

    async def tcp_to_ws():
        """
        Legge dal server TCP e inoltra al WebSocket.
        """
        try:
            while True:
                # recv bloccante eseguito in thread separato
                data = await loop.run_in_executor(None, tcp_sock.recv, 1024)
                if not data:
                    break

                # invia come binario se necessario
                try:
                    await websocket.send(data.decode())
                except UnicodeDecodeError:
                    await websocket.send(data)
        except Exception:
            pass

    async def ws_to_tcp():
        """
        Legge dal WebSocket e inoltra al server TCP.
        """
        try:
            async for message in websocket:
                # message può essere str o bytes
                if isinstance(message, str):
                    tcp_sock.sendall(message.encode())
                else:
                    tcp_sock.sendall(message)
        except Exception:
            pass

    # Esecuzione parallela delle due direzioni
    await asyncio.gather(tcp_to_ws(), ws_to_tcp())

    tcp_sock.close()


async def main():
    """
    Avvia il server WebSocket.
    """
    async with websockets.serve(bridge_handler, WS_HOST, WS_PORT):
        print(f"[BRIDGE ATTIVO] WebSocket su ws://{WS_HOST}:{WS_PORT}")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
