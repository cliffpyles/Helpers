import json
import openai
import os
import rich_click as click
import textwrap
import uuid
import webbrowser
import yaml
from conversation_commands import conversation_commands
from InquirerPy import inquirer
from InquirerPy.validator import NumberValidator
from pathlib import Path
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console
from rich.markdown import Markdown
from tempfile import NamedTemporaryFile
from constants import *


def create_message(content, name, role, mac_address):
    message = {"role": role, "content": content}
    if name:
        message["name"] = name

    return message


def execute_command(command_name, app_state):
    command_name = command_name[1:].lower()
    unknown_command = lambda: click.echo(f"Unrecognized command: {command_name}")
    result = conversation_commands.get(command_name, unknown_command)(app_state)

    return result


def get_conversations_directory():
    conversation_dir = Path.home() / ".chatai/conversations"
    return conversation_dir


def get_conversation_path(conversation_name, model):
    conversation_dir = Path.home() / ".chatai/conversations"
    conversation_path = conversation_dir / f"{conversation_name}__{model}.json"
    return conversation_path


def get_user_information():
    username = os.getlogin()
    mac_address = hex(uuid.getnode())
    return username, mac_address


def indent_text(text, spaces=4, max_width=None):
    if max_width is not None:
        text = textwrap.fill(text, max_width)

    indentation = " " * spaces
    indented_lines = [indentation + line for line in text.splitlines()]
    indented_text = "\n".join(indented_lines)
    return indented_text


def load_key_bindings():
    return KeyBindings()


def load_session(conversation):
    session = PromptSession(history=InMemoryHistory())
    for message in conversation.get_items():
        if message["role"] == "user":
            session.history.append_string(message["content"])

    return session


def load_prompt(prop_name="default"):
    script_dir = Path(__file__).resolve(strict=False).parent
    prompt_configs = [
        yaml.safe_load(prompt.read_text())
        for prompt in script_dir.glob("./prompts/*.yaml")
    ]
    prompts = {}
    cleaned_promp_name = (
        prop_name.strip().replace("-", "").replace("_", "").replace(" ", "").lower()
    )
    for prompt_config in prompt_configs:
        keys = prompt_config.get("keys")
        model = prompt_config.get("model")
        messages = prompt_config.get("messages")

        for key in keys:
            prompts[key] = {"model": model, "messages": messages}

    if cleaned_promp_name in prompts:
        return prompts[cleaned_promp_name]
    else:
        return prompts["default"]


def load_prompts():
    prompts = [
        yaml.safe_load(prompt.read_text())
        for prompt in script_dir.glob("./prompts/*.yaml")
    ]
    return prompts


def open_conversation(conversation_path, messages):
    conversation = []

    if conversation_path.is_file():
        file_content = json.loads(conversation_path.read_text())
        conversation = file_content
    else:
        conversation = []
        for message in messages:
            message["id"] = str(uuid.uuid4())
            conversation.append(message)

        conversation_path.touch()
        conversation_path.write_text(json.dumps(conversation))

    return conversation, conversation_path


def serialize_message(message):
    serialized_message = {"role": message["role"], "content": message["content"]}
    if "name" in message:
        serialized_message["name"] = message["name"]

    return serialized_message


def send_chat(**kwargs):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    response = openai.ChatCompletion.create(**kwargs)

    return response["choices"][0]["message"]


def send_chat_message(model, messages, user_message):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    messages_payload = []
    user = f"{user_message['mac_address']}::{user_message['name']}"
    for message in messages:
        messages_payload.append(serialize_message(message))
    if user_message:
        messages_payload.append(serialize_message(user_message))
    response = openai.ChatCompletion.create(model=model, messages=messages_payload, user=user)

    return response["choices"][0]["message"]


def send_image(image_description, size):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    response = openai.Image.create(
        prompt=f"{image_description}", n=1, size=f"{size}x{size}"
    )
    response["data"][0]["url"]


def view_conversation(conversation, key_bindings, mac_address, model, session, username):
    click.clear()
    click.echo("Entering an interactive conversation.")
    click.echo("Type 'exit' to end the conversation.")
    view_messages(conversation.get_items())
    view_message_input(conversation, key_bindings, mac_address, model, session, username)


def view_message_input(conversation, key_bindings, mac_address, model, session, username):
    current_state = {"multiline_mode": False}
    while True:
        user_input = session.prompt(
            message=f"\n\n{MESSAGE_INDICATOR} New Message: ",
            key_bindings=key_bindings,
            multiline=current_state.get("multiline_mode", False),
            wrap_lines=True,
        )

        # Execute the command if the input starts with a '/'
        if user_input.startswith("/"):
            current_state = execute_command(user_input, current_state)
        elif len(user_input.strip()) > 0:
            try:
                user_message = conversation.create_item({
                    "role": "user",
                    "name": username,
                    "content": f"{user_input}",
                    "mac_address": mac_address,
                })
                messages = conversation.get_items()
                response_message = send_chat_message(model, messages, user_message)
                assistant_message = response_message.to_dict_recursive()
                conversation.create_item(assistant_message)
                view_message(assistant_message)
                current_state["multiline_mode"] = False

            except Exception as e:
                click.echo(f"Error: {e}")


def view_message(message):
    console = Console()
    if message["role"] == "user":
        message_id = message.get("id", "None")
        click.secho(f"\n\n{MESSAGE_INDICATOR} Message ({message_id}):\n", bold=True)
    elif message["role"] == "system":
        click.secho(f"\n\n{SYSTEM_INDICATOR} System:\n", bold=True)
    else:
        message_id = message.get("id", "None")
        click.secho(f"\n\n{RESPONSE_INDICATOR} Response ({message_id}):\n", bold=True)
    markdown = Markdown(message["content"])
    console.print(markdown)


def view_messages(messages):
    for message in messages:
        view_message(message)
