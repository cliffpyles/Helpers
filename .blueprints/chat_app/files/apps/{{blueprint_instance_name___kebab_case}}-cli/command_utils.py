import sys
from typing import Dict
from pathlib import Path

def construct_command(config: Dict, responses: Dict) -> str:
    """
    Constructs the command to reproduce the current context based on the config and user responses.

    :param config: The loaded configuration dictionary containing prompts and other settings.
    :param responses: The user responses dictionary.
    :return: The command string to reproduce the current context.
    """

    # Construct a command to reproduce the current context
    command_filepath = " ".join(sys.argv)
    command = Path(command_filepath).name

    for k, v in responses.items():
        if k in config["prompts"]:
            command += f" --{k} \"{v}\""

    return command
