import sys
from pathlib import Path


def attach_file_command(command_name, args, conversation, current_state, user_input):
    for arg in args:
        file = Path(arg).expanduser()
        file_content = file.read_text()
        user_message = conversation.add_item({
            "role": "user",
            "name": current_state["username"],
            "content": file_content,
            "mac_address": current_state["mac_address"]
        })

    return conversation, current_state, user_input


def enable_multiline_command(command_name, args, conversation, current_state, user_input):
    current_state["multiline_mode"] = True

    return conversation, current_state, user_input


def exit_command(command_name, args, conversation, current_state, user_input):
    sys.exit()


conversation_commands = {
    "attach": attach_file_command,
    "exit": exit_command,
    "multi": enable_multiline_command
}