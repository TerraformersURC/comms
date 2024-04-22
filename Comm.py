import socket

class Comm:

    def __init__(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sock.connect((ip, port))

        try:
            self.sock.connect((ip, port))
        except socket.error as err:
            print(f"Error connecting to {ip}:{port}: {err}")
            self.sock.close()

    def send(self, message):
        try:
            # Send data
            self.sock.sendall(message.encode())
            print(f"Sent: {message}")
        except:
            print('Error sending message: {err}')
        finally:
            # Close the socket
            self.sock.close()

    def receive(self):
        try:
            # Receive data (assuming a maximum message size of 1024 bytes)
            received_data = self.sock.recv(1024)

            # Decode the received data (assuming UTF-8 encoding)
            message = received_data.decode()

            print(f"Received message: {message}")

        except socket.error as err:
            print(f"Error receiving message: {err}")

        finally:
            # Close the socket
            self.sock.close()


