import json
import threading
import time
from network_monitoring_examples import *
from typing import Callable, Union
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.patch_stdout import patch_stdout


def show_commands():
    """
    Show available commands
    :return: None
    """
    print("Commands:")
    print("  add - Add a new server to monitor")
    print("  edit - Edit an existing server")
    print("  delete - Delete an existing server")
    print("  show-servers - Show config of all servers")
    print("  monitor - Monitor a server")
    print("  monitor-all - Monitor all servers")
    print("  exit - Exit the application\n")


def show_services(services):
    """
    Show available services
    :return: None
    """
    # Print services
    print("Services: ")
    for i in range(len(services)):
        print(f"{services[i] : <10}", end="")
        if i == 3:
            print("")
    print("")


def show_server_configs(server_dict):
    """
    Show current servers and services they are
    registered to monitor.
    :return: None
    """
    print("")
    for server in server_dict:
        print(f"Server: {server}")
        print(f"Services: {', '.join(server_dict[server].keys())}")
        print("")


def icmp_service_check(server_dict, server, event):
    """
    Runs icmp service check on timer set by interval variable
    :param server_dict: dictionary with server and service information
    :param server: server the program is currently monitoring
    :param event: event to trigger killing thread
    :return: None
    """
    # Extract variables
    interval = server_dict[server]["ICMP"]["interval"]

    # Loop until thread event is set
    while not event.is_set():

        # Header
        print("\nICMP Service Check")
        print("--------------------------------------------------------------------")

        # Ping Test
        print("Ping Test:")
        ping_addr, ping_time = ping(server)
        if ping_addr and ping_time:
            print(f"{server} (ping): {ping_addr[0]} - {ping_time:.2f} ms")
        else:
            print(f"{server} (ping): Request timed out or no reply received")

        # Traceroute Test
        print("\nTraceroute Test:")
        print(f"{server} (traceroute):")
        print(traceroute(server))

        # Sleep the loop for the given interval
        event.wait(interval)


def http_service_check(server_dict, server, event):
    """
    Runs http service check on timer set by interval variable
    :param server_dict: dictionary with server and service information
    :param server: server the program is currently monitoring
    :param event: event to trigger killing thread
    :return: None
    """
    # Extract variables
    interval = server_dict[server]["HTTP"]["interval"]
    http_url = server_dict[server]["HTTP"]["url"]

    # Loop until thread event is set
    while not event.is_set():

        # Header
        print("\nHTTP Service Check")
        print("--------------------------------------------------------------------")

        # HTTP Request
        print(f"Sending HTTP Request to {server} ... ")
        http_server_status, http_server_response_code = check_server_http(http_url)
        print(f"HTTP URL: {http_url}, HTTP server status: {http_server_status}, Status Code: {http_server_response_code if http_server_response_code is not None else 'N/A'}")

        # Sleep the loop for the given interval
        event.wait(interval)


def https_service_check(server_dict, server, event):
    """
    Runs https service check on timer set by interval variable
    :param server_dict: dictionary with server and service information
    :param server: server the program is currently monitoring
    :param event: event to trigger killing thread
    :return: None
    """
    # Extract variables
    interval = server_dict[server]["HTTPS"]["interval"]
    https_url = server_dict[server]["HTTPS"]["url"]

    # Loop until thread event is set
    while not event.is_set():
        # Header
        print("\nHTTPS Service Check")
        print("--------------------------------------------------------------------")

        # HTTP Request
        print(f"Sending HTTPS Request to {server} ... ")
        https_server_status, https_server_response_code, description = check_server_https(https_url)
        print(f"HTTP URL: {https_url}, HTTP server status: {https_server_status}, Status Code: {https_server_response_code if https_server_response_code is not None else 'N/A'}, Description: {description}")

        # Sleep the loop for the given interval
        event.wait(interval)


def ntp_service_check(server_dict, server, event):
    """
    Runs ntp service check on timer set by interval variable
    :param server_dict: dictionary with server and service information
    :param server: server the program is currently monitoring
    :param event: event to trigger killing thread
    :return: None
    """
    # Extract variables
    interval = server_dict[server]["NTP"]["interval"]

    # Loop until thread event is set
    while not event.is_set():
        # Header
        print("\nNTP Service Check")
        print("--------------------------------------------------------------------")

        # NTP Test
        print(f"Testing Status of NTP Server {server} ... ")
        ntp_server_status, ntp_server_time = check_ntp_server(server)
        print(f"{server} is up. Time: {ntp_server_time}" if ntp_server_status else f"{server} is down.")

        # Sleep the loop for the given interval
        event.wait(interval)


