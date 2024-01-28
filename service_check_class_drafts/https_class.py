import shutil
from datetime import datetime
from typing import Tuple, Optional

import requests


class HTTPS:
    def __init__(self, url: str, timeout: int = 5, interval: int = 60):
        """
        Initialize HTTPS service object for use in HTTPS request service checks
        :param url: URL to send requests to.
        :param timeout: Timeout for the request in seconds. Default is 5 seconds.
        :param interval: How often to run HTTPS service checks in seconds.
        """
        self.url = url
        self.timeout = timeout
        self.interval = interval

    def https_service_check(self, lock, event):
        """
        Runs https service check on timer set by interval variable
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
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] HTTPS Service Check")
                print("=" * columns)

                # HTTP Request
                print(f"Sending HTTPS Request to {self.url} ... ")
                https_server_status, https_server_response_code, description = check_server_https(self.url)
                print(
                    f"HTTP URL: {self.url}, HTTP server status: {https_server_status}, Status Code: {https_server_response_code if https_server_response_code is not None else 'N/A'}, Description: {description}")

            finally:
                # Release lock
                lock.release()

            # Sleep the loop for the given interval
            event.wait(self.interval)


def check_server_https(url: str, timeout: int = 5) -> Tuple[bool, Optional[int], str]:
    """
    Check if an HTTPS server is up by making a request to the provided URL.

    This function attempts to connect to a web server using the specified URL with HTTPS.
    It returns a tuple containing a boolean indicating whether the server is up,
    the HTTP status code returned by the server, and a descriptive message.

    :param url: URL of the server (including https://)
    :param timeout: Timeout for the request in seconds. Default is 5 seconds.
    :return: Tuple (True/False for server status, status code, description)
    """
    try:
        # Setting custom headers for the request. Here, 'User-Agent' is set to mimic a web browser.
        headers: dict = {'User-Agent': 'Mozilla/5.0'}

        # Making a GET request to the server with the specified URL and timeout.
        # The timeout ensures that the request does not hang indefinitely.
        response: requests.Response = requests.get(url, headers=headers, timeout=timeout)

        # Checking if the status code is less than 400. Status codes in the 200-399 range generally indicate success.
        is_up: bool = response.status_code < 400

        # Returning a tuple: (server status, status code, descriptive message)
        return is_up, response.status_code, "Server is up"

    except requests.ConnectionError:
        # This exception is raised for network-related errors, like DNS failure or refused connection.
        return False, None, "Connection error"

    except requests.Timeout:
        # This exception is raised if the server does not send any data in the allotted time (specified by timeout).
        return False, None, "Timeout occurred"

    except requests.RequestException as e:
        # A catch-all exception for any error not covered by the specific exceptions above.
        # 'e' contains the details of the exception.
        return False, None, f"Error during request: {e}"