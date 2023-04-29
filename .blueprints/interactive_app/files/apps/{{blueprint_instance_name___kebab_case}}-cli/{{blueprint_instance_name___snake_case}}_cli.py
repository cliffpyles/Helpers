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


def parse_dynamic_args(dynamic_args):
    arguments = {}
    for arg in dynamic_args:
        key, value = arg.lstrip('--').split('=')
        arguments[key] = value
    return arguments


@click.command(context_settings=dict(ignore_unknown_options=True,))
@click.option('-f', '--file', 'file_path', type=click.Path(exists=True), help='Path to the JSON or YAML configuration file.')
@click.argument('dynamic_args', nargs=-1, type=click.UNPROCESSED)
def main(file_path, dynamic_args):
    config = load_config(file_path)
    arguments = parse_dynamic_args(dynamic_args)
    responses = display_prompts(config, arguments)
    click.echo(json.dumps(responses, indent=4))


if __name__ == '__main__':
    main()
