import random
import shutil
import socket
import time
from datetime import datetime

import lorem


class TCP:
    def __init__(self, ip_address: str, port: int, interval: int = 60):
        """
        Initialize a TCP service object for use in TCP service checks.
        :param ip_address: The IP address of the target server.
        :param port: The TCP port number to check.
        :param interval: How often to run TCP service checks in seconds.
        """
        self.ip_address = ip_address
        self.port = port
        self.interval = interval

    def tcp_service_check(self, lock, event):
        """
        Runs tcp service check on timer set by interval variable
        :param lock: thread lock to prevent overlapping output
        :param event: event to trigger killing thread
        :return: None
        """
        # Loop until thread event is set
        while not event.is_set():

            # Set lock
            lock.acquire()
            try:
                # Header
                columns, lines = shutil.get_terminal_size()
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] TCP Service Check")
                print("=" * columns)

                # TCP test
                print(f"Testing TCP to Server {self.ip_address} at Port {self.port} ... ")
                tcp_port_status, tcp_port_description = check_tcp_port(self.ip_address, self.port)
                print(f"Server: {self.ip_address}, TCP Port: {self.port}, TCP Port Status: {tcp_port_status}, Description: {tcp_port_description}")

            finally:
                # Release lock
                lock.release()

            # Sleep the loop for the given interval
            event.wait(self.interval)

    def local_tcp_service_check(self, lock, event):
        """
        Runs local tcp service check on timer set by interval variable
        :param lock: thread lock to prevent overlapping output
        :param event: event to trigger killing thread
        :return: None
        """
        # Loop until thread event is set
        while not event.is_set():

            # Set lock
            lock.acquire()
            try:
                # Header
                columns, lines = shutil.get_terminal_size()
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Local TCP Service Check")
                print("=" * columns)

                # TCP test
                print(f"Testing TCP to Local Server {self.ip_address} at Port {self.port} ... ")
                local_tcp_echo(self.ip_address, self.port)

            finally:
                # Release lock
                lock.release()

            # Sleep the loop for the given interval
            event.wait(self.interval)


def check_tcp_port(ip_address: str, port: int) -> (bool, str):
    """
    Checks the status of a specific TCP port on a given IP address.

    Args:
    ip_address (str): The IP address of the target server.
    port (int): The TCP port number to check.

    Returns:
    tuple: A tuple containing a boolean and a string.
           The boolean is True if the port is open, False otherwise.
           The string provides a description of the port status.

    Description:
    This function attempts to establish a TCP connection to the specified port on the given IP address.
    If the connection is successful, it means the port is open; otherwise, the port is considered closed or unreachable.
    """

    try:
        # Create a socket object using the AF_INET address family (IPv4) and SOCK_STREAM socket type (TCP).
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Set a timeout for the socket to avoid waiting indefinitely. Here, 3 seconds is used as a reasonable timeout duration.
            s.settimeout(3)

            # Attempt to connect to the specified IP address and port.
            # If the connection is successful, the port is open.
            s.connect((ip_address, port))
            return True, f"Port {port} on {ip_address} is open."

    except socket.timeout:
        # If a timeout occurs, it means the connection attempt took too long, implying the port might be filtered or the server is slow to respond.
        return False, f"Port {port} on {ip_address} timed out."

    except socket.error:
        # If a socket error occurs, it generally means the port is closed or not reachable.
        return False, f"Port {port} on {ip_address} is closed or not reachable."

    except Exception as e:
        # Catch any other exceptions and return a general failure message along with the exception raised.
        return False, f"Failed to check port {port} on {ip_address} due to an error: {e}"


def local_tcp_echo(ip_address: str, port: int) -> (bool, str):
    """
    Adapted from check_tcp_status to test functionality of local TCP server.

    Args:
    ip_address (str): The IP address of the target server.
    port (int): The TCP port number to check.

    Returns: None

    Description:
    Checks the status of a specific TCP port on a given IP address. Then, sends message with a pair of random integers
    from 1 to 100 for the server to perform addition on. The server should send the result back to the client, allowing
    for easy verification of functionality.
    """

    try:
        # Create a socket object using the AF_INET address family (IPv4) and SOCK_STREAM socket type (TCP).
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Set a timeout for the socket to avoid waiting indefinitely.
            s.settimeout(3)

            # Attempt to connect to the specified IP address and port.
            # If the connection is successful, the port is open.
            s.connect((ip_address, port))
            print(f"Port {port} on {ip_address} is open.")

            # Test a small random number of messages
            for _ in range(random.randint(1, 3)):

                # Get a random lorem ipsum sentence
                message = lorem.sentence()

                # Send message
                print(f"\nSending echo request message: {message}")
                s.sendall(message.encode())

                # Receive message
                reply = s.recv(1024).decode()
                print(f"Received echo reply message: {reply}")

                # Short sleep
                time.sleep(1)

            # Send termination message
            s.sendall("Goodbye".encode())

    except socket.timeout:
        # Connection attempt took too long; port might be filtered or the server is slow to respond.
        print(f"Port {port} on {ip_address} timed out.")

    except socket.error:
        # If a socket error occurs, it generally means the port is closed or not reachable.
        print(f"Port {port} on {ip_address} is closed or not reachable.")

    except Exception as e:
        # Catch any other exceptions and return a general failure message along with the exception raised.
        print(f"Failed to check port {port} on {ip_address} due to an error: {e}")