import socket
import threading

HOST = '127.0.0.1'
PORT = 55555
ADDR = (HOST, PORT)

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")
            if message:
                print(message)
        except Exception as e:
            print(f"[ERROR] Error al recibir mensaje: {e}")
            break

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(ADDR)
    name = input("Ingrese su nombre: ")
    client_socket.send(name.encode("utf-8"))
    welcome_message = client_socket.recv(1024).decode("utf-8")
    print(welcome_message)
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    while True:
        message = input()
        client_socket.send(message.encode("utf-8"))

if __name__ == "__main__":
    main()

