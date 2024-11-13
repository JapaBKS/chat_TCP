import socket
import threading

# Endereço e porta do servidor
host = '192.168.0.101'  # Escuta em todas as interfaces
port = 5555

# Lista de clientes conectados
clients = []  # Lista de sockets dos clientes
usernames = {}  # Dicionário que mapeia sockets para nomes de usuários
client_addresses = {}  

# Função para lidar com cada cliente conectado
def handle_client(client_socket, client_address):
    try:
        # Solicita o nome de usuário
        client_socket.send('USERNAME'.encode('utf-8'))
        username = client_socket.recv(1024).decode('utf-8')
        usernames[client_socket] = username
        clients.append(client_socket)
        client_addresses[client_socket] = client_address

        print(f"Usuário {username} conectado: IP {client_address[0]}, Porta {client_address[1]}")

        # Notifica todos os clientes sobre a nova conexão
        broadcast(f"{username} entrou no chat. IP: {client_address[0]}, Porta: {client_address[1]}", client_socket)

        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                if message.startswith('/sair'):
                    # Comando para sair do chat
                    client_socket.send('EXIT'.encode('utf-8'))
                    remove_client(client_socket)
                    break
                elif message.startswith('/privado'):
                    # Mensagem privada
                    parts = message.split(' ', 2)
                    if len(parts) >= 3:
                        recipient_name = parts[1]
                        private_message = parts[2]
                        send_private_message(private_message, usernames[client_socket], recipient_name, client_socket)
                    else:
                        client_socket.send('Uso correto: /privado nome_usuario mensagem'.encode('utf-8'))
                else:
                    # Mensagem pública
                    broadcast(f"{usernames[client_socket]}: {message}", client_socket)
            else:
                # Desconexão inesperada
                remove_client(client_socket)
                break
    except (ConnectionResetError, TimeoutError, OSError):
        remove_client(client_socket)
        return

# Função para enviar mensagens para todos os clientes conectados (broadcast)
def broadcast(message, sender_socket):
    for client in clients.copy():
        try:
            if client != sender_socket:
                client.send(message.encode('utf-8'))
        except:
            remove_client(client)

# Função para enviar mensagens privadas
def send_private_message(message, sender_username, recipient_username, sender_socket):
    recipient_socket = None
    for client_socket, username in usernames.items():
        if username == recipient_username:
            recipient_socket = client_socket
            break

    if recipient_socket:
        try:
            recipient_socket.send(f"[Privado de {sender_username}]: {message}".encode('utf-8'))
            sender_socket.send(f"[Privado para {recipient_username}]: {message}".encode('utf-8'))
        except:
            remove_client(recipient_socket)
    else:
        sender_socket.send(f"Usuário {recipient_username} não encontrado.".encode('utf-8'))

# Função para remover um cliente da lista e fechar a conexão
def remove_client(client_socket):
    if client_socket in clients:
        username = usernames.get(client_socket, "Desconhecido")
        client_address = client_addresses.get(client_socket, ("Desconhecido", "Desconhecido"))
        ip = client_address[0]
        port = client_address[1]
        print(f"Usuário {username} desconectado: IP {ip}, Porta {port}")
        clients.remove(client_socket)
        del usernames[client_socket]
        del client_addresses[client_socket]
        client_socket.close()
        broadcast(f"{username} saiu do chat. IP: {ip}, Porta: {port}", client_socket)

# Função principal do servidor
def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()

    print(f"Servidor rodando em {host}:{port}")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket, client_address)).start()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()
