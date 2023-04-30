import sys
from typing import Dict

def construct_command(config: Dict, responses: Dict) -> str:
    """
    Constructs the command to reproduce the current context based on the config and user responses.

    :param config: The loaded configuration dictionary containing prompts and other settings.
    :param responses: The user responses dictionary.
    :return: The command string to reproduce the current context.
    """

    # Construct a command to reproduce the current context
    command = " ".join(sys.argv)
    for k, v in responses.items():
        for prompt in config["prompts"]:
            prompt_key = prompt.get('key')
            prompt_type = prompt['type']
            if k == prompt_key and prompt_type != 'file':
                command += f" --{k} \"{v}\""
            elif k == prompt_key and prompt_type == 'file':
                command += f" --{k} \"{v}\""
    return command
