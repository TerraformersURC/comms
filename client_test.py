import socket

def send_message(ip, port, message):
    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Connect to the server
    sock.connect((ip, port))
    
    try:
        # Send data
        sock.sendall(message.encode())
        print(f"Sent: {message}")
    finally:
        # Close the socket
        sock.close()

if __name__ == '__main__':
    send_message('192.168.1.10', 12345, 'Hello, my name is Terry!')  # Destination IP, port, and message
