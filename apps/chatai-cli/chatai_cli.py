#!/usr/bin/env python3

import argparse
import openai
import os
import json
from pathlib import Path
from tempfile import NamedTemporaryFile

VALID_ASK_MODELS = ["gpt-3.5-turbo", "gpt-4"]
VALID_CONVERSATION_MODELS = ["gpt-3.5-turbo", "gpt-4"]

def clear_screen():
    if(os.name == 'posix'):
        os.system('clear')
    else:
        os.system('cls')

def create_ask_completion(user_input, model):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    username = os.getlogin()

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "name": username,
                "content": f"{user_input}"
            }
        ]
    )

    return response

def create_conversation_completion(user_message, model, previous_messages):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    
    system_messages = [{"role": "system", "content": "You are a helpful assistant."}]
    
    messages = system_messages + previous_messages + [user_message]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages
    )

    return response

def open_conversation(conversation_name, model):
    conversation_dir = Path.home() / ".chatai/conversations"
    conversation_dir.mkdir(parents=True, exist_ok=True)
    conversation_file = conversation_dir / f"{conversation_name}_{model}.json"
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
            print(f"\n{message['name']} > {message['content']}\n")
    else:
        print(f"\n{message['content']}\n\n")
        print(f"-----")

def conversation_interactive(conversation_name, model, output_format):
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
            user_message = {
                "role": "user",
                "name": username,
                "content": f"{user_input}",
            }
            response = create_conversation_completion(user_message, model, conversation)
            choice = response["choices"][0]
            conversation.append(user_message)
            conversation.append(choice["message"].to_dict_recursive())
            conversation_file.write_text(json.dumps(conversation, indent=2))
            view_message(choice["message"])

        except Exception as e:
            print(f"Error: {e}")

def view_choice(choice):
    print("\nChatGPT Response:\n")
    print(choice["message"]["content"])

def main():
    parser = argparse.ArgumentParser(description="Ask questions to OpenAPI.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    ask_parser = subparsers.add_parser("ask", help="Ask a general question.")
    ask_parser.add_argument("user_input", type=str, help="User input to send to ChatGPT.")
    ask_parser.add_argument("-m", "--model", type=str, default=VALID_ASK_MODELS[0], choices=VALID_ASK_MODELS, help=f"Language model to use. Valid models: {', '.join(VALID_ASK_MODELS)}")
    ask_parser.add_argument("-o", "--output-format", type=str, default="text", choices=["text", "json"], help="Output format (text or json).")

    conversation_parser = subparsers.add_parser("conversation", help="Start an interactive conversation.")
    conversation_parser.add_argument("conversation_name", type=str, help="Name of the conversation.")
    conversation_parser.add_argument("-m", "--model", type=str, default=VALID_CONVERSATION_MODELS[0], choices=VALID_CONVERSATION_MODELS, help=f"Language model to use. Valid models: {', '.join(VALID_CONVERSATION_MODELS)}")
    conversation_parser.add_argument("-o", "--output-format", type=str, default="text", choices=["text", "json"], help="Output format (text or json).")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if "OPENAI_API_KEY" not in os.environ:
        os.environ["OPENAI_API_KEY"] = input("Enter your OpenAI API Key: ")

    if args.command == "ask":
        try:
            response = create_ask_completion(args.user_input, args.model)

            if args.output_format == "json":
                print(json.dumps({"input": args.user_input, "response": response}, indent=2))
            else:
                
                view_choice(response["choices"][0])
        except Exception as e:
            print(f"Error: {e}")

    elif args.command == "conversation":
            conversation_interactive(args.conversation_name, args.model, args.output_format)

if __name__ == "__main__":
    main()