import sys
from prompt_toolkit import prompt
from prompt_toolkit.patch_stdout import patch_stdout
from prompts import *
from service_checks import *


def show_commands():
    """
    Show available primary commands
    :return: None
    """
    print(r"""
    ┌───────────────────────────────────────────────┐
    │ Commands:                                     │
    │   add-server      Add a new server to monitor │
    │   edit-server     Edit an existing server     │
    │   delete-server   Delete an existing server   │
    │   show-servers    Show config of all servers  │
    │   monitor-server  Monitor a single server     │
    │   monitor-all     Monitor all servers         │
    │   exit            Exit the application        │
    └───────────────────────────────────────────────┘
    """)


def show_edit_commands():
    """
    Show available commands for editing servers
    :return: None
    """
    print(r"""
    ┌──────────────────────────────────────────────────────────────┐
    │ Commands:                                                    │
    │   add-service     Add a new service to this server           │
    │   edit-service    Edit an existing service for this server   │
    │   delete-service  Delete an existing service for this server │
    └──────────────────────────────────────────────────────────────┘
    """)


def show_services():
    """
    Show available services
    :return: None
    """
    print(r"""
    ┌──────────────────────────────────┐
    │ Services:                        │
    │                                  │
    │   ICMP  HTTP  HTTPS  LOCAL TCP   │
    │                                  │
    │   NTP   DNS   TCP    UDP         │
    │                                  │
    └──────────────────────────────────┘
    """)


def show_record_types():
    """
    Show dns record types
    :return: None
    """
    print(r"""
    ┌─────────────────────────┐
    │ Record-Types:           │
    │   A      IPv4 Address   │
    │   MX     Mail Exchange  │
    │   AAAA   IPv6 Address   │
    │   CNAME  Canonical Name │
    │   Other  Manual Entry   │
    │                         │
    │   Press Enter to Stop   │
    └─────────────────────────┘
    """)


def show_server_configs(server_dict):
    """
    Show current servers and services they are
    registered to monitor.
    :return: None
    """
    for server in server_dict:
        print(f"\nServer: {server}")
        print(f"Services: {', '.join(server_dict[server].keys())}")


def initialize_threads(server_dict, server, lock, event, thread_list):
    """
    Initializes necessary threads for the service checks of a particular server
    :param server_dict: dictionary with server and service information
    :param server: server the program is currently monitoring
    :param lock: thread lock to prevent overlapping output
    :param event: event to trigger killing thread
    :param thread_list: list of currently running threads
    :return: None
    """
    # Map protocols to their service checks
    service_check_map = {
        'ICMP': icmp_service_check,
        'HTTP': http_service_check,
        'HTTPS': https_service_check,
        'NTP': ntp_service_check,
        'DNS': dns_service_check,
        'TCP': tcp_service_check,
        'UDP': udp_service_check,
        'LOCAL TCP': local_tcp_service_check
    }

    # Get protocols for server
    protocols = server_dict[server].keys()

    # Start service check threads and add them to list
    for protocol in protocols:
        thread = threading.Thread(target=service_check_map[protocol], args=(server_dict, server, lock, event))
        thread.start()
        thread_list.append(thread)


