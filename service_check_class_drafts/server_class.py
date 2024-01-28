import threading
from service_check_class_drafts.icmp_class import ICMP
from service_check_class_drafts.http_class import HTTP
from service_check_class_drafts.https_class import HTTPS
from service_check_class_drafts.dns_class import DNS
from service_check_class_drafts.ntp_class import NTP
from tcp_class import TCP
from udp_class import UDP


class Server:

    def __init__(self, server):
        """
        Initialize a server object with domain or ip address and dictionary for services
        :param server: name of the server; domain or ip address
        """
        self.server = server
        self.services = {}
        self.thread_list = []
        self.event = threading.Event()
        self.lock = threading.Lock()

    def add_service(self, protocol, protocol_object):
        """
        Add a service to the server
        :param protocol: name of the protocol to be added as a service
        :param protocol_object: the corresponding protocol object
        :return: None
        """
        self.services[protocol] = protocol_object

    def delete_service(self, protocol):
        """
        Delete a service from the server
        :param protocol: name of the protocol to be deleted
        :return: None
        """
        del self.services[protocol]

    def initialize_threads(self):
        """Initializes necessary threads for the service checks of a particular server"""

        # Map protocols to their service checks
        service_check_map = {
            'ICMP': ICMP.icmp_service_check,
            'HTTP': HTTP.http_service_check,
            'HTTPS': HTTPS.https_service_check,
            'NTP': NTP.ntp_service_check,
            'DNS': DNS.dns_service_check,
            'TCP': TCP.tcp_service_check,
            'UDP': UDP.udp_service_check,
            'LOCAL TCP': TCP.local_tcp_service_check
        }

        # Start service check threads and add them to list
        for protocol in list(self.services.keys()):
            thread = threading.Thread(target=service_check_map[protocol], args=(self.lock, self.event))
            thread.start()
            self.thread_list.append(thread)

    def kill_threads(self):
        """Kill the threads running service checks for the server"""

        # Set event and wait for all threads to quit
        self.event.set()
        for thread in self.thread_list:
            thread.join()

