import json

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.validation import Validator, ValidationError


class ServerCommandValidator(Validator):
    def validate(self, document):
        """
        Validator for server command prompt
        :param document: input from prompt
        :return: None
        """
        # Define server commands
        server_commands = [
            'add-server',
            'edit-server',
            'delete-server',
            'show-servers',
            'monitor-server',
            'monitor-all',
            'exit'
        ]

        # Validate that input is one of server commands
        if document.text not in server_commands:
            raise ValidationError(message=f"{document.text} is not a valid command!")


class ServiceValidator(Validator):
    def validate(self, document):
        """
        Validator for service prompt
        :param document: input from prompt
        :return: None
        """
        # Define available services
        services = ['ICMP', 'HTTP', 'HTTPS', 'NTP', 'DNS', 'TCP', 'UDP', 'LOCAL TCP']

        # Validate that input is one of available services
        if document.text not in services:
            raise ValidationError(message=f"{document.text} is not a valid service!")


class ServerEditCommandValidator(Validator):
    def validate(self, document):
        """
        Validator for server edit command prompt
        :param document: input from prompt
        :return: None
        """
        # Define commands for editing servers
        server_edit_commands = ['add-service', 'edit-service', 'delete-service']

        # Validate that input is one of server editing commands
        if document.text not in server_edit_commands:
            raise ValidationError(message=f"{document.text} is not a valid command!")


class RecordTypeValidator(Validator):
    def validate(self, document):
        """
        Validator for record type prompt
        :param document: input from prompt
        :return: None
        """
        # Define available dns record types
        record_types = ['A', 'MX', 'AAAA', 'CNAME', 'ANAME', 'NS', 'SOA', 'TXT', 'PTR', 'SRV', 'SPF']

        # Validate that input is one of available record types
        if document.text not in record_types:
            raise ValidationError(message=f"{document.text} is not a valid DNS record type!")


def home_command_prompt(prompt_msg):
    """
    Prompt user for a home level command
    :param prompt_msg: prompt message defined in main
    :return: None
    """
    # Define available main commands
    home_commands = [
        'add-server',
        'edit-server',
        'delete-server',
        'show-servers',
        'monitor-server',
        'monitor-all',
        'exit'
    ]

    # Initialize auto-completer and validator for prompt session
    completer: WordCompleter = WordCompleter(home_commands, ignore_case=True)
    validator = Validator.from_callable(
        lambda text: text in home_commands,
        error_message=f"This is not a valid command!",
        move_cursor_to_end=True)

    # Start prompt session
    prompt: PromptSession = PromptSession(completer=completer, validator=validator)

    # Prompt
    prompt.prompt(f"{prompt_msg}")


def service_prompt(prompt_msg):
    """
    Prompt user to enter a service
    :param prompt_msg: prompt message defined in main
    :return: None
    """
    # Define available services
    services = ['ICMP', 'HTTP', 'HTTPS', 'NTP', 'DNS', 'TCP', 'UDP', 'LOCAL TCP']

    # Initialize auto-completer and validator for prompt session
    completer: WordCompleter = WordCompleter(services, ignore_case=True)
    validator = Validator.from_callable(
        lambda text: text in services,
        error_message=f"This is not a valid service!",
        move_cursor_to_end=True)

    # Start prompt session
    prompt: PromptSession = PromptSession(completer=completer, validator=validator)

    # Prompt
    prompt.prompt(f"{prompt_msg}")


def edit_command_prompt(prompt_msg):
    """
    Prompt user for a command used to edit a server
    :param prompt_msg: prompt message defined in main
    :return: None
    """
    # Define available commands for editing a server
    edit_commands = ['add-service', 'edit-service', 'delete-service']

    # Initialize auto-completer and validator for prompt session
    completer: WordCompleter = WordCompleter(edit_commands, ignore_case=True)
    validator = Validator.from_callable(
        lambda text: text in edit_commands,
        error_message=f"This is not a valid command!",
        move_cursor_to_end=True)

    # Start prompt session
    prompt: PromptSession = PromptSession(completer=completer, validator=validator)

    # Prompt
    prompt.prompt(f"{prompt_msg}")


def record_type_prompt(prompt_msg):
    """
    Prompt user for a dns record type
    :param prompt_msg: prompt message defined in main
    :return: None
    """
    # Define available record types
    record_types = ['A', 'MX', 'AAAA', 'CNAME', 'ANAME', 'NS', 'SOA', 'TXT', 'PTR', 'SRV', 'SPF']

    # Initialize auto-completer and validator for prompt session
    completer: WordCompleter = WordCompleter(record_types, ignore_case=True)
    validator = Validator.from_callable(
        lambda text: text in record_types,
        error_message=f"This is not a valid DNS record type!",
        move_cursor_to_end=True)

    # Start prompt session
    prompt: PromptSession = PromptSession(completer=completer, validator=validator)

    # Prompt
    prompt.prompt(f"{prompt_msg}")


def server_prompt(prompt_msg):
    """
    Prompt user for a server to work with
    :param prompt_msg: prompt message defined in main
    :return: None
    """
    # Get server dict from json file
    with open("server_dict.json", "r") as file:
        server_dict = json.loads(file.read())

    # Get current servers from server dict
    servers = list(server_dict.keys())

    # Initialize auto-completer and validator for prompt session
    completer: WordCompleter = WordCompleter(servers, ignore_case=True)
    validator = Validator.from_callable(
        lambda text: text in servers,
        error_message=f"This is not a valid DNS record type!",
        move_cursor_to_end=True)

    # Start prompt session
    prompt: PromptSession = PromptSession(completer=completer, validator=validator)

    # Prompt
    prompt.prompt(f"{prompt_msg}")
