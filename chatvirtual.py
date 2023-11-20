import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, Entry, Button, END

class ChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.root = tk.Tk()
        self.root.title("Chat de Granjerxs")

        self.message_list = scrolledtext.ScrolledText(self.root, height=20, width=50)
        self.message_list.pack(padx=10, pady=10)

        self.name_entry = Entry(self.root, width=20)
        self.name_entry.pack(padx=10, pady=10)

        self.join_button = Button(self.root, text="Unirse al chat", command=self.join_chat)
        self.join_button.pack(padx=10, pady=10)

        self.input_entry = Entry(self.root, width=40)
        self.input_entry.pack(padx=10, pady=10)

        self.send_button = Button(self.root, text="Enviar", command=self.send_message)
        self.send_button.pack(padx=10, pady=10)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = None

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def join_chat(self):
        self.name = self.name_entry.get()
        if self.name:
            self.client_socket.connect((self.host, self.port))
            self.client_socket.send(self.name.encode("utf-8"))

            welcome_message = self.client_socket.recv(1024).decode("utf-8")
            self.display_message(welcome_message)

            self.name_entry.config(state="disabled")
            self.join_button.config(state="disabled")

            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.start()

    def display_message(self, message):
        self.message_list.insert(END, message + "\n")
        self.message_list.yview(END)

    def send_message(self):
        message = self.input_entry.get()
        if message:
            self.client_socket.send(message.encode("utf-8"))
            self.display_message(f"{self.name}: {message}")
            self.input_entry.delete(0, END)

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode("utf-8")
                if message:
                    if message.startswith("[SERVER]"):
                        self.display_message(message)
                    else:
                        self.display_message(message)
            except Exception as e:
                print(f"[ERROR] Error al recibir mensaje: {e}")
                break

    def on_closing(self):
        self.client_socket.send(":q".encode("utf-8"))
        self.client_socket.close()
        self.root.destroy()

if __name__ == "__main__":
    client = ChatClient('127.0.0.1', 55555)

