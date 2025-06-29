import os
import socket
import threading
import time
from flask import Flask
from waitress import serve

# Ortam değişkenlerini al
TCP_PORT = int(os.getenv("TCP_PORT", 39111))
FLASK_PORT = int(os.getenv("PORT", 8080))  # Railway bunu otomatik verir
IMEI = os.getenv("IMEI", "862205059210023")

print(f"IMEI: {IMEI}")
print(f"TCP_PORT: {TCP_PORT}")
print(f"HTTP_PORT: {FLASK_PORT}")

# Flask app
app = Flask(__name__)

@app.route("/")
def index():
    return "Server çalışıyor", 200

@app.route("/health")
def health():
    return "OK", 200

# TCP bağlantıları dinleyen fonksiyon
def handle_client(conn, addr):
    print(f"[+] TCP bağlantısı: {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            msg = data.decode(errors="ignore").strip()
            print(f"[{addr}] <<< {msg}")

            if "*CMDR" in msg and "Q0" in msg:
                print("[✓] Q0 geldi, L0 gönderiliyor...")
                cmd = f"*CMDS,OM,{IMEI},000000000000,L0,0,0,{int(time.time())}#\n"
                conn.sendall(cmd.encode())
                print(f"[>>] Gönderildi: {cmd.strip()}")
    except Exception as e:
        print(f"[!] Hata: {e}")
    finally:
        print(f"[-] Bağlantı kapandı: {addr}")
        conn.close()

def tcp_server():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind(("0.0.0.0", TCP_PORT))
    srv.listen()
    print(f"[TCP] Dinleniyor: {TCP_PORT}")
    while True:
        conn, addr = srv.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

# Başlat
if __name__ == "__main__":
    print("Sunucu başlıyor...")
    threading.Thread(target=tcp_server, daemon=True).start()
    serve(app, host="0.0.0.0", port=FLASK_PORT)
