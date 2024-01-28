import shutil
import socket
from datetime import datetime

import dns_class.exception
import dns_class.resolver


class DNS:
    def __init__(self, server: str, query: str, record_types: list, interval: int = 60):
        """
        Initialize DNS service object for use in DNS service checks
        :param server: DNS server name or IP address
        :param query: Domain name to query
        :param record_types: Types of DNS records to test
        :param interval: How often to run DNS service checks in seconds
        """
        self.server = server
        self.query = query
        self.record_types = record_types
        self.interval = interval

    def dns_service_check(self, lock, event):
        """
        Runs dns service check on timer set by interval variable
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
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] DNS Service Check")
                print("=" * columns)

                # DNS Test
                print(f"Querying DNS Server {self.server} with Server {self.query} ... ")
                for record_type in self.record_types:
                    dns_server_status, dns_query_results = check_dns_server_status(self.server, self.query, record_type)
                    print(
                        f"DNS Server: {self.server}, Status: {dns_server_status}, {record_type} Records Results: {dns_query_results}")

            finally:
                # Release lock
                lock.release()

            # Sleep the loop for the given interval
            event.wait(self.interval)


def check_dns_server_status(server, query, record_type) -> (bool, str):
    """
    Check if a DNS server is up and return the DNS query results for a specified domain and record type.
    :param server: DNS server name or IP address
    :param query: Domain name to query
    :param record_type: Type of DNS record (e.g., 'A', 'AAAA', 'MX', 'CNAME')
    :return: Tuple (status, query_results)
    """
    try:
        # Set the DNS resolver to use the specified server
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [socket.gethostbyname(server)]

        # Perform a DNS query for the specified domain and record type
        query_results = resolver.resolve(query, record_type)
        results = [str(rdata) for rdata in query_results]

        return True, results

    except (dns.exception.Timeout, dns.resolver.NoNameservers, dns.resolver.NoAnswer, socket.gaierror) as e:
        # Return False if there's an exception (server down, query failed, or record type not found)
        return False, str(e)
    