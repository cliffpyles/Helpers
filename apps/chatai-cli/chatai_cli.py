#!/usr/bin/env python3

import rich_click as click
from commands import *
from constants import *

@click.group()
def main():
    pass


@main.command()
@click.argument("user_input", type=str, required=False)
@click.option(
    "-m",
    "--model",
    type=click.Choice(VALID_ASK_MODELS),
    help=f"Language model to use. Valid models: {', '.join(VALID_ASK_MODELS)}",
)
@click.option(
    "-p",
    "--prompt",
    type=str,
    default="default",
    help="Name of a preconfigured prompt to use",
)
def ask(user_input, model, prompt):
    """Ask a single question to the chatbot"""
    ask_command(user_input, model, prompt)


@main.command()
@click.argument("conversation_name", type=str)
@click.option(
    "-m",
    "--model",
    type=click.Choice(VALID_CONVERSATION_MODELS),
    help=f"Language model to use. Valid models: {', '.join(VALID_CONVERSATION_MODELS)}",
)
@click.option(
    "-p",
    "--prompt",
    type=str,
    default="default",
    help="Name of a preconfigured prompt to use",
)
def conversation(conversation_name, model, prompt):
    """Start an ongoing conversation with the chatbot"""
    conversation_command(conversation_name, model, prompt)


@main.command()
@click.argument("conversation_name", type=str)
@click.option(
    "-m",
    "--model",
    type=click.Choice(VALID_CONVERSATION_MODELS),
    default=VALID_CONVERSATION_MODELS[0],
    help=f"Language model to use. Valid models: {', '.join(VALID_CONVERSATION_MODELS)}",
)
@click.option(
    "-f", "--force", is_flag=True, help="Force deletion without confirmation."
)
def delete(conversation_name, model, force):
    """Delete a conversation"""
    delete_command(conversation_name, model, force)


@main.command()
@click.argument("image_description", type=str)
@click.option("-b", "--browser", is_flag=True, help="Opens image in a new browser tab.")
@click.option(
    "-s",
    "--size",
    type=click.Choice(["256", "512", "1024"]),
    default="256",
    help="Size of the image in pixels.",
)
def draw(image_description, browser, size):
    """Draw an image based on a description"""
    draw_command(image_description, browser, size)


@main.command()
@click.argument("source_conversation_name", type=str)
@click.argument("new_conversation_name", type=str)
@click.option(
    "-m",
    "--model",
    type=click.Choice(VALID_CONVERSATION_MODELS),
    default=VALID_CONVERSATION_MODELS[0],
    help=f"Language model to use. Valid models: {', '.join(VALID_CONVERSATION_MODELS)}",
)
def fork(source_conversation_name, new_conversation_name, model):
    """Duplicate an existing conversation"""
    fork_command(source_conversation_name, new_conversation_name, model)

@main.command()
def list():
    """List existing conversations"""
    list_command()

@main.command()
def models():
    """Show the available models"""
    models_command()


@main.command()
@click.argument("filepath", type=str)
@click.option(
    "-m",
    "--model",
    type=click.Choice(VALID_SEND_MODELS),
    help=f"Language model to use. Valid models: {', '.join(VALID_SEND_MODELS)}",
)
@click.option(
    "-p",
    "--prompt",
    type=str,
    default="default",
    help="Name of a preconfigured prompt to use",
)
def send(filepath, model, prompt):
    """Send the contents of a file to the chatbot"""
    send_command(filepath, model, prompt)


@main.command()
def prompts():
    """Lists preconfigured prompts"""
    prompts_command()


@main.command()
@click.argument("filepath", type=str)
@click.option("-r", "--raw", is_flag=True, help="Show the raw content")
@click.option("-s", "--save", is_flag=True, help="Save responses to the file")
def prompt(filepath, raw, save):
    """Executes the prompt at the given filepath"""
    prompt_command(filepath, raw, save)


@main.command()
@click.argument("filepath", type=str)
def send(filepath, model, prompt):
    """Send the contents of a file to the chatbot"""
    send_command(filepath, model, prompt)


if __name__ == "__main__":
    main()
