import rich_click as click
from utils import *
import time
import io

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


def view_conversation_async(conversation, key_bindings, mac_address, model, session, username):
    click.clear()
    click.echo("Entering an interactive conversation.")
    click.echo("Type 'exit' to end the conversation.")
    view_messages(conversation.get_items())
    view_message_input(conversation, key_bindings, mac_address, model, session, username)


def view_conversation_sync(conversation, key_bindings, mac_address, model, session, username):
    click.clear()
    click.echo("Entering an interactive conversation.")
    click.echo("Type 'exit' to end the conversation.")
    view_messages(conversation.get_items())
    view_message_input(conversation, key_bindings, mac_address, model, session, username)


def view_image(image_description, image_url, size):
    render_text(f"Description: {image_description}\n")
    render_text(f"Size: {size}x{size}\n")
    render_text(f"Preview URL: {image_url}\n")
    render_image(image_url)


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
                response_message = send_chat_message_sync(model, messages, user_message)
                assistant_message = response_message.to_dict_recursive()
                conversation.create_item(assistant_message)
                view_message(assistant_message)
                current_state["multiline_mode"] = False

            except Exception as e:
                click.echo(f"Error: {e}")


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


def view_response_stream(response_generator):
    all_lines = ''
    line = ''
    for message in response_generator:
        finish_reason = message["choices"][0]["finish_reason"]
        if finish_reason == 'stop':
            print(line)
            break
        else:
            delta = message["choices"][0]["delta"]
            content = delta.get('content', '')
            line += content
            all_lines += content
            if '\n' in content:
                print(line)
                line = ''
    return all_lines
    


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
