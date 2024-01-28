import os
import random
import shutil
import socket
import string
import struct
import threading
import time
import zlib
from datetime import datetime
from typing import Tuple, Any


class ICMP:
    def __init__(self, host: str, ttl: int = 64, timeout: int = 1, sequence_number: int = 1, max_hops: int = 30,
                 pings_per_hop: int = 1, verbose: bool = False, interval: int = 60):
        """
        Initialize ICMP service object with parameters for use in ping and traceroute
        :param host: The IP address or hostname of the target host.
        :param ttl: Time-to-Live for the ICMP packet. Determines how many hops (routers) the packet can pass through.
        :param timeout: The time in seconds that the function will wait for a reply before giving up.
        :param sequence_number: The sequence number for the ICMP packet. Useful for matching requests with replies.
        :param max_hops: Maximum number of hops to try before stopping.
        :param pings_per_hop: Number of pings to perform at each hop.
        :param verbose: If True, print additional details during execution.
        :param interval: How often to run icmp service checks in seconds.
        """
        # Host name
        self.host = host

        # Ping parameters
        self.ttl = ttl
        self.timeout = timeout
        self.sequence_number = sequence_number

        # Traceroute parameters
        self.max_hops = max_hops
        self.pings_per_hop = pings_per_hop
        self.verbose = verbose

        # Service check frequency
        self.interval = interval

    def icmp_service_check(self, lock, event):
        """
        Runs icmp service check on timer set by interval variable
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
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ICMP Service Check")
                print("=" * columns)

                # Ping Test
                print("Ping Test:")
                ping_addr, ping_time = ping(self.host, self.ttl, self.timeout, self.sequence_number)
                if ping_addr and ping_time:
                    print(f"{self.host} (ping): {ping_addr[0]} - {ping_time:.2f} ms")
                else:
                    print(f"{self.host} (ping): Request timed out or no reply received")

                # Traceroute Test
                print("\nTraceroute Test:")
                print(f"{self.host} (traceroute):")
                print(traceroute(self.host, self.max_hops, self.pings_per_hop, self.verbose))

            finally:
                # Release lock
                lock.release()

            # Sleep the loop for the given interval
            event.wait(self.interval)


def calculate_icmp_checksum(data: bytes) -> int:
    """
    Calculate the checksum for the ICMP packet.

    The checksum is calculated by summing the 16-bit words of the entire packet,
    carrying any overflow bits around, and then complementing the result.

    Args:
    data (bytes): The data for which the checksum is to be calculated.

    Returns:
    int: The calculated checksum.
    """

    s: int = 0  # Initialize the sum to 0.

    # Iterate over the data in 16-bit (2-byte) chunks.
    for i in range(0, len(data), 2):
        # Combine two adjacent bytes (8-bits each) into one 16-bit word.
        # data[i] is the high byte, shifted left by 8 bits.
        # data[i + 1] is the low byte, added to the high byte.
        # This forms one 16-bit word for each pair of bytes.
        w: int = (data[i] << 8) + (data[i + 1])
        s += w  # Add the 16-bit word to the sum.

    # Add the overflow back into the sum.
    # If the sum is larger than 16 bits, the overflow will be in the higher bits.
    # (s >> 16) extracts the overflow by shifting right by 16 bits.
    # (s & 0xffff) keeps only the lower 16 bits of the sum.
    # The two parts are then added together.
    s = (s >> 16) + (s & 0xffff)

    # Complement the result.
    # ~s performs a bitwise complement (inverting all the bits).
    # & 0xffff ensures the result is a 16-bit value by masking the higher bits.
    s = ~s & 0xffff

    return s  # Return the calculated checksum.


def create_icmp_packet(icmp_type: int = 8, icmp_code: int = 0, sequence_number: int = 1, data_size: int = 192) -> bytes:
    """
    Creates an ICMP (Internet Control Message Protocol) packet with specified parameters.

    Args:
    icmp_type (int): The type of the ICMP packet. Default is 8 (Echo Request).
    icmp_code (int): The code of the ICMP packet. Default is 0.
    sequence_number (int): The sequence number of the ICMP packet. Default is 1.
    data_size (int): The size of the data payload in the ICMP packet. Default is 192 bytes.

    Returns:
    bytes: A bytes object representing the complete ICMP packet.

    Description:
    The function generates a unique ICMP packet by combining the specified ICMP type, code, and sequence number
    with a data payload of a specified size. It calculates a checksum for the packet and ensures that the packet
    is in the correct format for network transmission.
    """

    # Get the current thread identifier and process identifier.
    # These are used to create a unique ICMP identifier.
    thread_id = threading.get_ident()
    process_id = os.getpid()

    # Generate a unique ICMP identifier using CRC32 over the concatenation of thread_id and process_id.
    # The & 0xffff ensures the result is within the range of an unsigned 16-bit integer (0-65535).
    icmp_id = zlib.crc32(f"{thread_id}{process_id}".encode()) & 0xffff

    # Pack the ICMP header fields into a bytes object.
    # 'bbHHh' is the format string for struct.pack, which means:
    # b - signed char (1 byte) for ICMP type
    # b - signed char (1 byte) for ICMP code
    # H - unsigned short (2 bytes) for checksum, initially set to 0
    # H - unsigned short (2 bytes) for ICMP identifier
    # h - short (2 bytes) for sequence number
    header: bytes = struct.pack('bbHHh', icmp_type, icmp_code, 0, icmp_id, sequence_number)

    # Create the data payload for the ICMP packet.
    # It's a sequence of a single randomly chosen alphanumeric character (uppercase or lowercase),
    # repeated to match the total length specified by data_size.
    random_char: str = random.choice(string.ascii_letters + string.digits)
    data: bytes = (random_char * data_size).encode()

    # Calculate the checksum of the header and data.
    chksum: int = calculate_icmp_checksum(header + data)

    # Repack the header with the correct checksum.
    # socket.htons ensures the checksum is in network byte order.
    header = struct.pack('bbHHh', icmp_type, icmp_code, socket.htons(chksum), icmp_id, sequence_number)

    # Return the complete ICMP packet by concatenating the header and data.
    return header + data


def ping(host: str, ttl: int = 64, timeout: int = 1, sequence_number: int = 1) -> Tuple[Any, float] | Tuple[Any, None]:
    """
    Send an ICMP Echo Request to a specified host and measure the round-trip time.

    This function creates a raw socket to send an ICMP Echo Request packet to the given host.
    It then waits for an Echo Reply, measuring the time taken for the round trip. If the
    specified timeout is exceeded before receiving a reply, the function returns None for the ping time.

    Args:
    host (str): The IP address or hostname of the target host.
    ttl (int): Time-To-Live for the ICMP packet. Determines how many hops (routers) the packet can pass through.
    timeout (int): The time in seconds that the function will wait for a reply before giving up.
    sequence_number (int): The sequence number for the ICMP packet. Useful for matching requests with replies.

    Returns:
    Tuple[Any, float] | Tuple[Any, None]: A tuple containing the address of the replier and the total ping time in milliseconds.
    If the request times out, the function returns None for the ping time. The address part of the tuple is also None if no reply is received.
    """

    # Create a raw socket with the Internet Protocol (IPv4) and ICMP.
    # socket.AF_INET specifies the IPv4 address family.
    # socket.SOCK_RAW allows sending raw packets (including ICMP).
    # socket.IPPROTO_ICMP specifies the ICMP protocol.
    with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as sock:
        # Set the Time-To-Live (TTL) for the ICMP packet.
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)

        # Set the timeout for the socket's blocking operations (e.g., recvfrom).
        sock.settimeout(timeout)

        # Create an ICMP Echo Request packet.
        # icmp_type=8 and icmp_code=0 are standard for Echo Request.
        # sequence_number is used to match Echo Requests with Replies.
        packet: bytes = create_icmp_packet(icmp_type=8, icmp_code=0, sequence_number=sequence_number)

        # Send the ICMP packet to the target host.
        # The second argument of sendto is a tuple (host, port).
        # For raw sockets, the port number is irrelevant, hence set to 1.
        sock.sendto(packet, (host, 1))

        # Record the current time to measure the round-trip time later.
        start: float = time.time()

        try:
            # Wait to receive data from the socket (up to 1024 bytes).
            # This will be the ICMP Echo Reply if the target host is reachable.
            data, addr = sock.recvfrom(1024)

            # Record the time when the reply is received.
            end: float = time.time()

            # Calculate the round-trip time in milliseconds.
            total_ping_time = (end - start) * 1000

            # Return the address of the replier and the total ping time.
            return addr, total_ping_time
        except socket.timeout:
            # If no reply is received within the timeout period, return None for the ping time.
            return None, None


def traceroute(host: str, max_hops: int = 30, pings_per_hop: int = 1, verbose: bool = False) -> str:
    """
    Perform a traceroute to the specified host, with multiple pings per hop.

    Args:
    host (str): The IP address or hostname of the target host.
    max_hops (int): Maximum number of hops to try before stopping.
    pings_per_hop (int): Number of pings to perform at each hop.
    verbose (bool): If True, print additional details during execution.

    Returns:
    str: The results of the traceroute, including statistics for each hop.
    """
    # Header row for the results. Each column is formatted for alignment and width.
    results = [f"{'Hop':>3} {'Address':<15} {'Min (ms)':>8}   {'Avg (ms)':>8}   {'Max (ms)':>8}   {'Count':>5}"]

    # Loop through each TTL (Time-To-Live) value from 1 to max_hops.
    for ttl in range(1, max_hops + 1):
        # Print verbose output if enabled.
        if verbose:
            print(f"pinging {host} with ttl: {ttl}")

        # List to store ping response times for the current TTL.
        ping_times = []

        # Perform pings_per_hop number of pings for the current TTL.
        for _ in range(pings_per_hop):
            # Ping the host with the current TTL and sequence number.
            # The sequence number is incremented with TTL for each ping.
            addr, response = ping(host, ttl=ttl, sequence_number=ttl)

            # If a response is received (not None), append it to ping_times.
            if response is not None:
                ping_times.append(response)

        # If there are valid ping responses, calculate and format the statistics.
        if ping_times:
            min_time = min(ping_times)  # Minimum ping time.
            avg_time = sum(ping_times) / len(ping_times)  # Average ping time.
            max_time = max(ping_times)  # Maximum ping time.
            count = len(ping_times)  # Count of successful pings.

            # Append the formatted results for this TTL to the results list.
            results.append(f"{ttl:>3} {addr[0] if addr else '*':<15} {min_time:>8.2f}ms {avg_time:>8.2f}ms {max_time:>8.2f}ms {count:>5}")
        else:
            # If no valid responses, append a row of asterisks and zero count.
            results.append(f"{ttl:>3} {'*':<15} {'*':>8}   {'*':>8}   {'*':>8}   {0:>5}")

        # Print the last entry in the results if verbose mode is enabled.
        if verbose and results:
            print(f"\tResult: {results[-1]}")

        # If the address of the response matches the target host, stop the traceroute.
        if addr and addr[0] == host:
            break

    # Join all results into a single string with newline separators and return.
    return '\n'.join(results)