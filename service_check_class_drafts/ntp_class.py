import shutil
from datetime import datetime
from socket import gaierror
from time import ctime
from typing import Tuple, Optional

import ntplib


class NTP:
    def __init__(self, server: str, interval: int = 60):
        """
        Initialize NTP service object for use in NTP service checks
        :param server: The IP address or hostname of the target host.
        :param interval: How often to run NTP service checks in seconds.
        """
        self.server = server
        self.interval = interval

    def ntp_service_check(self, lock, event):
        """
        Runs ntp service check on timer set by interval variable
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
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] NTP Service Check")
                print("=" * columns)

                # NTP Test
                print(f"Testing Status of NTP Server {self.server} ... ")
                ntp_server_status, ntp_server_time = check_ntp_server(self.server)
                print(f"{self.server} is up. Time: {ntp_server_time}" if ntp_server_status else f"{self.server} is down.")

            finally:
                # Release lock
                lock.release()

            # Sleep the loop for the given interval
            event.wait(self.interval)


def check_ntp_server(server: str) -> Tuple[bool, Optional[str]]:
    """
    Checks if an NTP server is up and returns its status and time.

    Args:
    server (str): The hostname or IP address of the NTP server to check.

    Returns:
    Tuple[bool, Optional[str]]: A tuple containing a boolean indicating the server status
                                 (True if up, False if down) and the current time as a string
                                 if the server is up, or None if it's down.
    """
    # Create an NTP client instance
    client = ntplib.NTPClient()

    try:
        # Request time from the NTP server
        # 'version=3' specifies the NTP version to use for the request
        response = client.request(server, version=3)

        # If request is successful, return True and the server time
        # 'ctime' converts the time in seconds since the epoch to a readable format
        return True, ctime(response.tx_time)
    except (ntplib.NTPException, gaierror):
        # If an exception occurs (server is down or unreachable), return False and None
        return False, None
