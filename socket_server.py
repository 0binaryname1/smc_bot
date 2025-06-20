import socket

HOST = '192.168.0.105'  # Escuta em todas as interfaces
PORT = 5555       # Porta de comunicação

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Servidor ouvindo na porta {PORT}...")

    conn, addr = s.accept()
    with conn:
        print(f"Conectado por {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print("Mensagem recebida:", data.decode())
