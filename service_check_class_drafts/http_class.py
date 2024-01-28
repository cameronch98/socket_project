import shutil
from datetime import datetime
from typing import Tuple, Optional

import requests


class HTTP:
    def __init__(self, url: str, interval: int = 60):
        """
        Initialize HTTP service object for use in HTTP request service checks
        :param url: URL to send requests to.
        :param interval: How often to run HTTP service checks in seconds.
        """
        self.url = url
        self.interval = interval

    def http_service_check(self, lock, event):
        """
        Runs http service check on timer set by interval variable
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
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] HTTP Service Check")
                print("=" * columns)

                # HTTP Request
                print(f"Sending HTTP Request to {self.url} ... ")
                http_server_status, http_server_response_code = check_server_http(self.url)
                print(
                    f"HTTP URL: {self.url}, HTTP server status: {http_server_status}, Status Code: {http_server_response_code if http_server_response_code is not None else 'N/A'}")

            finally:
                # Release lock
                lock.release()

            # Sleep the loop for the given interval
            event.wait(self.interval)


def check_server_http(url: str) -> Tuple[bool, Optional[int]]:
    """
    Check if an HTTP server is up by making a request to the provided URL.

    This function attempts to connect to a web server using the specified URL.
    It returns a tuple containing a boolean indicating whether the server is up,
    and the HTTP status code returned by the server.

    :param url: URL of the server (including http://)
    :return: Tuple (True/False, status code)
             True if server is up (status code < 400), False otherwise
    """
    try:
        # Making a GET request to the server
        response: requests.Response = requests.get(url)

        # The HTTP status code is a number that indicates the outcome of the request.
        # Here, we consider status codes less than 400 as successful,
        # meaning the server is up and reachable.
        # Common successful status codes are 200 (OK), 301 (Moved Permanently), etc.
        is_up: bool = response.status_code < 400

        # Returning a tuple: (True/False, status code)
        # True if the server is up, False if an exception occurs (see except block)
        return is_up, response.status_code

    except requests.RequestException:
        # This block catches any exception that might occur during the request.
        # This includes network problems, invalid URL, etc.
        # If an exception occurs, we assume the server is down.
        # Returning False for the status, and None for the status code,
        # as we couldn't successfully connect to the server to get a status code.
        return False, None
