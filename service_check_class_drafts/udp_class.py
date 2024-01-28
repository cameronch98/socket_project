import shutil
import socket
from datetime import datetime


class UDP:
    def __init__(self, ip_address: str, port: int, timeout: int = 3, interval: int = 60):
        """
        Initialize a UDP service object for use in UDP service checks
        :param ip_address: The IP address of the target server.
        :param port: The UDP port number to check.
        :param timeout: The timeout duration in seconds for the socket operation.
        :param interval: How often to run UDP service checks in seconds.
        """
        self.ip_address = ip_address
        self.port = port
        self.timeout = timeout
        self.interval = interval

    def udp_service_check(self, lock, event):
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
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] UDP Service Check")
                print("=" * columns)

                # TCP test
                print(f"Testing UDP to Server {self.ip_address} at Port {self.port} ... ")
                udp_port_status, udp_port_description = check_udp_port(self.ip_address, self.port)
                print(
                    f"Server: {self.ip_address}, UDP Port: {self.port}, UDP Port Status: {udp_port_status}, Description: {udp_port_description}")

            finally:
                # Release lock
                lock.release()

            # Sleep the loop for the given interval
            event.wait(self.interval)


def check_udp_port(ip_address: str, port: int, timeout: int = 3) -> (bool, str):
    """
    Checks the status of a specific UDP port on a given IP address.

    Args:
    ip_address (str): The IP address of the target server.
    port (int): The UDP port number to check.
    timeout (int): The timeout duration in seconds for the socket operation. Default is 3 seconds.

    Returns:
    tuple: A tuple containing a boolean and a string.
           The boolean is True if the port is open (or if the status is uncertain), False if the port is definitely closed.
           The string provides a description of the port status.

    Description:
    This function attempts to send a UDP packet to the specified port on the given IP address.
    Since UDP is a connectionless protocol, the function can't definitively determine if the port is open.
    It can only confirm if the port is closed, typically indicated by an ICMP 'Destination Unreachable' response.
    """

    try:
        # Create a socket object using the AF_INET address family (IPv4) and SOCK_DGRAM socket type (UDP).
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Set a timeout for the socket to avoid waiting indefinitely.
            s.settimeout(timeout)

            # Send a dummy packet to the specified IP address and port.
            # As UDP is connectionless, this does not establish a connection but merely sends the packet.
            s.sendto(b'', (ip_address, port))

            try:
                # Try to receive data from the socket.
                # If an ICMP 'Destination Unreachable' message is received, the port is considered closed.
                s.recvfrom(1024)
                return False, f"Port {port} on {ip_address} is closed."

            except socket.timeout:
                # If a timeout occurs, it's uncertain whether the port is open or closed, as no response is received.
                return True, f"Port {port} on {ip_address} is open or no response received."

    except Exception as e:
        # Catch any other exceptions and return a general failure message along with the exception raised.
        return False, f"Failed to check UDP port {port} on {ip_address} due to an error: {e}"