def set_service_params(server_dict, server, service):
    """
    Sets parameters for a given service during an add or edit
    :param server_dict: dictionary with server and service information
    :param server: server the program is currently monitoring
    :param service: service to add or edit
    :return: None
    """
    # Get/set icmp specific parameters
    if service == "ICMP":
        print("\nPlease enter the requested parameters: ")
        interval = int(prompt("Test Interval (secs): "))

        # Add service to dict
        server_dict[server][service] = {
            'host': server,
            'ttl': 64,
            'timeout': 1,
            'sequence_number': 1,
            'max_hops': 30,
            'pings_per_hops': 1,
            'verbose': False,
            'interval': interval
        }

        # Inquire about optional params
        if prompt("\nWould you like to set optional parameters? (y/n): ") == 'y':
            print("\nPlease enter the optional parameters (press enter for defaults): ")
            ttl = prompt("TTL of Ping Packet (Default = 64): ")
            timeout = prompt("Timeout of Ping Test (secs) (Default = 1): ")
            sequence_number = prompt("Sequence Number of Ping Packet (Default = 1): ")
            max_hops = prompt("Max Hops in Traceroute Test (Default = 30): ")
            pings_per_hop = prompt("Number of Pings Per Traceroute Hop (Default = 1): ")
            verbose = prompt("Verbose Traceroute Results (True/False) (Default = False): ")

            # Set optional params
            server_dict[server][service]['ttl'] = int(ttl) if ttl else 64
            server_dict[server][service]['timeout'] = int(timeout) if timeout else 1
            server_dict[server][service]['sequence_number'] = int(sequence_number) if sequence_number else 1
            server_dict[server][service]['max_hops'] = int(max_hops) if max_hops else 30
            server_dict[server][service]['pings_per_hop'] = int(pings_per_hop) if pings_per_hop else 1
            server_dict[server][service]['verbose'] = verbose if verbose else False

    # Get/set http specific parameters
    elif service == "HTTP":
        print("\nPlease enter the requested parameters: ")
        url = prompt("URL: http://")
        interval = int(prompt("Test Interval (secs): "))
        server_dict[server][service] = {'url': f"http://{url}", 'interval': interval}

    # Get/set https specific parameters
    elif service == "HTTPS":
        print("\nPlease enter the requested parameters: ")
        url = prompt("URL: https://")
        interval = int(prompt("Test Interval (secs): "))

        # Add service to dict
        server_dict[server][service] = {'url': f"https://{url}", 'timeout': 5, 'interval': interval}

        # Inquire about optional params
        if prompt("\nWould you like to set optional parameters? (y/n): ") == 'y':
            print("\nPlease enter the optional parameters (press enter for defaults): ")
            timeout = prompt("Timeout of Request (secs) (Default = 5): ")

            # Set optional param
            server_dict[server][service]['timeout'] = int(timeout) if timeout else 5

    # Get/set ntp specific parameters
    elif service == "NTP":
        print("\nPlease enter the requested parameters: ")
        interval = int(prompt("Test Interval (secs): "))
        server_dict[server][service] = {'server': server, 'interval': interval}

    # Get/set dns specific parameters
    elif service == "DNS":

        # Get DNS server and query domain
        print("\nPlease enter the requested parameters: ")
        dns_server = prompt("DNS Server: ")
        query = prompt("Query Domain: ")

        # Get list of record types user wants to check
        print("Enter record types to test: ")
        show_record_types()
        record_type_list = []
        record_type = record_type_prompt("Record Type: ")
        while record_type != "":
            record_type_list.append(record_type)
            record_type = record_type_prompt("Record Type: ")

        # Get interval
        interval = int(prompt("\nTest Interval (secs): "))

        # Set values in dict
        server_dict[server][service] = {'dns_server': dns_server, 'query': query,
                                        'record_types': record_type_list, 'interval': interval}

    # Get/set tcp or local tcp specific parameters
    elif service == "TCP" or service == "LOCAL TCP":
        print("\nPlease enter the requested parameters: ")
        port = int(prompt("Target Port: "))
        interval = int(prompt("Test Interval (in seconds): "))
        server_dict[server][service] = {'port': port, 'interval': interval}

    # Get/set udp specific parameters
    elif service == "UDP":
        print("\nPlease enter the requested parameters: ")
        port = int(prompt("Target Port: "))
        interval = int(prompt("Test Interval (in seconds): "))

        # Add service to dict
        server_dict[server][service] = {'port': port, 'timeout': 3, 'interval': interval}

        # Inquire about optional params
        if prompt("\nWould you like to set optional parameters? (y/n): ") == 'y':
            print("\nPlease enter the optional parameters (press enter for defaults): ")
            timeout = prompt("Timeout of Socket Operation (secs) (Default = 3): ")

            # Set optional params
            server_dict[server][service]['timeout'] = int(timeout) if timeout else 3


