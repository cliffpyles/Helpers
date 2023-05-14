# Filename: commands.py

import click
from pathlib import Path
from utils import *
from constants import *
from views import *
from lib.datastore import Datastore
import re


def analyze_command(filepath, model, prompt):
    username, mac_address = get_user_information()
    prompt = load_prompt(prompt)
    model = model or prompt["model"]
    messages = prompt["messages"]
    file_content = Path(filepath).read_text()
    if file_content:
        user_message = {
            "role": "user",
            "name": username,
            "mac_address": mac_address,
            "content": file_content,
        }
        response_message, usage = send_chat_message_sync(
            model=model, messages=messages, user_message=user_message
        )
        messages.append(user_message)
        messages.append(response_message)
    view_messages(messages)


def ask_command(user_input, model, prompt, raw, stream):
    if stream:
        ask_command_async(user_input, model, prompt, raw)
    else:
        ask_command_sync(user_input, model, prompt, raw)


def ask_command_sync(user_input, model, prompt, raw):
    username, mac_address = get_user_information()
    prompt = load_prompt(prompt)
    model = model or prompt["model"]
    messages = prompt["messages"]
    user_message = {
        "role": "user",
        "name": username,
        "mac_address": mac_address,
        "content": user_input,
    }
    get_api_data = lambda: send_chat_message_sync(
        model=model, messages=messages, user_message=user_message
    )
    if raw:
        response_message = get_api_data()
        click.echo(response_message["content"])
    else:
        messages.append(user_message)
        view_messages(messages, model)
        response_message = view_data_loader(fn=get_api_data)
        messages.append(response_message)
        view_message(messages[-1])


def ask_command_async(user_input, model, prompt, raw):
    username, mac_address = get_user_information()
    prompt = load_prompt(prompt)
    model = model or prompt["model"]
    messages = prompt["messages"]
    user_message = {
        "role": "user",
        "name": username,
        "mac_address": mac_address,
        "content": user_input,
    }
    if raw:
        response_generator = send_chat_message_async(
            model=model, messages=messages, user_message=user_message
        )
        view_response_stream(response_generator, raw=raw)
    else:
        view_messages(messages, model)
        response_generator = send_chat_message_async(
            model=model, messages=messages, user_message=user_message
        )
        view_message(messages, model)
        view_response_stream(response_generator, raw=raw)


def conversation_command(conversation_name, model, prompt, stream):
    if stream:
        conversation_command_async(conversation_name, model, prompt)
    else:
        conversation_command_sync(conversation_name, model, prompt)


def conversation_command_async(conversation_name, model, prompt):
    username, mac_address = get_user_information()
    prompt = load_prompt(prompt)
    model = model or prompt["model"]
    conversation_path = (
        Path(CONVERSATIONS_DIR).expanduser() / f"{conversation_name}__{model}.json"
    )
    conversation = Datastore(conversation_path)
    session = load_session(conversation)
    key_bindings = load_key_bindings()
    view_conversation_async(
        conversation, key_bindings, mac_address, model, session, username
    )


def conversation_command_sync(conversation_name, model, prompt):
    username, mac_address = get_user_information()
    prompt = load_prompt(prompt)
    model = model or prompt["model"]
    conversation_path = (
        Path(CONVERSATIONS_DIR).expanduser() / f"{conversation_name}__{model}.json"
    )
    conversation = Datastore(conversation_path)
    session = load_session(conversation)
    key_bindings = load_key_bindings()
    view_conversation_sync(
        conversation, key_bindings, mac_address, model, session, username
    )


def delete_command(conversation_name, model, force):
    conversation_path = (
        Path(CONVERSATIONS_DIR).expanduser() / f"{conversation_name}__{model}.json"
    )

    if not conversation_path.is_file():
        click.echo(f"Conversation file not found: {conversation_path}")
    else:
        if not force:
            confirmation = click.confirm(
                f"Are you sure you want to delete the conversation '{conversation_name}' with model '{model}'?:"
            )
            if not confirmation:
                click.echo("Deletion canceled.")
                return

        try:
            conversation_path.unlink()
            click.echo(f"Conversation file deleted: {conversation_path}")
        except Exception as e:
            click.echo(f"Error deleting conversation file: {e}")


