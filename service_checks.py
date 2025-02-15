import shutil
from datetime import datetime
from network_tests import *


def icmp_service_check(server_dict, server, lock, event):
    """
    Runs icmp service check on timer set by interval variable
    :param server_dict: dictionary with server and service information
    :param server: server the program is currently monitoring
    :param lock: thread lock to prevent overlapping output
    :param event: event to trigger killing thread
    :return: None
    """
    # Extract variables
    ttl = server_dict[server]["ICMP"]['ttl']
    timeout = server_dict[server]["ICMP"]['timeout']
    sequence_number = server_dict[server]["ICMP"]['sequence_number']
    max_hops = server_dict[server]["ICMP"]['max_hops']
    pings_per_hop = server_dict[server]["ICMP"]['pings_per_hop']
    verbose = server_dict[server]["ICMP"]['verbose']
    interval = server_dict[server]["ICMP"]["interval"]

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
            ping_addr, ping_time = ping(server, ttl, timeout, sequence_number)
            if ping_addr and ping_time:
                print(f"{server} (ping): {ping_addr[0]} - {ping_time:.2f} ms")
            else:
                print(f"{server} (ping): Request timed out or no reply received")

            # Traceroute Test
            print("\nTraceroute Test:")
            print(f"{server} (traceroute):")
            print(traceroute(server, max_hops, pings_per_hop, verbose))

        finally:
            # Release lock
            lock.release()

        # Sleep the loop for the given interval
        event.wait(interval)


def http_service_check(server_dict, server, lock, event):
    """
    Runs http service check on timer set by interval variable
    :param server_dict: dictionary with server and service information
    :param server: server the program is currently monitoring
    :param lock: thread lock to prevent overlapping output
    :param event: event to trigger killing thread
    :return: None
    """
    # Extract variables
    http_url = server_dict[server]["HTTP"]["url"]
    interval = server_dict[server]["HTTP"]["interval"]

    # Loop until thread event is set
    while not event.is_set():

        # Set lock
        lock.acquire()
        try:
            # Header
            columns, lines = shutil.get_terminal_size()
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] HTTP Service Check")
            print("=" * columns)

            # HTTP Request
            print(f"Sending HTTP Request to {server} ... ")
            http_server_status, http_server_response_code = check_server_http(http_url)
            print(f"HTTP URL: {http_url}, HTTP server status: {http_server_status}, Status Code: {http_server_response_code if http_server_response_code is not None else 'N/A'}")

        finally:
            # Release lock
            lock.release()

        # Sleep the loop for the given interval
        event.wait(interval)


def https_service_check(server_dict, server, lock, event):
    """
    Runs https service check on timer set by interval variable
    :param server_dict: dictionary with server and service information
    :param server: server the program is currently monitoring
    :param lock: thread lock to prevent overlapping output
    :param event: event to trigger killing thread
    :return: None
    """
    # Extract variables
    https_url = server_dict[server]["HTTPS"]["url"]
    timeout = server_dict[server]["HTTPS"]["timeout"]
    interval = server_dict[server]["HTTPS"]["interval"]

    # Loop until thread event is set
    while not event.is_set():

        # Set lock
        lock.acquire()
        try:
            # Header
            columns, lines = shutil.get_terminal_size()
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] HTTPS Service Check")
            print("=" * columns)

            # HTTP Request
            print(f"Sending HTTPS Request to {server} ... ")
            https_server_status, https_server_response_code, description = check_server_https(https_url, timeout)
            print(f"HTTP URL: {https_url}, HTTP server status: {https_server_status}, Status Code: {https_server_response_code if https_server_response_code is not None else 'N/A'}, Description: {description}")

        finally:
            # Release lock
            lock.release()

        # Sleep the loop for the given interval
        event.wait(interval)


