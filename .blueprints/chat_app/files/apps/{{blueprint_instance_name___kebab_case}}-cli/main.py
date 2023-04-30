#!/usr/bin/env python3

import click
from pathlib import Path
from config_loader import load_config
from prompt_handler import display_prompts
from gpt_chat import chat_with_gpt
from click_options import generate_options
from command_utils import construct_command

def main(**kwargs):
    """
    Main function for the application.
    """
    # Load configuration
    file_path = kwargs.pop('file', None) or config_file_path
    config = load_config(str(file_path))
    
    # Display prompts to the user and collect their responses
    responses = display_prompts(config["prompts"], kwargs)

    # Send messages to ChatGPT and display the response
    chatgpt_response = chat_with_gpt(config, responses)
    click.echo(chatgpt_response)

    # Show the command to reproduce this interaction
    command = construct_command(config, responses)
    click.echo("\nCommand:")
    click.echo(command)
    click.echo("\n")

# Set the script directory and configuration file path
script_dir = Path(__file__).resolve(strict=False).parent
config_file_path = script_dir / './config.yaml'

# Load the configuration
config = load_config(str(config_file_path))

# Generate command line options using the configuration
options = generate_options(config["prompts"])

# Create a Click command with the main function and options
main = click.Command('main', callback=main, params=options)

# Execute the main function when the script is run
if __name__ == '__main__':
    main()
