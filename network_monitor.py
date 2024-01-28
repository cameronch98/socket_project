import json
import sys
import keyboard
# from rich import print
from service_checks import *
from prompts import *


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
    print("Record-Types:")
    print("  A - IPv4 Address")
    print("  MX - Mail Exchange")
    print("  AAAA - IPv6 Address")
    print("  CNAME - Canonical Name")
    print("  Other - Manual Entry")
    print("  Press Enter to Stop\n")


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


# Main function
def main() -> None:
    """
    Main function to handle user input and manage threads.
    Uses prompt-toolkit for handling user input with auto-completion and ensures
    the prompt stays at the bottom of the terminal.
    """
    # Create a general prompt
    general_prompt: PromptSession = PromptSession()

    # Get terminal size
    columns, lines = shutil.get_terminal_size()
    print("\n")

    # Print project title
    print("███╗   ██╗███████╗████████╗ ██████╗ █████╗ ███╗   ███╗".center(columns))
    print("████╗  ██║██╔════╝╚══██╔══╝██╔════╝██╔══██╗████╗ ████║".center(columns))
    print("██╔██╗ ██║█████╗     ██║   ██║     ███████║██╔████╔██║".center(columns))
    print("██║╚██╗██║██╔══╝     ██║   ██║     ██╔══██║██║╚██╔╝██║".center(columns))
    print("██║ ╚████║███████╗   ██║   ╚██████╗██║  ██║██║ ╚═╝ ██║".center(columns))
    print(" ╚═╝  ╚═══╝╚══════╝   ╚═╝    ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝\n".center(columns))
    title_string = "Network Monitoring Tool"
    print(title_string.center(columns))
    author_string = "by Cameron Hester"
    print(author_string.center(columns))
    print("\n")

    # Prompt user to start program
    start_string = "Press any key to begin ..."
    print(start_string.center(columns))

    # Sleep to prevent auto enter
    time.sleep(1)

    # Start program upon keypress
    if keyboard.read_key():

        # Clear terminal
        os.system('cls') if sys.platform.startswith('win') else os.system('clear')

        # Start the main loop
        is_running: bool = True

    try:
        with patch_stdout():
            while is_running:

                # Display intro message and commands
                print("What would you like to do?\n")
                show_commands()

                # Get user command and validate
                command: str = command_prompt.prompt("Enter command: ")
                while command not in commands:
                    print("That is not a valid command!\n")
                    show_commands()
                    command: str = command_prompt.prompt("Enter command: ")

                # Get server dict from json file
                with open("server_dict.json", "r") as file:
                    server_dict = json.loads(file.read())

                # Server completer for auto-completion
                # This is where you will add new auto-complete servers
                servers = server_dict.keys()
                server_completer: WordCompleter = WordCompleter(servers, ignore_case=True)

                # Create a prompt session
                server_prompt: PromptSession = PromptSession(completer=server_completer)

                if command == "add-server":

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
                        show_services()

                        # Get and validate service
                        service: str = service_prompt.prompt("Service: ")
                        service = service.upper()
                        while service not in services:
                            print("That is not a valid service!\n")
                            show_services()
                            service: str = service_prompt.prompt("Service: ")
                            service = service.upper()
                        print("")

                        # Get/set icmp or ntp specific parameters
                        if service == "ICMP" or service == "NTP":
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

                        # Get dns specific parameters
                        elif service == "DNS":

                            # Get DNS server and query domain
                            print("Please enter the requested parameters: ")
                            dns_server = general_prompt.prompt("DNS Server: ")
                            query = input("Query Domain: ")

                            # Get list of record types user wants to check
                            print("Enter record types to test: \n")
                            show_record_types()
                            record_type_list = []
                            record_type = record_type_prompt.prompt("Record Type: \n")
                            while record_type != "":
                                record_type_list.append(record_type)
                                show_record_types()
                                record_type = record_type_prompt.prompt("Record Type: \n")

                            # Get interval
                            interval = int(general_prompt.prompt("Test Interval (in seconds): "))

                            # Set values in dict
                            server_dict[server][service] = {'dns_server': dns_server, 'query': query,
                                                            'record_types': record_type_list, 'interval': interval}

                        # Get tcp, udp, or local tcp specific parameters
                        elif service == "TCP" or service == "UDP" or service == "LOCAL TCP":
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
                            print("=" * columns)

                            # Persist server/service to JSON file
                            with open('server_dict.json', 'r+') as file:
                                server_json = file.read()
                                server_dict.update(json.loads(server_json))
                                file.seek(0)
                                file.truncate()
                                file.write(json.dumps(server_dict))

                if command == "edit-server":

                    # Ask which server they'd like to edit
                    print("\nWhat server would you like to edit?")

                    # Show current server configs
                    show_server_configs(server_dict)

                    # Prompt for server and validate
                    server: str = server_prompt.prompt("\nServer: ")
                    while server not in servers:
                        print("That is not a valid server!")
                        show_server_configs(server_dict)
                        server: str = server_prompt.prompt("Server: ")
                    print(f"Great! You are now editing the server {server} ...")

                    # Provide selection between adding, editing, and deleting a service
                    print("\nWhat would you like to do?")
                    show_edit_commands()

                    # Service completer for auto-completion
                    edit_commands = ['add-service', 'edit-service', 'delete-service']
                    edit_command_completer: WordCompleter = WordCompleter(edit_commands, ignore_case=True)

                    # Create a service prompt session
                    edit_command_prompt: PromptSession = PromptSession(completer=edit_command_completer)

                if command == "show-servers":

                    # Show the server configs
                    show_server_configs(server_dict)

                    # Go back home when user presses enter
                    if general_prompt.prompt("Press enter to go back to home: ") == "":
                        print("=" * columns)

                if command == "monitor-server":

                    # Ask which server they'd like to monitor
                    print("\nWhat server would you like to monitor?")

                    # Show current server configs
                    show_server_configs(server_dict)

                    # Prompt for server and validate
                    server: str = server_prompt.prompt("\nServer: ")
                    while server not in servers:
                        print("That is not a valid server!")
                        show_server_configs(server_dict)
                        server: str = server_prompt.prompt("Server: ")

                    # Event, lock and list to stop, prioritize, and track threads
                    event, lock = threading.Event(), threading.Lock()
                    thread_list = []

                    # Initialize proper threads for service checks of the current server
                    initialize_threads(server_dict, server, lock, event, thread_list)

                    # Quit service checks when user presses enter
                    if general_prompt.prompt("\nPress enter to quit monitoring: ") == "":

                        # Set event and wait for threads to quit
                        event.set()
                        for thread in thread_list:
                            thread.join()

                        # Print divider
                        print("=" * columns)

                if command == "monitor-all":

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
                    if general_prompt.prompt("\nPress enter to quit monitoring: ") == "":

                        # Set event and wait for threads to quit
                        event.set()
                        for thread in thread_list:
                            thread.join()

                        # Print divider
                        print("=" * columns)

                if command == "exit":
                    is_running = False

    finally:
        print("\nThank you for using NetCam! Goodbye.")


if __name__ == '__main__':
    main()

