import sys
from pathlib import Path
import pyperclip


def attach_file_command(command_name, args, conversation, current_state, user_input):
    for filepath in args:
        file = Path(filepath).expanduser()
        file_content = file.read_text()
        conversation.add_item({
            "role": "user",
            "name": current_state["username"],
            "content": file_content,
            "mac_address": current_state["mac_address"]
        })

    return conversation, current_state, user_input


def copy_to_clipboard(command_name, args, conversation, current_state, user_input):
    content_to_copy = None
    selector = args[0] if args else None

    if not selector:
        last_response = conversation.filter_items({"role": "assistant"})[-1]
        response_id = last_response.get("id")
        content_to_copy = last_response.get("content", None)
        current_state["notifications"] = [f"last response ({response_id}) copied"]
    elif selector == 'all':
        all_responses = conversation.filter_items({"role": "assistant"})
        content_to_copy = '\n\n'.join([message.get('content') for message in all_responses])
        current_state["notifications"] = ["all responses copied"]
    elif ':' in selector:
        start, end = map(int, selector.split(':'))
        all_responses = conversation.filter_items({"role": "assistant"})
        selected_responses = all_responses[start-1:end+1]
        content_to_copy = "\n\n".join(response.get("content") for response in selected_responses)
        current_state["notifications"] = [f"responses {start}-{end} copied"]
    elif selector.isdigit():
        all_responses = conversation.filter_items({"role": "assistant"})
        selected_response = all_responses[int(selector) - 1]
        content_to_copy = selected_response.get("content")
        response_id = selected_response.get("id")
        current_state["notifications"] = [f"response #{selector} ({response_id}) copied"]
    else:
        selected_response = conversation.get_item(selector)
        content_to_copy = conversation.get_item(selector).get("content")
        response_id = selected_response.get("id")
        current_state["notifications"] = [f"response {response_id} copied"]

    if content_to_copy:
        pyperclip.copy(content_to_copy)


    return conversation, current_state, user_input


def enable_multiline_command(command_name, args, conversation, current_state, user_input):
    current_state["multiline_mode"] = True

    return conversation, current_state, user_input


def exit_command(command_name, args, conversation, current_state, user_input):
    sys.exit()


def remove_message_command(command_name, args, conversation, current_state, user_input):
    for message_id in args:
        removed_item = conversation.remove_item(message_id)

    return conversation, current_state, user_input


conversation_commands = {
    "attach": attach_file_command,
    "copy": copy_to_clipboard,
    "delete": remove_message_command,
    "exit": exit_command,
    "multi": enable_multiline_command,
    "remove": remove_message_command,
}