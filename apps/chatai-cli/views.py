import random
import time
import rich
import rich_click as click
from rich.progress import Progress, TimeElapsedColumn, SpinnerColumn
from rich.console import Console
from rich.markdown import Markdown
from utils import *
from constants import *


def view_conversations(conversation_files):
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


def view_conversation_sync(
    conversation, key_bindings, mac_address, model, session, username
):
    def view_conversation_banner():
        click.clear()
        click.echo("Entering an interactive conversation.")
        click.echo("Type 'exit' to end the conversation.")
    
    def on_after_add_item(new_message):
        view_message(new_message)
    
    def on_after_remove_item(item):
        view_conversation_banner()
        view_messages(conversation.get_items())

    conversation.register_event_hook("after", "add_item", on_after_add_item)
    conversation.register_event_hook("after", "remove_item", on_after_remove_item)

    view_conversation_banner()
    view_messages(conversation.get_items())

    current_state = {
        "mac_address": mac_address,
        "model": model,
        "multiline_mode": False,
        "username": username,
    }
    

    while True:

        # if conversation.last_item().get("role") == "user":
        #     messages = conversation.get_items()
        #     response_message = send_messages_sync(model, messages)
        #     assistant_message = response_message.to_dict_recursive()
        #     conversation.add_item(assistant_message)

        user_input = session.prompt(
            message=f"\n\n{MESSAGE_INDICATOR} New Message: ",
            key_bindings=key_bindings,
            multiline=current_state.get("multiline_mode", False),
            wrap_lines=True,
        )

        # Execute the command if the input starts with a '/'
        if user_input.startswith("/"):
            conversation, current_state, user_input = execute_conversation_command(
                user_input,
                conversation=conversation,
                current_state=current_state,
                user_input=user_input,
            )
            if "notifications" in current_state:
                for notification in current_state["notifications"]:
                    click.echo(notification)
                del current_state["notifications"]
        elif len(user_input.strip()) > 0:
            try:
                user_message = conversation.add_item(
                    {
                        "role": "user",
                        "name": username,
                        "content": f"{user_input}",
                        "mac_address": mac_address,
                    }
                )
                messages = conversation.get_items()
                response_message = send_chat_message_sync(model, messages, user_message)
                assistant_message = response_message.to_dict_recursive()
                conversation.add_item(assistant_message)
                current_state["multiline_mode"] = False

            except Exception as e:
                click.echo(f"Error: {e}")



def view_data_loader(fn, **kwargs):
    with Progress(
        SpinnerColumn(),
        TimeElapsedColumn(),
    ) as progress:
        loading_task = progress.add_task("[green]Processing…", total=None)
        response = fn()
        progress.update(loading_task, completed=True, visible=False)

    return response


def view_image(image_description, image_url, size):
    render_text(f"Description: {image_description}\n")
    render_text(f"Size: {size}x{size}\n")
    render_text(f"Preview URL: {image_url}\n")
    render_image(image_url)
    

def view_message(message, raw=False):
    console = Console()
    if message["role"] == "user":
        message_id = message.get("id", "None")
        click.secho(f"\n\n{MESSAGE_INDICATOR} Message ({message_id}):\n", bold=True)
    elif message["role"] == "system":
        click.secho(f"\n\n{SYSTEM_INDICATOR} System:\n", bold=True)
    elif message["role"] == "assistant":
        message_id = message.get("id", "None")
        click.secho(f"\n\n{RESPONSE_INDICATOR} Response ({message_id}):\n", bold=True)

    if raw:
        click.echo(message["content"])
    else:
        markdown = Markdown(message["content"])
        console.print(markdown)


def view_messages(messages, raw=False):
    for message in messages:
        view_message(message, raw)


def view_prompts(prompts):
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


def view_response_stream(response_generator, raw=False):
    console = Console()
    all_lines = ""
    line = ""
    if not raw:
        click.secho(f"\n\n{RESPONSE_INDICATOR} Response:\n", bold=True)
    for message in response_generator:
        finish_reason = message["choices"][0]["finish_reason"]
        if finish_reason == "stop":
            click.echo(line)
            break
        else:
            delta = message["choices"][0]["delta"]
            content = delta.get("content", "")
            line += content
            all_lines += content
            if "\n" in content:
                click.echo(line)
                line = ""
    return all_lines