def draw_command(image_description, browser, size):
    username, _ = get_user_information()
    image_url = send_image(image_description, size)
    view_image(image_description, image_url, size)


def edit_command(filepath, model, raw):
    system_info = get_system_info()
    prompt = load_prompt("texteditor")
    session = load_session()
    key_bindings = load_key_bindings()
    model = model or prompt["model"]
    messages = prompt["messages"]
    file = Path(filepath).expanduser()
    file_content = file.read_text()
    file_content = f"```\n{file_content}\n```"
    user_message = {
        "role": "user",
        "name": system_info["login"],
        "mac_address": system_info["mac_address"],
        "content": file_content,
    }
    messages.append(user_message)
    view_edit_sync(
        file,
        key_bindings,
        system_info["mac_address"],
        messages,
        model,
        session,
        system_info["login"],
    )


def fork_command(source_conversation_name, new_conversation_name, model):
    source_conversation_file = (
        Path(CONVERSATIONS_DIR).expanduser()
        / f"{source_conversation_name}__{model}.json"
    )
    new_conversation_file = (
        Path(CONVERSATIONS_DIR).expanduser() / f"{new_conversation_name}__{model}.json"
    )
    if not source_conversation_file.is_file():
        click.echo(f"Source conversation file not found: {source_conversation_file}")
        return

    if new_conversation_file.is_file():
        click.echo(f"New conversation file already exists: {new_conversation_file}")
        return

    try:
        source_conversation = json.loads(source_conversation_file.read_text())
        new_conversation_file.write_text(json.dumps(source_conversation, indent=2))
        click.echo(
            f"Forked conversation '{source_conversation_name}' to '{new_conversation_name}' with model '{model}'"
        )
    except Exception as e:
        click.echo(f"Error forking conversation: {e}")


def list_command():
    conversation_files = Path(CONVERSATIONS_DIR).expanduser().glob("*__gpt-*.json")
    view_conversations(conversation_files)


def models_command():
    openai.api_key = os.environ["OPENAI_API_KEY"]
    response = openai.Model.list()
    models = [model["id"] for model in response["data"]]
    models.sort()

    click.echo("Available Models:")
    for model in models:
        click.echo(f"{model}")


def prompts_command():
    prompts = load_prompts()
    view_prompts(prompts)


def send_command_async(filepath, apply, interactive, raw):
    prompt = load_prompt(filepath=filepath)
    response_generator = send_chat_async(**prompt)
    view_messages(prompt["messages"], raw)
    content = view_response_stream(response_generator)
    if apply:
        prompt["messages"].append({"role": "assistant", "content": content})
        save_prompt(filepath=filepath, prompt=prompt)


def send_command_sync(filepath, apply, interactive, raw):
    prompt = load_prompt(filepath=filepath)
    system_info = get_system_info()
    model = prompt.get("model")
    messages = prompt.get("messages")
    user_message = {
        "mac_address": system_info["mac_address"],
        "name": system_info["login"],
    }
    view_messages(prompt["messages"], raw)
    get_api_data = lambda: send_chat_message_sync(model, messages, user_message)
    response = view_data_loader(fn=get_api_data)
    response_message = response.to_dict_recursive()
    response_message["content"] = re.sub(r" \n", "\n", response_message["content"])
    prompt["messages"].append(response_message)
    view_message(prompt["messages"][-1], raw)
    if not apply and interactive:
        click.echo("\n")
        apply = click.confirm("Would you like to apply the response?")
    if apply:
        save_prompt(filepath=filepath, prompt=prompt)


def send_command(filepath, apply, interactive, raw, stream):
    if stream:
        send_command_async(filepath, apply, interactive, raw)
    else:
        send_command_sync(filepath, apply, interactive, raw)
