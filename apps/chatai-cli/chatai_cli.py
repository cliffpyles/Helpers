#!/usr/bin/env python3

import openai
import os
import json
from pathlib import Path
from tempfile import NamedTemporaryFile
import webbrowser
import uuid
import yaml
import rich_click as click
from rich.console import Console
from rich.markdown import Markdown

console = Console()
script_dir = Path(__file__).resolve(strict=False).parent

VALID_ASK_MODELS = ["gpt-3.5-turbo", "gpt-4"]
VALID_CONVERSATION_MODELS = ["gpt-3.5-turbo", "gpt-4"]
VALID_SEND_MODELS = ["gpt-3.5-turbo", "gpt-4"]
PROMPTS_DIR = "./prompts"

def load_prompt(prop_name = "default"):
    prompt_configs = [yaml.safe_load(prompt.read_text()) for prompt in script_dir.glob("./prompts/*.yaml")]
    prompts = {}
    cleaned_promp_name = prop_name\
        .strip()\
        .replace('-','')\
        .replace('_','')\
        .replace(' ','')\
        .lower()
    for prompt_config in prompt_configs:
        keys = prompt_config.get("keys")
        model = prompt_config.get("model")
        messages = prompt_config.get("messages")

        for key in keys:
            prompts[key] = {
                "model": model,
                "messages": messages
            }

    if cleaned_promp_name in prompts:
        return prompts[cleaned_promp_name]
    else:
        return prompts["default"]


def bold_text(text):
    return "\033[1m" + text + "\033[0m"


def clear_screen():
    os.system('clear') if os.name == 'posix' else os.system('cls')


def get_conversation_file_path(conversation_name, model):
    conversation_dir = Path.home() / ".chatai/conversations"
    conversation_file = conversation_dir / f"{conversation_name}__{model}.json"
    return conversation_file


def get_conversations_directory():
    conversation_dir = Path.home() / ".chatai/conversations"
    return conversation_dir


def get_user_information():
    username = os.getlogin()
    mac_address = hex(uuid.getnode())
    return username, mac_address


def create_message(role, content, name=None):
    message = {
        "role": role,
        "content": content
    }
    if name:
        message["name"] = name
    return message


def create_system_message(prompt = "default"):
    if prompt in prompts:
        return create_message("system", prompts[prompt])
    else:
        return create_message("system", prompts["default"])


def create_user_message(username, content):
    return create_message("user", content, name=username)


def send_chat(**kwargs):
    response = openai.ChatCompletion.create(**kwargs)

    return response["choices"][0]["message"]


def send_chat_message(user_message, model, messages):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    username, mac_address = get_user_information()

    messages_without_id = []

    if user_message:
        messages.append(user_message)

    for message in messages:
        message_without_id = {
            "role": message["role"],
            "content": message["content"]
        }
        if "name" in message:
            message_without_id["name"] = message["name"]
        messages_without_id.append(message_without_id)

    messages = messages_without_id
    response_message = send_chat(
        model=model,
        messages=messages,
        user=f"{mac_address}::{username}"
    )

    return response_message


def open_conversation(conversation_name, model, messages):
    conversation_dir = Path.home() / ".chatai/conversations"
    conversation_dir.mkdir(parents=True, exist_ok=True)
    conversation_file = get_conversation_file_path(conversation_name, model)
    conversation = []

    if conversation_file.is_file():
        file_content = json.loads(conversation_file.read_text())
        conversation = file_content
        click.secho("Conversation file opened:", nl=False, bold=True)
        click.echo(conversation_file)
    else:
        conversation = []
        for message in messages:
            message["id"] = str(uuid.uuid4())
            conversation.append(message)

        conversation_file.touch()
        conversation_file.write_text(json.dumps(conversation))
        click.secho("Conversation file created:", nl=False, bold=True)
        click.echo(conversation_file)

    return conversation, conversation_file


