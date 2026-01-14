import subprocess
import sys

print("[AVVIO] Cloud Server")
server = subprocess.Popen([sys.executable, "cloud_server.py"])

print("[AVVIO] Bridge WebSocket")
bridge = subprocess.Popen([sys.executable, "bridge_ws.py"])

try:
    server.wait()
    bridge.wait()
except KeyboardInterrupt:
    print("\n[STOP] Arresto servizi")
    server.terminate()
    bridge.terminate()
