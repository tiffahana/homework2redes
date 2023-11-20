import socket
import threading
import json

HOST = '127.0.0.1'
PORT = 55555
ADDR = (HOST, PORT)

clients = []
artefactos = {}
mutex = threading.Lock()

with open('artefactos.json', 'r') as file:
    artefactos = json.load(file)

def broadcast(message, sender_name="SERVER"):
    with mutex:
        for client, name in clients:
            try:
                if ": " in message:
                    client.send(f"{message}\n".encode("utf-8"))
                else:
                    client.send(f"{sender_name}: {message}\n".encode("utf-8"))
            except Exception as e:
                print(f"[ERROR] No se pudo enviar mensaje a un cliente: {e}")


def private_message(sender, recipient, message):
    with mutex:
        for client, name in clients:
            if name == recipient:
                try:
                    client.send(f"[PM] {sender}: {message}\n".encode("utf-8"))
                except Exception as e:
                    print(f"[ERROR] No se pudo enviar mensaje privado: {e}")

def user_list(client):
    with mutex:
        users = ', '.join([name for _, name in clients])
        client.send(f"[SERVER] Usuarios conectados: {users}\n".encode("utf-8"))

def emoticon(client, emoticon):
    client.send(f"{emoticon}\n".encode("utf-8"))

def handle_client(client, name):
    with mutex:
        clients.append((client, name))
    
    client.send("[SERVER] Cuéntame, ¿qué artefactos tienes?\n".encode("utf-8"))
    response = client.recv(1024).decode("utf-8").strip()
    artefacto_ids = response.split(", ")
    artefacto_nombres = [artefactos[id] for id in artefacto_ids]
    client.send(f"[SERVER] Tus artefactos son: {', '.join(artefacto_nombres)}\n".encode("utf-8"))
    client.send("[SERVER] ¿Está bien? (Sí/No)\n".encode("utf-8"))
    response = client.recv(1024).decode("utf-8").strip().lower()
    if response != "sí":
        client.send("[SERVER] Artefactos no confirmados. Desconectando...\n".encode("utf-8"))
        client.close()
        return
    else:
        client.send("[SERVER] ¡OK!\n".encode("utf-8"))
        broadcast(f"{name}: se ha unido al chat. Artefactos: {', '.join(artefacto_nombres)}.", name)

    while True:
        try:
            message = client.recv(1024).decode("utf-8")
            if message:
                if message.startswith(":q"):
                    with mutex:
                        clients.remove((client, name))
                    broadcast(f"{name}: se ha desconectado.")
                    client.send("[SERVER] Desconectado. ¡Hasta luego!\n".encode("utf-8"))
                    client.close()
                    break
                elif message.startswith(":p"):
                    _, recipient, private_message_text = message.split(maxsplit=2)
                    private_message(name, recipient, private_message_text)
                elif message.startswith(":u"):
                    user_list(client)
                elif message.startswith(":smile"):
                    # Enviar carita feliz
                    broadcast(":)", name)
                elif message.startswith(":angry"):
                    broadcast(">:(", name)
                elif message.startswith(":combito"):
                    broadcast("Q(’- ’Q)", name)
                elif message.startswith(":larva"):
                    broadcast("(:o)OOOooo", name)
                elif message.startswith(":artefactos"):
                    client.send(f"[SERVER] Tus artefactos son: {', '.join(artefacto_nombres)}\n".encode("utf-8"))
                elif message.startswith(":artefacto"):
                    _, artefacto_id = message.split()
                    artefacto_nombre = artefactos[name][int(artefacto_id)-1]
                    client.send(f"[SERVER] Artefacto {artefacto_id}: {artefacto_nombre}\n".encode("utf-8"))
                elif message.startswith(":offer"):
                    _, recipient, my_artefact_id, their_artefact_id = message.split()
                    my_artefacto_nombre = artefactos[name][int(my_artefact_id)-1]
                    their_artefacto_nombre = artefactos[recipient][int(their_artefact_id)-1]
                    broadcast(f"{name}: ofrece {my_artefacto_nombre} a {recipient} a cambio de {their_artefacto_nombre}. ¿Aceptar? (:accept/:reject)", name)
                elif message.startswith(":accept"):
                    with mutex:
                        my_artefacto_nombre = artefactos[name][int(my_artefact_id)-1]
                        their_artefacto_nombre = artefactos[recipient][int(their_artefact_id)-1]
                        broadcast(f"{name}: ha aceptado la oferta. Intercambio realizado.", name)
                        broadcast(f"{recipient}: ha aceptado la oferta. Intercambio realizado.", recipient)
                        client.send("[SERVER] ¡Intercambio realizado!\n".encode("utf-8"))
                elif message.startswith(":reject"):
                    broadcast(f"{name}: ha rechazado la oferta. Intercambio rechazado.", name)
                    broadcast(f"{recipient}: ha rechazado la oferta. Intercambio rechazado.", recipient)
                else:
                    broadcast(f"{name}: {message}\n")
                    print(f"{name}: {message}")
        except Exception as e:
            print(f"[ERROR] Error al recibir mensaje: {e}")
            break

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print("[SERVER] Esperando conexiones...")

    while True:
        client, addr = server.accept()
        print(f"[SERVER] Cliente {addr} intentando conectarse.")
        name = client.recv(1024).decode("utf-8")
        if name in [client_name for _, client_name in clients]:
            print(f"[SERVER] Nombre '{name}' ya está en uso. Rechazando conexión.")
            client.send("[SERVER] Nombre ya en uso. Por favor, elige otro.\n".encode("utf-8"))
            client.close()
            continue
        print(f"[SERVER] Cliente {addr} conectado con nombre '{name}'.")
        client.send("[SERVER] Conexión exitosa. ¡Bienvenid@!\n".encode("utf-8"))

        with mutex:
            clients.append((client, name))

        client_thread = threading.Thread(target=handle_client, args=(client, name))
        client_thread.start()

if __name__ == "__main__":
    main()
