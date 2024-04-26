import socket

def start_server(ip, port):
    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Bind the socket to the address and port
    sock.bind((ip, port))
    
    # Start listening for incoming connections
    sock.listen(1)
    print(f"Listening on {ip}:{port}")

    # Accept a connection
    connection, address = sock.accept()
    print(f"Connected by {address}")

    try:
        while True:
            # Receive data from the client
            data = connection.recv(1024)
            if not data:
                break  # No more data from client, exit loop
            print("Received:", data.decode())
    finally:
        # Close the connection
        connection.close()

if __name__ == '__main__':
    start_server('192.168.1.14', 12346)  # Listening IP and port
