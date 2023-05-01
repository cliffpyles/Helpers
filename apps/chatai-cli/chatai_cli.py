#!/usr/bin/env python3

import argparse
import openai
import os
import json
from pathlib import Path
from tempfile import NamedTemporaryFile
import webbrowser
import uuid
import yaml

script_dir = Path(__file__).resolve(strict=False).parent

VALID_ASK_MODELS = ["gpt-3.5-turbo", "gpt-4"]
VALID_CONVERSATION_MODELS = ["gpt-3.5-turbo", "gpt-4"]
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
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        user=f"{mac_address}::{username}"
    )

    return response


def open_conversation(conversation_name, model, messages):
    conversation_dir = Path.home() / ".chatai/conversations"
    conversation_dir.mkdir(parents=True, exist_ok=True)
    conversation_file = get_conversation_file_path(conversation_name, model)
    conversation = []

    if conversation_file.is_file():
        file_content = json.loads(conversation_file.read_text())
        conversation = file_content
        print(f"\nConversation file opened: {conversation_file}\n")
    else:
        # file_content = create_system_message(prompt)
        # file_content["id"] = str(uuid.uuid4())
        conversation = []
        for message in messages:
            message["id"] = str(uuid.uuid4())
            conversation.append(message)

        conversation_file.touch()
        conversation_file.write_text(json.dumps(conversation))
        print(f"\nConversation file created: {conversation_file}\n")
        # view_message(file_content)

    return conversation, conversation_file


def view_message(message):
    if message["role"] == "user":
        label = bold_text(f"User ({message['id']}):")
        print(f"\n{label}:\n\n{message['content']}\n")
    elif message["role"] == "system":
        label = bold_text("System:")
        print(f"\n{label}\n\n{message['content']}\n")
    else:
        label = bold_text(f"Response ({message['id']}):")
        print(f"\n{label}\n\n{message['content']}\n")
        

def view_choice(choice):
    print("\nChatGPT Response:\n")
    print(choice["message"]["content"])


def ask_command(args):
    prompt = load_prompt(args.prompt)
    user_input = args.user_input
    model = args.model or prompt["model"]
    openai.api_key = os.environ["OPENAI_API_KEY"]
    username, mac_address = get_user_information()
    file_input = Path(user_input)
    content = file_input.read_text() if file_input.is_file() else user_input
    messages = prompt["messages"]
    
    if user_input.strip().lower() in ["", "none", "help"]:
        messages.append(create_user_message(username, content))

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        user=f"{mac_address}::{username}"
    )

    view_choice(response["choices"][0])


def conversation_command(args):
    clear_screen()
    print("\nEntering an interactive conversation. \n\nType 'exit' to end the conversation.\n")
    prompt = load_prompt(args.prompt)
    conversation_name = args.conversation_name
    model = args.model or prompt["model"]
    username, _ = get_user_information()
    conversation, conversation_file = open_conversation(conversation_name, model, prompt["messages"])

    if conversation[-1]["role"] != "assistant":
        response = send_chat_message(None, model, conversation)
        choice = response["choices"][0]
        assistant_message_id = str(uuid.uuid4())
        assistant_message = choice["message"].to_dict_recursive()
        assistant_message["id"] = assistant_message_id
        conversation.append(assistant_message)
        conversation_file.write_text(json.dumps(conversation, indent=2))


    for message in conversation:
        view_message(message)


    while True:
        user_input = input(bold_text("Message: "))

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
            response = send_chat_message(user_message, model, conversation)
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


def delete_command(args):
    conversation_name = args.conversation_name
    model = args.model
    force = args.force
    conversation_file = get_conversation_file_path(conversation_name, model)

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


def list_command(args):
    conversation_dir = get_conversations_directory()
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


def draw_command(args):
    image_description = args.image_description
    browser = args.browser
    size = args.size
    openai.api_key = os.environ["OPENAI_API_KEY"]
    username, _ = get_user_information()
    response = openai.Image.create(
        prompt=f"{image_description}",
        n=1,
        size=f"{size}x{size}"
    )
    image_url = response['data'][0]['url']

    print(f"Preview: {image_url}")

    if browser:
        webbrowser.open_new_tab(image_url)


