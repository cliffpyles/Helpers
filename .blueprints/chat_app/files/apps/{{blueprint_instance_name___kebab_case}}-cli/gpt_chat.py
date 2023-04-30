import openai
import sys

def chat_with_gpt(config, responses):
    """
    Interacts with the GPT-3.5-turbo model based on the provided config and user responses.

    :param config: The loaded configuration dictionary containing prompts and other settings.
    :param responses: The user responses dictionary.
    :return: A tuple containing the GPT model's response and the command string to reproduce the context.
    """

    # Initialize the messages list with the system message
    messages = [{"role": "system", "content": config["context"]}]

    # Add user responses as separate messages
    for k, v in responses.items():
        for prompt in config["prompts"]:
            prompt_key = prompt.get('key')
            prompt_type = prompt['type']
            response = responses[k]

            if k == prompt_key and prompt_type == 'file' and response.strip() != "":
                messages.append({"role": "user", "content": f"{k}_path: {v}"})
                messages.append({"role": "user", "content": f"{k}: {responses[f'{k}_content']}"})
            elif k == prompt_key:
                messages.append({"role": "user", "content": f"{k}: {v}"})

    # Add predefined messages from the configuration
    for message in config["messages"]:
        messages.append({"role": "user", "content": message})

    # Send messages to ChatGPT and return the response
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    chatgpt_response = response.choices[0].message['content'].strip()
    return chatgpt_response
