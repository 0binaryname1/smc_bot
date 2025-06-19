import socket

HOST = '192.168.0.104'  # IP do celular
PORT = 5555

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print("Conectado ao servidor!\n")

    while True:
        msg = input("Digite sua mensagem (ou 'sair'): ")
        if msg.lower() == "sair":
            break
        s.sendall(msg.encode())
