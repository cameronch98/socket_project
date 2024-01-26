class ICMP:
    def __init__(self, host: str, ttl: int = 64, timeout: int = 1, sequence_number: int = 1,
                 max_hops: int = 30, pings_per_hop: int = 1, verbose: bool = False):
        # Ping and Traceroute
        self.host = host

        # Ping parameters
        self.ttl = ttl
        self.timeout = timeout
        self.sequence_number = sequence_number

        # Traceroute parameters
        self.max_hops = max_hops
        self.pings_per_hop = pings_per_hop
        self.verbose = verbose


class HTTP:
    def __init__(self, url: str):
        self.url = url


class HTTPS:
    def __init__(self, url: str, timeout: int = 5):
        self.url = url
        self.timeout = timeout


class NTP:
    def __init__(self, server: str):
        self.server = server


class DNS:
    def __init__(self, server, query, record_type):
        self.server = server
        self.query = query
        self.record_type = record_type


class TCP:
    def __init__(self, ip_address: str, port: int):
        self.ip_address = ip_address
        self.port = port


class UDP:
    def __init__(self, ip_address: str, port: int, timeout: int = 3):
        self.ip_address = ip_address
        self.port = port
        self.timeout = timeout