def dns_service_check(server_dict, server, event):
    """
    Runs dns service check on timer set by interval variable
    :param server_dict: dictionary with server and service information
    :param server: server the program is currently monitoring
    :param event: event to trigger killing thread
    :return: None
    """
    # Extract variables
    interval = server_dict[server]["DNS"]["interval"]
    dns_server = server_dict[server]["DNS"]["dns_server"]
    query = server_dict[server]["DNS"]["query"]
    record_types = server_dict[server]["DNS"]["record_types"]

    # Loop until thread event is set
    while not event.is_set():

        # Header
        print("\nDNS Service Check")
        print("--------------------------------------------------------------------")

        # DNS Test
        print(f"Querying DNS Server {dns_server} with Server {query} ... ")
        for dns_record_type in record_types:
            dns_server_status, dns_query_results = check_dns_server_status(dns_server, query, dns_record_type)
            print(f"DNS Server: {dns_server}, Status: {dns_server_status}, {dns_record_type} Records Results: {dns_query_results}")

        # Sleep the loop for the given interval
        event.wait(interval)


def tcp_service_check(server_dict, server, event):
    """
    Runs tcp service check on timer set by interval variable
    :param server_dict: dictionary with server and service information
    :param server: server the program is currently monitoring
    :param event: event to trigger killing thread
    :return: None
    """
    # Extract variables
    interval = server_dict[server]["TCP"]["interval"]
    port = server_dict[server]["TCP"]["port"]

    # Loop until thread event is set
    while not event.is_set():

        # Header
        print("\nTCP Service Check")
        print("--------------------------------------------------------------------")

        # TCP test
        print(f"Testing TCP to Server {server} at Port {port} ... ")
        tcp_port_status, tcp_port_description = check_tcp_port(server, port)
        print(f"Server: {server}, TCP Port: {port}, TCP Port Status: {tcp_port_status}, Description: {tcp_port_description}")

        # Sleep the loop for the given interval
        event.wait(interval)


def udp_service_check(server_dict, server, event):
    """
    Runs tcp service check on timer set by interval variable
    :param server_dict: dictionary with server and service information
    :param server: server the program is currently monitoring
    :param event: event to trigger killing thread
    :return: None
    """
    # Extract variables
    interval = server_dict[server]["UDP"]["interval"]
    port = server_dict[server]["UDP"]["port"]

    # Loop until thread event is set
    while not event.is_set():

        # Header
        print("\nUDP Service Check")
        print("--------------------------------------------------------------------")

        # TCP test
        print(f"Testing UDP to Server {server} at Port {port} ... ")
        udp_port_status, udp_port_description = check_udp_port(server, port)
        print(f"Server: {server}, UDP Port: {port}, UDP Port Status: {udp_port_status}, Description: {udp_port_description}")

        # Sleep the loop for the given interval
        event.wait(interval)


def initialize_threads(server_dict, server, event, thread_list):
    """
    Initializes necessary threads for the service checks of a particular server
    :param server_dict: dictionary with server and service information
    :param server: server the program is currently monitoring
    :param event: event to trigger killing thread
    :param thread_list: list of currently running threads
    :return: None
    """
    # Get protocols for server
    service_checks = server_dict[server].keys()

    # Start icmp service check thread and add to list
    if 'ICMP' in service_checks:
        icmp_thread = threading.Thread(target=icmp_service_check, args=(server_dict, server, event))
        icmp_thread.start()
        thread_list.append(icmp_thread)
        time.sleep(3)  # Give time before next check starts

    # Start http service check thread and add to list
    if 'HTTP' in service_checks:
        http_thread = threading.Thread(target=http_service_check, args=(server_dict, server, event))
        http_thread.start()
        thread_list.append(http_thread)
        time.sleep(3)  # Give time before next check starts

    # Start https service check thread and add to list
    if 'HTTPS' in service_checks:
        https_thread = threading.Thread(target=https_service_check,
                                        args=(server_dict, server, event))
        https_thread.start()
        thread_list.append(https_thread)
        time.sleep(3)  # Give time before next check starts

    # Start ntp service check thread and add to list
    if 'NTP' in service_checks:
        ntp_thread = threading.Thread(target=ntp_service_check, args=(server_dict, server, event))
        ntp_thread.start()
        thread_list.append(ntp_thread)
        time.sleep(3)  # Give time before next check starts

    # Start dns service check thread and add to list
    if 'DNS' in service_checks:
        dns_thread = threading.Thread(target=dns_service_check, args=(server_dict, server, event))
        dns_thread.start()
        thread_list.append(dns_thread)
        time.sleep(3)  # Give time before next check starts

    # Start tcp service check thread and add to list
    if 'TCP' in service_checks:
        tcp_thread = threading.Thread(target=tcp_service_check, args=(server_dict, server, event))
        tcp_thread.start()
        thread_list.append(tcp_thread)
        time.sleep(3)  # Give time before next check starts

    # Start udp service check thread and add to list
    if 'UDP' in service_checks:
        udp_thread = threading.Thread(target=udp_service_check, args=(server_dict, server, event))
        udp_thread.start()
        thread_list.append(udp_thread)
        time.sleep(3)  # Give time before next check starts


