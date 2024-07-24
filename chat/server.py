import socket
import select


class ChatServer:
    def __init__(self, port):
        self.server_socket = socket.socket()
        self.port = port
        self.clients = []

    def start(self):
        self.server_socket.bind(("localhost", self.port))
        self.server_socket.listen()
        self.server_socket.setblocking(False)
        while True:
            try:
                self.run_call()
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.server_socket.close()

    def run_call(self):
        # Use select to wait for incoming connections or messages from clients
        readable, writable, errored = select.select([self.server_socket] + self.clients, [], [], 0)
        for sock in readable:
            if sock is self.server_socket:
                client_socket, address = self.server_socket.accept()
                print(f"Connected to {address}")
                client_socket.setblocking(False)
                self.clients.append(client_socket)

            else:
                try:
                    header = sock.recv(4)
                except ConnectionResetError:
                    print(f"sock {sock} disconnected")
                    self.clients.remove(sock)
                    continue
                if not header:
                    continue
                msg_len = int.from_bytes(header, byteorder="big")
                msg = sock.recv(msg_len).decode("utf-8")
                print(f"Received message from {str(sock)}: {msg}")

                # Broadcast message to all other clients
                for client in self.clients:
                    if client != sock:
                        client.sendall(header + msg.encode("utf-8"))

        # Remove any closed connections
        self.clients = [sock for sock in self.clients if sock.fileno() != -1]
