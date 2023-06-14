# Filename: utils.py

import json
import openai
import os
import requests
import glob
import rich_click as click
import shutil
import socket
import subprocess
import uuid
import yaml
import tiktoken
from conversation_commands import (
    conversation_commands,
    conversation_command_autocompletes,
)
from pathlib import Path
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory


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


def get_system_info():
    system_info = {}
    # User name
    system_info["login"] = os.getlogin()

    # Host name
    system_info["host_name"] = socket.gethostname()

    # IP address
    system_info["ip_address"] = socket.gethostbyname(system_info["host_name"])

    # System name
    system_info["system_name"] = os.name

    # Mac address
    system_info["mac_address"] = ":".join(
        ["{:02x}".format((uuid.getnode() >> ele) & 0xFF) for ele in range(0, 8 * 6, 8)][
            ::-1
        ]
    )

    return system_info


def get_text_between(source, start_tag, end_tag):
    # Check if the start_tag and end_tag exist in the source
    if start_tag not in source or end_tag not in source:
        raise ValueError("Start tag or end tag not found in source.")

    # Check if the start_tag comes before the end_tag
    if source.index(start_tag) > source.index(end_tag):
        raise ValueError("Start tag appears after end tag.")

    # Find the start and end indices of the content between the tags
    start_index = source.index(start_tag) + len(start_tag)
    end_index = source.index(end_tag)

    # Extract and return the content
    return source[start_index:end_index]


def get_user_information():
    username = os.getlogin()
    mac_address = hex(uuid.getnode())

    return username, mac_address


def load_completer(conversation):
    command_names = [
        conversation_command
        for conversation_command in conversation_command_autocompletes.keys()
    ]

    commands = {}
    for command_name in command_names:
        commands[f"/{command_name}"] = conversation_command_autocompletes.get(
            command_name
        )(conversation)
    completer = NestedCompleter.from_nested_dict(commands)

    return completer


def load_key_bindings():
    return KeyBindings()


def load_session(conversation=None):
    session = PromptSession(
        auto_suggest=AutoSuggestFromHistory(), history=InMemoryHistory()
    )
    if conversation:
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
    prompts_dir = Path(__file__).resolve(strict=False).parent / f"./prompts"
    prompt_files = glob.glob("**/*.yaml", root_dir=prompts_dir, recursive=True)

    prompts = [
        yaml.safe_load(Path(prompts_dir / f"./{prompt}").read_text())
        for prompt in prompt_files
    ]

    return prompts


def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        print(
            "Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301."
        )
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301")
    elif model == "gpt-4":
        print(
            "Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314."
        )
        return num_tokens_from_messages(messages, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = (
            4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        )
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


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
    if shutil.which("imgcat"):
        response = requests.get(image_url)
        image_data = response.content
        subprocess.run(["imgcat"], input=image_data, check=True)


def render_text(text, **kwargs):
    click.echo(text, **kwargs)


def save_prompt(filepath, prompt):
    def str_presenter(dumper, data):
        if len(data.splitlines()) > 1:  # check for multiline string
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
        return dumper.represent_scalar("tag:yaml.org,2002:str", data)

    yaml.add_representer(str, str_presenter)
    yaml.representer.SafeRepresenter.add_representer(str, str_presenter)
    filepath = Path(filepath).expanduser()
    content = yaml.dump(prompt, default_flow_style=False, sort_keys=False)
    filepath.write_text(content, newline=None)
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


def send_messages_sync(model, messages):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    messages_payload = []

    for message in messages:
        messages_payload.append(serialize_message(message))

    response = openai.ChatCompletion.create(model=model, messages=messages_payload)
    message = response["choices"][0]["message"]

    message["usage"] = response["usage"]
    return message


def send_chat_message_sync(model, messages, user_message):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    messages_payload = []
    user = f"{user_message['mac_address']}::{user_message['name']}"
    for message in messages:
        messages_payload.append(serialize_message(message))
    if "content" in user_message:
        messages_payload.append(serialize_message(user_message))

    response = openai.ChatCompletion.create(
        model=model, messages=messages_payload, user=user
    )
    message = response["choices"][0]["message"]
    message["usage"] = response["usage"]
    return message


def send_chat_message_async(model, messages, user_message):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    messages_payload = []
    user = f"{user_message['mac_address']}::{user_message['name']}"
    for message in messages:
        messages_payload.append(serialize_message(message))
    if user_message:
        messages_payload.append(serialize_message(user_message))

    response_generator = openai.ChatCompletion.create(
        model=model, messages=messages_payload, user=user, stream=True
    )

    return response_generator


def send_image(image_description, size):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    response = openai.Image.create(
        prompt=f"{image_description}", n=1, size=f"{size}x{size}"
    )
    return response["data"][0]["url"]