# Main function
def main() -> None:
    """
    Main function to handle user input and manage threads.
    Uses prompt-toolkit for handling user input with auto-completion and ensures
    the prompt stays at the bottom of the terminal.
    """
    # Create a general prompt
    general_prompt: PromptSession = PromptSession()

    # Command completer for auto-completion
    # This is where you will add new auto-complete commands
    commands = ['add', 'edit', 'delete', 'show-servers', 'monitor', 'monitor-all', 'exit']
    command_completer: WordCompleter = WordCompleter(commands, ignore_case=True)

    # Create a command prompt session
    command_prompt: PromptSession = PromptSession(completer=command_completer)

    # Service completer for auto-completion
    # This is where you will add new auto-complete services
    services = ['ICMP', 'HTTP', 'HTTPS', 'NTP', 'DNS', 'TCP', 'UDP']
    service_completer: WordCompleter = WordCompleter(services, ignore_case=True)

    # Create a service prompt session
    service_prompt: PromptSession = PromptSession(completer=service_completer)

    # Variable to control the main loop
    is_running: bool = True

    try:
        with patch_stdout():
            while is_running:

                # Display intro message and commands
                print("What would you like to do?\n")
                show_commands()

                # Get server dict from json file
                with open("server_dict.json", "r") as file:
                    server_dict = json.loads(file.read())

                # Get user command and validate
                command: str = command_prompt.prompt("Enter command: ")
                while command not in commands:
                    print("That is not a valid command!\n")
                    show_commands()
                    command: str = command_prompt.prompt("Enter command: ")

                if command == "add":

                    # Get domain or ip address from user
                    print("\nWhat server would you like to monitor?")
                    server: str = general_prompt.prompt("Domain or IP Address: ")
                    server_dict = {server: {}}

                    # Loop until user done adding services
                    adding_services = True
                    while adding_services:

                        # Get service user would like to monitor
                        print(f"\nWhat service would you like to test {server} with?")

                        # Print services
                        show_services(services)

                        # Get and validate service
                        service: str = service_prompt.prompt("Service: ")
                        service = service.upper()
                        while service not in services:
                            print("That is not a valid service!\n")
                            show_services(services)
                            service: str = service_prompt.prompt("Service: ")
                            service = service.upper()
                        print("")

                        # Get/set icmp specific parameters
                        if service == "ICMP":
                            print("Please enter the requested parameters: ")
                            interval = int(general_prompt.prompt("Test Interval (in seconds): "))
                            server_dict[server][service] = {'interval': interval}

                        # Get/set http specific parameters
                        elif service == "HTTP":
                            print("Please enter the requested parameters: ")
                            url = general_prompt.prompt("URL: http://")
                            interval = int(general_prompt.prompt("Test Interval (in seconds): "))
                            server_dict[server][service] = {'url': f"http://{url}", 'interval': interval}

                        # Get/set https specific parameters
                        elif service == "HTTPS":
                            print("Please enter the requested parameters: ")
                            url = general_prompt.prompt("URL: https://")
                            interval = int(general_prompt.prompt("Test Interval (in seconds): "))
                            server_dict[server][service] = {'url': f"https://{url}", 'interval': interval}

                        # Get/set ntp specific parameters
                        elif service == "NTP":
                            print("Please enter the requested parameters: ")
                            interval = int(general_prompt.prompt("Test Interval (in seconds): "))
                            server_dict[server][service] = {'server': server, 'interval': interval}

                        # Get dns specific parameters
                        elif service == "DNS":
                            print("Please enter the requested parameters: ")
                            dns_server = general_prompt.prompt("DNS Server: ")
                            query = input("Query Domain: ")
                            print("Enter record types to test (enter empty input when finished): ")
                            record_type_list = []
                            record_type = general_prompt.prompt("Record Type: ")
                            while record_type != "":
                                record_type_list.append(record_type)
                                record_type = general_prompt.prompt("Record Type: ")
                            interval = int(general_prompt.prompt("Test Interval (in seconds): "))
                            server_dict[server][service] = {'dns_server': dns_server, 'query': query,
                                                            'record_types': record_type_list, 'interval': interval}

                        # Get tcp specific parameters
                        elif service == "TCP":
                            print("Please enter the requested parameters: ")
                            port = int(general_prompt.prompt("Target Port: "))
                            interval = int(general_prompt.prompt("Test Interval (in seconds): "))
                            server_dict[server][service] = {'port': port, 'interval': interval}

                        # Get udp specific parameters
                        elif service == "UDP":
                            print("Please enter the requested parameters: ")
                            port = int(general_prompt.prompt("Target Port: "))
                            interval = int(general_prompt.prompt("Test Interval (in seconds): "))
                            server_dict[server][service] = {'port': port, 'interval': interval}

                        # Success message
                        print("")
                        print(f"Successfully added {service} as a service to server {server}!")

                        # Ask if another service should be added - exit loop and update json file if not
                        if general_prompt.prompt("Would you like to add another service? (y/n): ").lower() != "y":
                            # Stop loop and print separator
                            adding_services = False
                            print("--------------------------------------------------------------------")

                            # Persist server/service to JSON file
                            with open('server_dict.json', 'r+') as file:
                                server_json = file.read()
                                server_dict.update(json.loads(server_json))
                                file.seek(0)
                                file.truncate()
                                file.write(json.dumps(server_dict))

                if command == "show-servers":

                    # Show the server configs
                    show_server_configs(server_dict)

                    # Go back home when user presses enter
                    if general_prompt.prompt("Press enter to go back to home: ") == "":
                        print("\n--------------------------------------------------------------------")

                if command == "monitor":

                    # Server completer for auto-completion
                    # This is where you will add new auto-complete servers
                    servers = server_dict.keys()
                    server_completer: WordCompleter = WordCompleter(servers, ignore_case=True)

                    # Create a prompt session
                    server_prompt: PromptSession = PromptSession(completer=server_completer)

                    # Ask which server they'd like to monitor
                    print("\nWhat server would you like to monitor?")

                    # Show current server configs
                    show_server_configs(server_dict)

                    # Prompt for server and validate
                    server: str = server_prompt.prompt("Server: ")
                    while server not in servers:
                        print("That is not a valid server!")
                        show_server_configs(server_dict)
                        server: str = server_prompt.prompt("Server: ")

                    # Initialize thread event and thread list to stop threads
                    event = threading.Event()
                    thread_list = []

                    # Initialize proper threads for service checks of the current server
                    initialize_threads(server_dict, server, event, thread_list)

                    # Quit service checks when user presses enter
                    if general_prompt.prompt("\nPress enter to quit monitoring: ") == "":

                        # Set event to kill threads
                        event.set()

                        # Wait for all threads to quit
                        for thread in thread_list:
                            thread.join()

                        print("\n--------------------------------------------------------------------")

                if command == "monitor-all":

                    # List servers prior to beginning monitor
                    show_server_configs(server_dict)

                    # Initialize thread event and thread list to stop threads
                    event = threading.Event()
                    thread_list = []

                    # Start service_checks for all services
                    for server in server_dict:

                        # Initialize proper threads for service checks of current server
                        initialize_threads(server_dict, server, event, thread_list)

                        # Give a time buffer between thread initializations
                        time.sleep(2)

                    # Quit service checks when user presses enter
                    if general_prompt.prompt("\nPress enter to quit monitoring: ") == "":

                        # Set event to kill threads
                        event.set()

                        # Wait for all threads to quit
                        for thread in thread_list:
                            thread.join()

                        print("\n--------------------------------------------------------------------")

                if command == "exit":
                    print("\nThank you for using CamCast! Goodbye.")
                    is_running = False
    finally:
        print("Closing")


if __name__ == '__main__':
    main()