# Main function
def main() -> None:
    """
    Main function to handle user input and manage threads.
    Uses prompt-toolkit for handling user input with auto-completion and ensures
    the prompt stays at the bottom of the terminal.
    """
    # Get terminal size
    columns, lines = shutil.get_terminal_size()
    print("")

    # Print project title
    print(r" _   _      _    ____                ".center(columns))
    print(r"| \ | | ___| |_ / ___|__ _ _ __ ___  ".center(columns))
    print(r"|  \| |/ _ \ __| |   / _` | '_ ` _ \ ".center(columns))
    print(r"| |\  |  __/ |_| |__| (_| | | | | | |".center(columns))
    print(r"|_| \_|\___|\__|\____\__,_|_| |_| |_|".center(columns))
    print("")
    title_string = "Network Monitoring Tool"
    print(title_string.center(columns))
    author_string = "by Cameron Hester"
    print(author_string.center(columns))
    print("\n")

    # Prompt user to start program
    start_string = "Press enter to begin ..."
    print(start_string.center(columns))

    # Sleep to prevent auto enter
    time.sleep(1)

    # Start program upon keypress
    if prompt("") == "":

        # Clear terminal
        os.system('cls') if sys.platform.startswith('win') else os.system('clear')

        # Start the main loop
        is_running: bool = True

    try:
        with patch_stdout():
            while is_running:

                print("What would you like to do?")

                # Get user command and validate
                show_commands()
                command: str = home_command_prompt("Enter command: ")

                # Get server dict from json file
                with open("server_dict.json", "r") as file:
                    server_dict = json.loads(file.read())

                if command == "add-server":

                    # Get domain or ip address from user
                    print("\nWhat server would you like to monitor?")
                    server: str = prompt("Domain or IP Address: ")
                    server_dict[server] = dict()

                    # Loop until user done adding services
                    adding_services = True
                    while adding_services:

                        # Get service user would like to monitor
                        print(f"\nWhat service would you like to test {server} with?")

                        # Get and validate service
                        show_services()
                        service: str = service_prompt("Service: ").upper()

                        # Get and set service parameters
                        set_service_params(server_dict, server, service)

                        # Success message
                        print("")
                        print(f"Successfully added {service} as a service to server {server}!")

                        # Ask if another service should be added - exit loop and update json file if not
                        if prompt("Would you like to add another service? (y/n): ").lower() == "n":

                            # Stop loop and print separator
                            adding_services = False

                            # Clear terminal
                            os.system('cls') if sys.platform.startswith('win') else os.system('clear')

                            # Persist server dict to JSON file
                            with open('server_dict.json', 'w') as file:
                                file.write(json.dumps(server_dict))

                elif command == "edit-server" and len(server_dict) > 0:

                    # Ask which server they'd like to edit
                    print("\nWhat server would you like to edit?")

                    # Show current server configs
                    show_server_configs(server_dict)

                    # Prompt for server and validate
                    server: str = server_prompt("\nServer: ")
                    print(f"Great! You are now editing the server {server} ...")

                    # Provide selection between adding, editing, and deleting a service
                    print("\nWhat would you like to do?")
                    show_edit_commands()
                    command: str = edit_command_prompt("Enter command: ")

                    if command == "add-service":

                        # Loop until user done adding services
                        adding_services: bool = True
                        while adding_services:

                            print(f"\nWhat service would you like to add to {server}?")

                            # Get and validate service
                            show_services()
                            service: str = service_prompt("Service: ").upper()

                            # Add new service to given server
                            set_service_params(server_dict, server, service)
                            print(f"\nSuccessfully added {service} as a service to server {server}!")

                            # Ask if another service should be added - exit loop and update json file if not
                            if prompt("Would you like to add another service? (y/n): ").lower() == "n":
                                # Stop loop and print separator
                                adding_services = False

                                # Clear terminal
                                os.system('cls') if sys.platform.startswith('win') else os.system('clear')

                                # Persist server dict to JSON file
                                with open('server_dict.json', 'w') as file:
                                    file.write(json.dumps(server_dict))

                    elif command == "edit-service":

                        # Loop until user done editing services
                        editing_services: bool = True
                        while editing_services:

                            print(f"\nWhat service would you like to edit?")

                            # Get and validate service
                            print(f"Services: {', '.join(server_dict[server].keys())}")
                            service: str = service_prompt("\nService: ").upper()

                            # Add new service to given server
                            set_service_params(server_dict, server, service)
                            print(f"\nSuccessfully edited {service}!")

                            # Ask if another service should be edited - exit loop and update json file if not
                            if prompt("Would you like to edit another service? (y/n): ").lower() == "n":
                                # Stop loop and print separator
                                editing_services = False

                                # Clear terminal
                                os.system('cls') if sys.platform.startswith('win') else os.system('clear')

                                # Persist server dict to JSON file
                                with open('server_dict.json', 'w') as file:
                                    file.write(json.dumps(server_dict))

                    elif command == "delete-service":

                        # Loop until user done deleting services
                        deleting_services: bool = True
                        while deleting_services:

                            print(f"\nWhat service would you like to delete?")

                            # Get and validate service
                            print(f"Services: {', '.join(server_dict[server].keys())}")
                            service: str = service_prompt("Service: ").upper()

                            # Delete service
                            del server_dict[server][service]

                            # Ask if another service should be deleted - exit loop and update json file if not
                            if prompt("Would you like to delete another service? (y/n): ").lower() == "n":
                                # Stop loop and print separator
                                deleting_services = False

                                # Clear terminal
                                os.system('cls') if sys.platform.startswith('win') else os.system('clear')

                                # Persist server dict to JSON file
                                with open('server_dict.json', 'w') as file:
                                    file.write(json.dumps(server_dict))

                elif command == "delete-server" and len(server_dict) > 0:

                    # Loop until user done deleting servers
                    deleting_servers: bool = True
                    while deleting_servers:

                        print(f"\nWhat server would you like to delete?")

                        # Get and validate service
                        show_server_configs(server_dict)
                        server: str = server_prompt("\nServer: ")

                        # Delete server
                        del server_dict[server]

                        # Success message
                        print(f"\nSuccessfully deleted {server} from server list!")

                        # Ask if another server should be deleted - exit loop and update json file if not
                        if prompt("Would you like to delete another server? (y/n): ").lower() == "n":
                            # Stop loop and print separator
                            deleting_servers = False

                            # Clear terminal
                            os.system('cls') if sys.platform.startswith('win') else os.system('clear')

                            # Persist server dict to JSON file
                            with open('server_dict.json', 'w') as file:
                                file.write(json.dumps(server_dict))

                elif command == "edit-server" or command == "delete-server" and len(server_dict) == 0:
                    print("There are no servers to edit or delete!\n")

                elif command == "show-servers":

                    # Show the server configs
                    show_server_configs(server_dict)

                    # Go back home when user presses enter
                    if prompt("\nPress enter to go back to home: ") == "":

                        # Clear terminal
                        os.system('cls') if sys.platform.startswith('win') else os.system('clear')

                elif command == "monitor-server":

                    # Ask which server they'd like to monitor
                    print("\nWhat server would you like to monitor?")

                    # Show current server configs
                    show_server_configs(server_dict)

                    # Prompt for server and validate
                    server: str = server_prompt("\nServer: ")

                    # Event, lock and list to stop, prioritize, and track threads
                    event, lock = threading.Event(), threading.Lock()
                    thread_list = []

                    # Initialize proper threads for service checks of the current server
                    initialize_threads(server_dict, server, lock, event, thread_list)

                    # Quit service checks when user presses enter
                    if prompt("\nPress enter to quit monitoring: ") == "":

                        # Set event and wait for threads to quit
                        event.set()
                        for thread in thread_list:
                            thread.join()

                        # Print divider
                        print("\n" + "=" * columns + "\n")

                elif command == "monitor-all":

                    # List servers prior to beginning monitor
                    show_server_configs(server_dict)

                    # Event, lock and list to stop, prioritize, and track threads
                    event, lock = threading.Event(), threading.Lock()
                    thread_list = []

                    # Start service_checks for all services
                    for server in server_dict:

                        # Initialize proper threads for service checks of current server
                        initialize_threads(server_dict, server, lock, event, thread_list)

                    # Quit service checks when user presses enter
                    if prompt("\nPress enter to quit monitoring: ") == "":

                        # Set event and wait for threads to quit
                        event.set()
                        for thread in thread_list:
                            thread.join()

                        # Print divider
                        print("\n" + "=" * columns + "\n")

                elif command == "exit":
                    is_running = False

    finally:
        print("\nThank you for using NetCam! Goodbye.")


if __name__ == '__main__':
    main()

