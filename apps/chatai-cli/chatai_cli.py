#!/usr/bin/env python3

import argparse
import openai
import os
import json
from pathlib import Path
from tempfile import NamedTemporaryFile
import webbrowser
import uuid

VALID_ASK_MODELS = ["gpt-3.5-turbo", "gpt-4"]
VALID_CONVERSATION_MODELS = ["gpt-3.5-turbo", "gpt-4"]


def clear_screen():
    if(os.name == 'posix'):
        os.system('clear')
    else:
        os.system('cls')


def ask_command(user_input, model):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    username = os.getlogin()
    mac_address = hex(uuid.getnode())
    file_input = Path(user_input)

    if file_input.is_file():
        content = file_input.read_text()
    else:
        content = user_input

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "name": username,
                "content": f"{content}"
            }
        ],
        user=f"{mac_address}::{username}"
    )

    view_choice(response["choices"][0])


def create_conversation_completion(user_message, model, previous_messages):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    username = os.getlogin()
    mac_address = hex(uuid.getnode())
    system_messages = [{"role": "system", "content": "You are a helpful assistant."}]
    
    messages = system_messages + previous_messages + [user_message]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        user=f"{mac_address}::{username}"
    )

    return response


def delete_command(conversation_name, model, force=False):
    conversation_dir = Path.home() / ".chatai/conversations"
    conversation_file = conversation_dir / f"{conversation_name}__{model}.json"

    if not conversation_file.is_file():
        print(f"\nConversation file not found: {conversation_file}\n")
    else:
        if not force:
            confirmation = input(f"\nAre you sure you want to delete the conversation '{conversation_name}' with model '{model}'? (y/n): ").lower()
            if confirmation != "y":
                print("\nDeletion canceled.\n")
                return

        try:
            conversation_file.unlink()
            print(f"\nConversation file deleted: {conversation_file}\n")
        except Exception as e:
            print(f"\nError deleting conversation file: {e}\n")


def open_conversation(conversation_name, model):
    conversation_dir = Path.home() / ".chatai/conversations"
    conversation_dir.mkdir(parents=True, exist_ok=True)
    conversation_file = conversation_dir / f"{conversation_name}__{model}.json"
    conversation = []

    if conversation_file.is_file():
        file_content = json.loads(conversation_file.read_text())
        conversation = conversation + file_content
        print(f"\nConversation file opened: {conversation_file}\n")
    else:
        conversation_file.touch()
        conversation_file.write_text("[]")
        print(f"\nConversation file created: {conversation_file}\n")

    return conversation, conversation_file


def view_message(message):
    
    if message["role"] == "user":
        print(f"\n> {message['name']} ({message['id']}):\n")
        print(f"\n{message['content']}\n")
    else:
        print(f"\n> {message['role']} ({message['id']}):\n")
        print(f"\n{message['content']}\n")
        print(f"\n-----\n\n")


def conversation_command(conversation_name, model):
    clear_screen()
    print("\nEntering an interactive conversation. \n\nType 'exit' to end the conversation.\n")
    username = os.getlogin()
    conversation, conversation_file = open_conversation(conversation_name, model)

    print("\n-----\n")

    for message in conversation:
        view_message(message)


    while True:
        user_input = input("Message: ")

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
            response = create_conversation_completion(user_message, model, conversation)
            choice = response["choices"][0]
            assistant_message_id = str(uuid.uuid4())
            assistant_message = choice["message"].to_dict_recursive()
            assistant_message["id"] = assistant_message_id
            conversation.append(user_message)
            conversation.append(assistant_message)
            conversation_file.write_text(json.dumps(conversation, indent=2))
            view_message(assistant_message)

        except Exception as e:
            print(f"Error: {e}")


def view_choice(choice):
    print("\nChatGPT Response:\n")
    print(choice["message"]["content"])


def list_command():
    conversation_dir = Path.home() / ".chatai/conversations"
    conversation_files = conversation_dir.glob("*__gpt-*.json")

    conversations = []
    for file in conversation_files:
        conversation_name, model = file.stem.split("__")
        conversations.append({"name": conversation_name, "model": model})

    if not conversations:
        print("\nNo existing conversations found.\n")
    else:
        print("Existing conversations:")
        for conversation in conversations:
            print(f"\nName: {conversation['name']} | Model: {conversation['model']}\n")


def draw_command(image_description, browser, size):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    username = os.getlogin()
    response = openai.Image.create(
        prompt=f"{image_description}",
        n=1,
        size=f"{size}x{size}"
    )
    image_url = response['data'][0]['url']

    print(f"Preview: {image_url}")

    if browser:
        webbrowser.open_new_tab(image_url)


def models_command():
    openai.api_key = os.environ["OPENAI_API_KEY"]
    response = openai.Model.list()
    models = [ model["id"] for model in response["data"] ]
    models.sort()

    print("\nAvailable Models:\n")
    for model in models:
        print(f"{model}")


def main():
    parser = argparse.ArgumentParser(description="Ask questions to OpenAPI.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    ask_parser = subparsers.add_parser("ask", help="Ask a general question.")
    ask_parser.add_argument("user_input", type=str, help="User input to send the API.")
    ask_parser.add_argument("-m", "--model", type=str, default=VALID_ASK_MODELS[0], choices=VALID_ASK_MODELS, help=f"Language model to use. Valid models: {', '.join(VALID_ASK_MODELS)}")

    conversation_parser = subparsers.add_parser("conversation", help="Start an interactive conversation.")
    conversation_parser.add_argument("conversation_name", type=str, help="Name of the conversation.")
    conversation_parser.add_argument("-m", "--model", type=str, default=VALID_CONVERSATION_MODELS[0], choices=VALID_CONVERSATION_MODELS, help=f"Language model to use. Valid models: {', '.join(VALID_CONVERSATION_MODELS)}")

    delete_parser = subparsers.add_parser("delete", help="Delete a conversation.")
    delete_parser.add_argument("conversation_name", type=str, help="Name of the conversation to delete.")
    delete_parser.add_argument("-m", "--model", type=str, default=VALID_CONVERSATION_MODELS[0], choices=VALID_CONVERSATION_MODELS, help=f"Language model to use. Valid models: {', '.join(VALID_CONVERSATION_MODELS)}")
    delete_parser.add_argument("-f", "--force", action="store_true", help="Force deletion without confirmation.")

    draw_parser = subparsers.add_parser("draw", help="Draw an image based on a description.")
    draw_parser.add_argument("image_description", type=str, help="Description of the image.")
    draw_parser.add_argument("-b", "--browser", action="store_true", help="Opens image in a new browser tab.")
    draw_parser.add_argument("-s", "--size", type=str, default="256", choices=["256", "512", "1024"], help="Size of the image in pixels.")

    list_parser = subparsers.add_parser("list", help="List existing conversations.")

    models_parser = subparsers.add_parser("models")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if "OPENAI_API_KEY" not in os.environ:
        os.environ["OPENAI_API_KEY"] = input("Enter your OpenAI API Key: ")

    if args.command == "ask":
        ask_command(args.user_input, args.model)

    elif args.command == "conversation":
        conversation_command(args.conversation_name, args.model)

    elif args.command == "delete":
        delete_command(args.conversation_name, args.model, args.force)

    elif args.command == "draw":
        draw_command(args.image_description, args.browser, args.size)

    elif args.command == "list":
        list_command()

    elif args.command == "models":
        models_command()


if __name__ == "__main__":
    main()