def view_message(message):
    if message["role"] == "user":
        message_id = message.get('id', 'None')
        click.secho(f"User ({message_id}):", bold=True)
    elif message["role"] == "system":
        click.secho("System:", bold=True)
    else:
        message_id = message.get('id', 'None')
        click.secho(f"Response ({message_id}):", bold=True)
    markdown = Markdown(message['content'])
    console.print(markdown)


def view_messages(messages):
    for message in messages:
        view_message(message)


def ask_command(user_input, model, prompt):
    prompt = load_prompt(prompt)
    model = model or prompt["model"]
    openai.api_key = os.environ["OPENAI_API_KEY"]
    username, mac_address = get_user_information()
    messages = prompt["messages"]

    if user_input:
        messages.append(create_user_message(username, user_input))

    response_message = send_chat(
        model=model,
        messages=messages,
        user=f"{mac_address}::{username}"
    )

    view_messages(messages + [response_message])


def conversation_command(conversation_name, model, prompt):
    click.clear()

    click.echo("Entering an interactive conversation.")
    click.echo("Type 'exit' to end the conversation.")
    prompt = load_prompt(prompt)
    conversation_name = conversation_name
    model = model or prompt["model"]
    username, _ = get_user_information()
    conversation, conversation_file = open_conversation(conversation_name, model, prompt["messages"])

    if conversation[-1]["role"] != "assistant":
        response_message = send_chat_message(None, model, conversation)
        assistant_message_id = str(uuid.uuid4())
        assistant_message = response_message.to_dict_recursive()
        assistant_message["id"] = assistant_message_id
        conversation.append(assistant_message)
        conversation_file.write_text(json.dumps(conversation, indent=2))

    view_messages(conversation)

    while True:
        user_input = click.prompt(click.style("Message", bold=True))

        if user_input.lower() == "exit":
            break

        try:
            user_message_id = str(uuid.uuid4())
            user_message = {
                "id": user_message_id,
                "role": "user",
                "name": username,
                "content": f"{user_input}",
            }
            response_message = send_chat_message(user_message, model, conversation)
            assistant_message_id = str(uuid.uuid4())
            assistant_message = response_message.to_dict_recursive()
            assistant_message["id"] = assistant_message_id
            conversation.append(user_message)
            conversation.append(assistant_message)
            conversation_file.write_text(json.dumps(conversation, indent=2))
            view_message(assistant_message)

        except Exception as e:
            click.echo(f"Error: {e}")


def delete_command(conversation_name, model, force):
    conversation_name = conversation_name
    model = model
    conversation_file = get_conversation_file_path(conversation_name, model)

    if not conversation_file.is_file():
        click.echo(f"Conversation file not found: {conversation_file}")
    else:
        if not force:
            confirmation = click.confirm(f"Are you sure you want to delete the conversation '{conversation_name}' with model '{model}'?:")
            if not confirmation:
                click.echo("Deletion canceled.")
                return

        try:
            conversation_file.unlink()
            click.echo(f"Conversation file deleted: {conversation_file}")
        except Exception as e:
            click.echo(f"Error deleting conversation file: {e}")


def list_command():
    conversation_dir = get_conversations_directory()
    conversation_files = conversation_dir.glob("*__gpt-*.json")

    conversations = []
    for file in conversation_files:
        conversation_name, model = file.stem.split("__")
        conversations.append({"name": conversation_name, "model": model})

    if not conversations:
        click.echo("No existing conversations found.")
    else:
        click.echo("Existing conversations:")
        for conversation in conversations:
            click.echo(f"Name: {conversation['name']} | Model: {conversation['model']}")


def draw_command(image_description, browser, size):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    username, _ = get_user_information()
    response = openai.Image.create(
        prompt=f"{image_description}",
        n=1,
        size=f"{size}x{size}"
    )
    image_url = response['data'][0]['url']

    click.echo(f"Preview: {image_url}")

    if browser:
        webbrowser.open_new_tab(image_url)


def models_command():
    openai.api_key = os.environ["OPENAI_API_KEY"]
    response = openai.Model.list()
    models = [model["id"] for model in response["data"]]
    models.sort()

    click.echo("Available Models:")
    for model in models:
        click.echo(f"{model}")


