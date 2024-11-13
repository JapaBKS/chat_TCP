# client.py

import socket
import threading

# Endereço e porta do servidor
host = '192.168.0.101'  # Substitua pelo endereço IP do servidor
port = 5555

# Função para receber mensagens do servidor
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message == 'USERNAME':
                client_socket.send(username.encode('utf-8'))
            elif message == 'EXIT':
                print("Você saiu do chat.")
                client_socket.close()
                break
            else:
                print(message)
        except:
            print("Ocorreu um erro na conexão.")
            client_socket.close()
            break

# Função principal do cliente
def main():
    global username
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    username = input("Digite seu nome de usuário: ")

    # Inicia a thread para receber mensagens do servidor
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    # Loop para enviar mensagens ao servidor
    while True:
        message = input()
        if message:
            client_socket.send(message.encode('utf-8'))
            if message.startswith('/sair'):
                break

if __name__ == "__main__":
    main()
