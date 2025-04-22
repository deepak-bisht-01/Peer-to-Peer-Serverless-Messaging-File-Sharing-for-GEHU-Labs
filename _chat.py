import socket
import threading

UDP_PORT = 5000
TCP_PORT = 6000
BUFFER_SIZE = 1024

peers = set()

# ---------- UDP Broadcast ----------
def udp_broadcast():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    msg = "DISCOVER_PEER".encode('utf-8')
    while True:
        udp_socket.sendto(msg, ('255.255.255.255', UDP_PORT))
        threading.Event().wait(5)  # Broadcast every 5 seconds

# ---------- UDP Listener ----------
def udp_listener():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(('', UDP_PORT))
    while True:
        data, addr = udp_socket.recvfrom(BUFFER_SIZE)
        if data.decode() == "DISCOVER_PEER" and addr[0] != socket.gethostbyname(socket.gethostname()):
            peers.add(addr[0])

# ---------- TCP Server ----------
def tcp_server():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind(('', TCP_PORT))
    tcp_socket.listen(5)
    print(f"[TCP Server] Listening on port {TCP_PORT}...")

    while True:
        conn, addr = tcp_socket.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

def handle_client(conn, addr):
    print(f"[New Connection] {addr[0]} connected.")
    while True:
        try:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            print(f"[{addr[0]}] {data.decode()}")
        except:
            break
    conn.close()

# ---------- TCP Client Sender ----------
def send_messages():
    while True:
        msg = input()
        for peer_ip in peers:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((peer_ip, TCP_PORT))
                    s.sendall(msg.encode())
            except:
                pass  # Peer might be offline or not ready

# ---------- Main ----------
if __name__ == "__main__":
    threading.Thread(target=udp_broadcast, daemon=True).start()
    threading.Thread(target=udp_listener, daemon=True).start()
    threading.Thread(target=tcp_server, daemon=True).start()
    
    print("[*] Peer-to-Peer LAN Chat Started. Type messages to broadcast.")
    send_messages()
