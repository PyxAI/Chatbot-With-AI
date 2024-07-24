import socket
import threading
import queue
from retrying import retry

MIN_SOCKETS = 2


class ChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket()
        self.connect(host, port)
        self.enter_message_prompt = "Enter a message>> "

    def start(self):
        try:
            # Create a thread for receiving messages from the server
            self.recv_thread = threading.Thread(target=self.receive_messages)
            self.recv_thread.start()
            self.snd_thread = threading.Thread(target=self.send_messages)
            self.snd_thread.start()
        except Exception as e:
            self.close()

    @retry(wait_fixed=3000)
    def connect(self, host, port):
        try:
            self.socket.connect((host, port))
        except ConnectionError as err:
            print("Connection error, retrying...\n")
            raise err
        print("Connected!")

    def close(self):
        self.socket.close()
        import sys
        sys.exit()

    def send_messages(self):
        while True:
            message = input(self.enter_message_prompt)
            if message == "quit":
                self.close()
            header = len(message).to_bytes(4, byteorder="big")
            self.socket.sendall(header + message.encode("utf-8"))

    def send_single_message(self, message):
        header = len(message).to_bytes(4, byteorder="big")
        self.socket.sendall(header + message.encode("utf-8"))

    def receive_messages(self):
        while True:
            # Receive message from server
            header = self.socket.recv(4)
            if not header:
                break
            msg_len = int.from_bytes(header, byteorder="big")
            msg = self.socket.recv(msg_len).decode("utf-8")
            print(f"\nReceived message: {msg}\n{self.enter_message_prompt}")