def models_command(args):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    response = openai.Model.list()
    models = [model["id"] for model in response["data"]]
    models.sort()

    print("\nAvailable Models:\n")
    for model in models:
        print(f"{model}")


def fork_command(args):
    source_conversation_name = args.source_conversation_name
    new_conversation_name = args.new_conversation_name
    model = args.model
    source_conversation_file = get_conversation_file_path(source_conversation_name, model)
    new_conversation_file = get_conversation_file_path(new_conversation_name, model)

    if not source_conversation_file.is_file():
        print(f"\nSource conversation file not found: {source_conversation_file}\n")
        return

    if new_conversation_file.is_file():
        print(f"\nNew conversation file already exists: {new_conversation_file}\n")
        return

    try:
        source_conversation = json.loads(source_conversation_file.read_text())
        new_conversation_file.write_text(json.dumps(source_conversation, indent=2))
        print(f"\nForked conversation '{source_conversation_name}' to '{new_conversation_name}' with model '{model}'\n")
    except Exception as e:
        print(f"\nError forking conversation: {e}\n")


def configure_subparsers(subparsers):
    ask_parser = subparsers.add_parser("ask", help="Ask a general question.")
    ask_parser.add_argument("user_input", type=str, help="User input to send the API.")
    ask_parser.add_argument("-m", "--model", type=str, choices=VALID_ASK_MODELS, help=f"Language model to use. Valid models: {', '.join(VALID_ASK_MODELS)}")
    ask_parser.add_argument("-p", "--prompt", type=str, default="default", help="Name of a preconfigured prompt to use")

    conversation_parser = subparsers.add_parser("conversation", help="Start an interactive conversation.")
    conversation_parser.add_argument("conversation_name", type=str, help="Name of the conversation.")
    conversation_parser.add_argument("-m", "--model", type=str, choices=VALID_CONVERSATION_MODELS, help=f"Language model to use. Valid models: {', '.join(VALID_CONVERSATION_MODELS)}")
    conversation_parser.add_argument("-p", "--prompt", type=str, default="default", help="Name of a preconfigured prompt to use")

    delete_parser = subparsers.add_parser("delete", help="Delete a conversation.")
    delete_parser.add_argument("conversation_name", type=str, help="Name of the conversation to delete.")
    delete_parser.add_argument("-m", "--model", type=str, default=VALID_CONVERSATION_MODELS[0], choices=VALID_CONVERSATION_MODELS, help=f"Language model to use. Valid models: {', '.join(VALID_CONVERSATION_MODELS)}")
    delete_parser.add_argument("-f", "--force", action="store_true", help="Force deletion without confirmation.")

    draw_parser = subparsers.add_parser("draw", help="Draw an image based on a description.")
    draw_parser.add_argument("image_description", type=str, help="Description of the image.")
    draw_parser.add_argument("-b", "--browser", action="store_true", help="Opens image in a new browser tab.")
    draw_parser.add_argument("-s", "--size", type=str, default="256", choices=["256", "512", "1024"], help="Size of the image in pixels.")

    fork_parser = subparsers.add_parser("fork", help="Fork a conversation.")
    fork_parser.add_argument("source_conversation_name", type=str, help="Name of the conversation to fork.")
    fork_parser.add_argument("new_conversation_name", type=str, help="Name of the new forked conversation.")
    fork_parser.add_argument("-m", "--model", type=str, default=VALID_CONVERSATION_MODELS[0], choices=VALID_CONVERSATION_MODELS, help=f"Language model to use. Valid models: {', '.join(VALID_CONVERSATION_MODELS)}")

    list_parser = subparsers.add_parser("list", help="List existing conversations.")

    models_parser = subparsers.add_parser("models")


def main():
    parser = argparse.ArgumentParser(description="Ask questions to OpenAPI.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    configure_subparsers(subparsers)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if "OPENAI_API_KEY" not in os.environ:
        os.environ["OPENAI_API_KEY"] = input("Enter your OpenAI API Key: ")

    command_mapper = {
        "ask": ask_command,
        "conversation": conversation_command,
        "delete": delete_command,
        "draw": draw_command,
        "fork": fork_command,
        "list": list_command,
        "models": models_command,
    }

    command_mapper[args.command](args)


if __name__ == "__main__":
    main()