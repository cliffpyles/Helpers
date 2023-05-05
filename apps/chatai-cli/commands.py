from utils import *


def ask_command(user_input, model, prompt):
    prompt = load_prompt(prompt)
    model = model or prompt["model"]
    username, mac_address = get_user_information()
    messages = prompt["messages"]

    if user_input:
        messages.append(create_message("user", username, user_input))

    response_message = send_chat(
        model=model, messages=messages, user=f"{mac_address}::{username}"
    )

    view_messages(messages + [response_message])


def conversation_command(conversation_name, model, prompt):
    username, _ = get_user_information()
    prompt = load_prompt(prompt)
    model = model or prompt["model"]
    conversation_path = get_conversation_path(conversation_name, model)
    conversation, conversation_file = open_conversation(
        conversation_path, prompt["messages"]
    )
    view_conversation(conversation, conversation_file, model)


def delete_command(conversation_name, model, force):
    conversation_name = conversation_name
    model = model
    conversation_file = get_conversation_path(conversation_name, model)

    if not conversation_file.is_file():
        click.echo(f"Conversation file not found: {conversation_file}")
    else:
        if not force:
            confirmation = click.confirm(
                f"Are you sure you want to delete the conversation '{conversation_name}' with model '{model}'?:"
            )
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


def prompts_command():
    prompts = load_prompts()

    if not prompts:
        click.echo("No available prompts.")
    else:
        content = "Available Prompts:\n\n"
        for prompt in prompts:
            keys = prompt.get("keys")
            model = prompt.get("model")
            messages = prompt.get("messages")

            content += indent_text(f"Name: {keys[0]}", max_width=120)
            content += "\n\n"
            content += indent_text(f"Aliases: {', '.join(keys[1:])}", max_width=120)
            content += "\n\n"
            content += indent_text(f"Default Model: {model}", max_width=120)
            content += "\n\n"
            content += indent_text(
                f"System Context:\n{messages[0]['content']}", max_width=120
            )
            content += "\n\n"
            content += indent_text("-" * 40)
            content += "\n\n"

        click.echo_via_pager(content)


def draw_command(image_description, browser, size):
    username, _ = get_user_information()
    image_url = send_image(image_description, size)

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
