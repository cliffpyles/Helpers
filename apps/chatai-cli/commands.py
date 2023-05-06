from utils import *
from constants import *
from views import *
from lib.datastore import Datastore
from pathlib import Path

def ask_command(user_input, model, prompt):
    username, mac_address = get_user_information()
    prompt = load_prompt(prompt)
    model = model or prompt["model"]
    username, mac_address = get_user_information()
    messages = prompt["messages"]

    if user_input:
        user_message = {
            "role": "user",
            "name": username,
            "mac_address": mac_address,
            "content": user_input
        }
        response_message = send_chat_message(
            model=model,
            messages=messages,
            user_message=user_message
        )
        messages.append(user_message)
        messages.append(response_message)

    view_messages(messages)


def conversation_command(conversation_name, model, prompt):
    username, mac_address = get_user_information()
    prompt = load_prompt(prompt)
    model = model or prompt["model"]
    conversation_path = Path(CONVERSATIONS_DIR).expanduser() / f"{conversation_name}__{model}.json"
    conversation = Datastore(conversation_path)
    session = load_session(conversation)
    key_bindings = load_key_bindings()
    view_conversation(conversation, key_bindings, mac_address, model, session, username)


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


def send_command(filepath, model, prompt):
    prompt = load_prompt(prompt)
    model = model or prompt["model"]
    openai.api_key = os.environ["OPENAI_API_KEY"]
    username, mac_address = get_user_information()
    file_input = Path(filepath)
    content = file_input.read_text()
    messages = prompt["messages"]

    messages.append(create_message("user", username, content))

    response_message = send_chat(
        model=model, messages=messages, user=f"{mac_address}::{username}"
    )

    view_message(response_message)
