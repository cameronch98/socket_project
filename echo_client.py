import socket
import time


def tcp_client():
    """
    TCP client for testing included local echo server. Will prompt user for echo message and display the sent and
    received messages to confirm the echo is working properly. Will also display additional status information
    pertaining to the port being open, or if there is an issue with the TCP connection. Connection will be closed
    when the user sends the message "Goodbye".
    :return: None
    """
    # Create an IPv4 sock stream socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Define target address and port
    server_address = '127.0.0.1'
    server_port = 12345

    try:
        # Connect to server at specified port
        sock.connect((server_address, server_port))
        print(f"Port {server_port} on {server_address} is open.")

        # Loop until user sends goodbye message
        while True:

            # Get a random lorem ipsum sentence
            message = input("Enter your echo message: ")

            # Send message
            if message == "Goodbye":
                print(f"Sending termination message to {(server_address, server_port)} ... ")
                sock.sendall(message.encode())
                break
            else:
                print(f"\nSending echo request message: {message}")
                sock.sendall(message.encode())

            # Receive message
            reply = sock.recv(1024).decode()
            print(f"Received echo reply message: {reply}\n")

    finally:
        # Close TCP connection
        sock.close()
        print(f"Connection to {(server_address, server_port)} is closed.")


if __name__ == "__main__":
    tcp_client()
