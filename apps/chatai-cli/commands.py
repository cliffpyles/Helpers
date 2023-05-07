# Filename: commands.py

from utils import *
from constants import *
from views import *
from lib.datastore import Datastore
from pathlib import Path

def ask_command(user_input, model, prompt, stream):
    if (stream):
        ask_command_async(user_input, model, prompt)
    else:
        ask_command_sync(user_input, model, prompt)


def ask_command_sync(user_input, model, prompt):
    username, mac_address = get_user_information()
    prompt = load_prompt(prompt)
    model = model or prompt["model"]
    messages = prompt["messages"]

    if user_input:
        user_message = {
            "role": "user",
            "name": username,
            "mac_address": mac_address,
            "content": user_input
        }
        get_api_data = lambda: send_chat_message_sync(
            model=model,
            messages=messages,
            user_message=user_message
        )
        response_message = view_data_loader(fn=get_api_data)
        messages.append(user_message)
        messages.append(response_message)
    
    view_messages(messages)
    

def ask_command_async(user_input, model, prompt):
    username, mac_address = get_user_information()
    prompt = load_prompt(prompt)
    model = model or prompt["model"]
    messages = prompt["messages"]

    view_messages(messages)

    if user_input:
        user_message = {
            "role": "user",
            "name": username,
            "mac_address": mac_address,
            "content": user_input
        }
        response_generator = send_chat_message_async(
            model=model,
            messages=messages,
            user_message=user_message
        )
        view_message(user_message)
        view_response_stream(response_generator)
    

def conversation_command(conversation_name, model, prompt, stream):
    if stream:
        conversation_command_async(conversation_name, model, prompt)
    else:
        conversation_command_sync(conversation_name, model, prompt)


def conversation_command_async(conversation_name, model, prompt):
    username, mac_address = get_user_information()
    prompt = load_prompt(prompt)
    model = model or prompt["model"]
    conversation_path = Path(CONVERSATIONS_DIR).expanduser() / f"{conversation_name}__{model}.json"
    conversation = Datastore(conversation_path)
    session = load_session(conversation)
    key_bindings = load_key_bindings()
    view_conversation_async(conversation, key_bindings, mac_address, model, session, username)


def conversation_command_sync(conversation_name, model, prompt):
    username, mac_address = get_user_information()
    prompt = load_prompt(prompt)
    model = model or prompt["model"]
    conversation_path = Path(CONVERSATIONS_DIR).expanduser() / f"{conversation_name}__{model}.json"
    conversation = Datastore(conversation_path)
    session = load_session(conversation)
    key_bindings = load_key_bindings()
    view_conversation_sync(conversation, key_bindings, mac_address, model, session, username)


def delete_command(conversation_name, model, force):
    conversation_path = Path(CONVERSATIONS_DIR).expanduser() / f"{conversation_name}__{model}.json"

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


def list_command():
    conversation_files = Path(CONVERSATIONS_DIR).expanduser().glob("*__gpt-*.json")
    view_conversations(conversation_files)    


def prompts_command():
    prompts = load_prompts()
    view_prompts(prompts)
    

def draw_command(image_description, browser, size):
    username, _ = get_user_information()
    image_url = send_image(image_description, size)
    view_image(image_description, image_url, size)


def models_command():
    openai.api_key = os.environ["OPENAI_API_KEY"]
    response = openai.Model.list()
    models = [model["id"] for model in response["data"]]
    models.sort()

    click.echo("Available Models:")
    for model in models:
        click.echo(f"{model}")


def fork_command(source_conversation_name, new_conversation_name, model):
    source_conversation_file = get_conversation_path(source_conversation_name, model)
    new_conversation_file = get_conversation_path(new_conversation_name, model)

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


def analyze_command(filepath, model, prompt):
    username, mac_address = get_user_information()
    prompt = load_prompt(prompt)
    model = model or prompt["model"]
    username, mac_address = get_user_information()
    messages = prompt["messages"]
    file_content = Path(filepath).read_text()
    if file_content:
        user_message = {
            "role": "user",
            "name": username,
            "mac_address": mac_address,
            "content": file_content
        }
        response_message = send_chat_message_sync(
            model=model,
            messages=messages,
            user_message=user_message
        )
        messages.append(user_message)
        messages.append(response_message)
    view_messages(messages)


def send_command_async(filepath, raw, update):
    prompt = load_prompt(filepath=filepath)
    response_generator = send_chat_async(**prompt)
    view_messages(prompt["messages"], raw)
    content = view_response_stream(response_generator)
    if (update):
        prompt["messages"].append({
            "role": "assistant",
            "content": content
        })
        save_prompt(filepath=filepath, prompt=prompt)


def send_command_sync(filepath, raw, update):
    prompt = load_prompt(filepath=filepath)
    get_api_data = lambda: send_chat_sync(**prompt)
    response_message = view_data_loader(fn=get_api_data)
    prompt["messages"].append(response_message)

    if (update):
        save_prompt(filepath=filepath, prompt=prompt)
    view_messages(prompt["messages"], raw)


def send_command(filepath, raw, update, stream):
    if (stream):
        send_command_async(filepath, raw, update)
    else:
        send_command_sync(filepath, raw, update)