def fork_command(source_conversation_name, new_conversation_name, model):
    source_conversation_file = get_conversation_file_path(source_conversation_name, model)
    new_conversation_file = get_conversation_file_path(new_conversation_name, model)

    if not source_conversation_file.is_file():
        click.echo(f"Source conversation file not found: {source_conversation_file}")
        return

    if new_conversation_file.is_file():
        click.echo(f"New conversation file already exists: {new_conversation_file}")
        return

    try:
        source_conversation = json.loads(source_conversation_file.read_text())
        new_conversation_file.write_text(json.dumps(source_conversation, indent=2))
        click.echo(f"Forked conversation '{source_conversation_name}' to '{new_conversation_name}' with model '{model}'")
    except Exception as e:
        click.echo(f"Error forking conversation: {e}")


def send_command(filepath, model, prompt):
    prompt = load_prompt(prompt)
    model = model or prompt["model"]
    openai.api_key = os.environ["OPENAI_API_KEY"]
    username, mac_address = get_user_information()
    file_input = Path(filepath)
    content = file_input.read_text()
    messages = prompt["messages"]

    messages.append(create_user_message(username, content))

    response_message = send_chat(
        model=model,
        messages=messages,
        user=f"{mac_address}::{username}"
    )

    view_message(response_message)


@click.group()
def main():
    """
    Ask questions to OpenAI.
    """
    pass


@main.command()
@click.argument("user_input", type=str, required=False)
@click.option("-m", "--model", type=click.Choice(VALID_ASK_MODELS), help=f"Language model to use. Valid models: {', '.join(VALID_ASK_MODELS)}")
@click.option("-p", "--prompt", type=str, default="default", help="Name of a preconfigured prompt to use")
def ask(user_input, model, prompt):
    ask_command(user_input, model, prompt)


@main.command()
@click.argument("conversation_name", type=str)
@click.option("-m", "--model", type=click.Choice(VALID_CONVERSATION_MODELS), help=f"Language model to use. Valid models: {', '.join(VALID_CONVERSATION_MODELS)}")
@click.option("-p", "--prompt", type=str, default="default", help="Name of a preconfigured prompt to use")
def conversation(conversation_name, model, prompt):
    conversation_command(conversation_name, model, prompt)


@main.command()
@click.argument("conversation_name", type=str)
@click.option("-m", "--model", type=click.Choice(VALID_CONVERSATION_MODELS), default=VALID_CONVERSATION_MODELS[0], help=f"Language model to use. Valid models: {', '.join(VALID_CONVERSATION_MODELS)}")
@click.option("-f", "--force", is_flag=True, help="Force deletion without confirmation.")
def delete(conversation_name, model, force):
    delete_command(conversation_name, model, force)


@main.command()
@click.argument("image_description", type=str)
@click.option("-b", "--browser", is_flag=True, help="Opens image in a new browser tab.")
@click.option("-s", "--size", type=click.Choice(["256", "512", "1024"]), default="256", help="Size of the image in pixels.")
def draw(image_description, browser, size):
    draw_command(image_description, browser, size)


@main.command()
@click.argument("source_conversation_name", type=str)
@click.argument("new_conversation_name", type=str)
@click.option("-m", "--model", type=click.Choice(VALID_CONVERSATION_MODELS), default=VALID_CONVERSATION_MODELS[0], help=f"Language model to use. Valid models: {', '.join(VALID_CONVERSATION_MODELS)}")
def fork(source_conversation_name, new_conversation_name, model):
    fork_command(source_conversation_name, new_conversation_name, model)


@main.command()
def list():
    list_command()


@main.command()
def models():
    models_command()


@main.command()
@click.argument("filepath", type=str)
@click.option("-m", "--model", type=click.Choice(VALID_SEND_MODELS), help=f"Language model to use. Valid models: {', '.join(VALID_SEND_MODELS)}")
@click.option("-p", "--prompt", type=str, default="default", help="Name of a preconfigured prompt to use")
def send(filepath, model, prompt):
    send_command(filepath, model, prompt)


if __name__ == "__main__":
    main()
