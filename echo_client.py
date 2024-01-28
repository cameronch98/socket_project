import socket
import time


def tcp_client():
    # Create an IPv4 sock stream socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Define target address and port
    server_address = '127.0.0.1'
    server_port = 12345

    try:
        # Connect to server at specified port
        sock.connect((server_address, server_port))
        print(f"Port {server_port} on {server_address} is open.")

        # Get a random lorem ipsum sentence
        message = input("Enter your echo message: ")

        # Send message
        print(f"\nSending echo request message: {message}")
        sock.sendall(message.encode())

        # Receive message
        reply = sock.recv(1024).decode()
        print(f"Received echo reply message: {reply}\n")

        # Short sleep
        time.sleep(2)

        # Send termination message
        sock.sendall("Goodbye".encode())

    finally:
        # Close TCP connection
        sock.close()


if __name__ == "__main__":
    tcp_client()
