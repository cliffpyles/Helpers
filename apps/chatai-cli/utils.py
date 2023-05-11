# Filename: utils.py

import json
import openai
import os
import requests
import rich_click as click
import shutil
import subprocess
import textwrap
import uuid
import yaml
from conversation_commands import conversation_commands
from pathlib import Path
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings


def execute_conversation_command(raw_command, **kwargs):
    try:
        command_sections = raw_command.strip().split(" ")
        args = command_sections[1:]
        command_name = command_sections[0][1:].lower()
        unknown_command = conversation_commands.get("unknown")
        conversation_command = conversation_commands.get(command_name, unknown_command)
        return conversation_command(command_name, args, **kwargs)
    except TypeError as err:
        print("Error executing conversation command", err)


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


def load_prompt_preconfigured(prop_name):
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


def load_prompt_filepath(filepath):
    prompt_file = Path(filepath).expanduser()
    prompt = yaml.safe_load(prompt_file.read_text())
    return prompt


def load_prompt(prop_name="default", filepath=None):
    if not filepath:
        return load_prompt_preconfigured(prop_name)
    else:
        return load_prompt_filepath(filepath)


def load_prompts():
    script_dir = Path(__file__).resolve(strict=False).parent
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


def render_image(image_url):
    if shutil.which('imgcat'):
        response = requests.get(image_url)
        image_data = response.content
        subprocess.run(['imgcat'], input=image_data, check=True)


def render_text(text, **kwargs):
    click.echo(text, **kwargs)


def save_prompt(filepath, prompt):
    filepath = Path(filepath).expanduser()
    content = yaml.dump(prompt)
    filepath.write_text(content)

    return filepath


def serialize_message(message):
    serialized_message = {"role": message["role"], "content": message["content"]}
    if "name" in message:
        serialized_message["name"] = message["name"]

    return serialized_message


def send_chat_sync(**kwargs):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    response = openai.ChatCompletion.create(**kwargs)

    return response["choices"][0]["message"]


def send_chat_async(**kwargs):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    response_generator = openai.ChatCompletion.create(stream=True, **kwargs)
    
    return response_generator


def send_messages_sync (model, messages):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    messages_payload = []

    for message in messages:
        messages_payload.append(serialize_message(message))
    
    response = openai.ChatCompletion.create(model=model, messages=messages_payload)

    return response["choices"][0]["message"]

def send_chat_message_sync (model, messages, user_message):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    messages_payload = []
    user = f"{user_message['mac_address']}::{user_message['name']}"
    for message in messages:
        messages_payload.append(serialize_message(message))
    if user_message:
        messages_payload.append(serialize_message(user_message))
    response = openai.ChatCompletion.create(model=model, messages=messages_payload, user=user)

    return response["choices"][0]["message"]


def send_chat_message_async(model, messages, user_message):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    messages_payload = []
    user = f"{user_message['mac_address']}::{user_message['name']}"
    for message in messages:
        messages_payload.append(serialize_message(message))
    if user_message:
        messages_payload.append(serialize_message(user_message))
    
    response_generator = openai.ChatCompletion.create(model=model, messages=messages_payload, user=user, stream=True)

    return response_generator


def send_image(image_description, size):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    response = openai.Image.create(
        prompt=f"{image_description}", n=1, size=f"{size}x{size}"
    )
    return response["data"][0]["url"]
