#!/usr/bin/env python3

import json
import yaml
import click
import inquirer


def load_config(file_path):
    with open(file_path, 'r') as config_file:
        if file_path.endswith('.json'):
            return json.load(config_file)
        elif file_path.endswith('.yml') or file_path.endswith('.yaml'):
            return yaml.safe_load(config_file)
        else:
            raise ValueError('Invalid file format. Use JSON or YAML.')


def display_prompts(config, arguments):
    questions = []

    for prompt in config:
        prompt_key = prompt.get('key')
        prompt_type = prompt['type']
        kwargs = prompt['kwargs']

        if prompt_key and arguments.get(prompt_key) is not None:
            # Use the value passed as an argument
            continue

        if prompt_type == 'text':
            question = inquirer.Text(**kwargs)
        elif prompt_type == 'checkbox':
            question = inquirer.Checkbox(**kwargs)
        elif prompt_type == 'radio':
            question = inquirer.List(**kwargs)
        elif prompt_type == 'range':
            question = inquirer.Slider(**kwargs)
        elif prompt_type == 'autocomplete':
            question = inquirer.autocomplete.AutoComplete(**kwargs)
        else:
            raise ValueError(f'Invalid prompt type: {prompt_type}')

        questions.append(question)

    user_responses = inquirer.prompt(questions)
    responses = {**arguments, **user_responses}
    return {k: v for k, v in responses.items() if v is not None}


def generate_options(config):
    options = []

    for prompt in config:
        prompt_key = prompt.get('key')
        prompt_type = prompt['type']

        if prompt_key:
            if prompt_type == 'radio':
                choices = prompt['kwargs']['choices']
                option = click.Option(param_decls=[f'--{prompt_key}'],
                                      type=click.Choice(choices, case_sensitive=False),
                                      help=f'Pass your {prompt_key} preference as an argument.')
            else:
                option = click.Option(param_decls=[f'--{prompt_key}'],
                                      type=str,
                                      help=f'Pass your {prompt_key} as an argument.')
            options.append(option)

    return options


def main(**kwargs):
    file_path = kwargs.pop('file', None) or config_file_path
    config = load_config(file_path)
    responses = display_prompts(config, kwargs)
    click.echo(json.dumps(responses, indent=4))

config_file_path = 'prompts.yaml'
config = load_config(config_file_path)
options = generate_options(config)
main = click.Command('main', callback=main, params=options)

if __name__ == '__main__':
    main()