def ntp_service_check(server_dict, server, lock, event):
    """
    Runs ntp service check on timer set by interval variable
    :param server_dict: dictionary with server and service information
    :param server: server the program is currently monitoring
    :param lock: thread lock to prevent overlapping output
    :param event: event to trigger killing thread
    :return: None
    """
    # Extract variables
    interval = server_dict[server]["NTP"]["interval"]

    # Loop until thread event is set
    while not event.is_set():

        # Set lock
        lock.acquire()
        try:
            # Header
            columns, lines = shutil.get_terminal_size()
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] NTP Service Check")
            print("=" * columns)

            # NTP Test
            print(f"Testing Status of NTP Server {server} ... ")
            ntp_server_status, ntp_server_time = check_ntp_server(server)
            print(f"{server} is up. Time: {ntp_server_time}" if ntp_server_status else f"{server} is down.")

        finally:
            # Release lock
            lock.release()

        # Sleep the loop for the given interval
        event.wait(interval)


def dns_service_check(server_dict, server, lock, event):
    """
    Runs dns service check on timer set by interval variable
    :param server_dict: dictionary with server and service information
    :param server: server the program is currently monitoring
    :param lock: thread lock to prevent overlapping output
    :param event: event to trigger killing thread
    :return: None
    """
    # Extract variables
    dns_server = server_dict[server]["DNS"]["dns_server"]
    query = server_dict[server]["DNS"]["query"]
    record_types = server_dict[server]["DNS"]["record_types"]
    interval = server_dict[server]["DNS"]["interval"]

    # Loop until thread event is set
    while not event.is_set():

        # Set lock
        lock.acquire()
        try:
            # Header
            columns, lines = shutil.get_terminal_size()
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] DNS Service Check")
            print("=" * columns)

            # DNS Test
            print(f"Querying DNS Server {dns_server} with Server {query} ... ")
            for dns_record_type in record_types:
                dns_server_status, dns_query_results = check_dns_server_status(dns_server, query, dns_record_type)
                print(f"DNS Server: {dns_server}, Status: {dns_server_status}, {dns_record_type} Records Results: {dns_query_results}")

        finally:
            # Release lock
            lock.release()

        # Sleep the loop for the given interval
        event.wait(interval)


def tcp_service_check(server_dict, server, lock, event):
    """
    Runs tcp service check on timer set by interval variable
    :param server_dict: dictionary with server and service information
    :param server: server the program is currently monitoring
    :param lock: thread lock to prevent overlapping output
    :param event: event to trigger killing thread
    :return: None
    """
    # Extract variables
    port = server_dict[server]["TCP"]["port"]
    interval = server_dict[server]["TCP"]["interval"]

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
            print(f"Testing TCP to Server {server} at Port {port} ... ")
            tcp_port_status, tcp_port_description = check_tcp_port(server, port)
            print(f"Server: {server}, TCP Port: {port}, TCP Port Status: {tcp_port_status}, Description: {tcp_port_description}")

        finally:
            # Release lock
            lock.release()

        # Sleep the loop for the given interval
        event.wait(interval)


def udp_service_check(server_dict, server, lock, event):
    """
    Runs tcp service check on timer set by interval variable
    :param server_dict: dictionary with server and service information
    :param server: server the program is currently monitoring
    :param lock: thread lock to prevent overlapping output
    :param event: event to trigger killing thread
    :return: None
    """
    # Extract variables
    port = server_dict[server]["UDP"]["port"]
    timeout = server_dict[server]["UDP"]["timeout"]
    interval = server_dict[server]["UDP"]["interval"]

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
            print(f"Testing UDP to Server {server} at Port {port} ... ")
            udp_port_status, udp_port_description = check_udp_port(server, port, timeout)
            print(f"Server: {server}, UDP Port: {port}, UDP Port Status: {udp_port_status}, Description: {udp_port_description}")

        finally:
            # Release lock
            lock.release()

        # Sleep the loop for the given interval
        event.wait(interval)


def local_tcp_service_check(server_dict, server, lock, event):
    """
    Runs local tcp service check on timer set by interval variable
    :param server_dict: dictionary with server and service information
    :param server: server the program is currently monitoring
    :param lock: thread lock to prevent overlapping output
    :param event: event to trigger killing thread
    :return: None
    """
    # Extract variables
    interval = server_dict[server]["LOCAL TCP"]["interval"]
    port = server_dict[server]["LOCAL TCP"]["port"]

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
            print(f"Testing TCP to Local Server {server} at Port {port} ... ")
            local_tcp_echo(server, port)

        finally:
            # Release lock
            lock.release()

        # Sleep the loop for the given interval
        event.wait(interval)