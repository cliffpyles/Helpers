import inquirer
from inquirer.errors import ValidationError
from config_loader import load_config

class RangeValidator(object):
    """Validator class for ensuring user input is within a specified range."""

    def __init__(self, min_value, max_value):
        self.min_value = min_value
        self.max_value = max_value

    def __call__(self, _, value):
        try:
            int_value = int(value)
            if self.min_value <= int_value <= self.max_value:
                return value
            else:
                raise ValidationError("", reason=f"Value must be between {self.min_value} and {self.max_value}")
        except ValueError:
            raise ValidationError("", reason="Please enter a valid number")

def read_file(file_path):
    """Read the content of a file."""
    with open(file_path, 'r') as file:
        content = file.read()
    return content

def display_prompts(prompts, arguments):
    """
    Displays interactive prompts to the user and collects their responses.

    :param prompts: A list of dictionaries containing prompt configurations.
    :param arguments: A dictionary containing values of provided command-line arguments.
    :return: A dictionary containing user responses.
    """
    questions = []

    for prompt in prompts:
        prompt_key = prompt.get('key')
        prompt_type = prompt['type']
        kwargs = prompt['kwargs']

        if prompt_key and arguments.get(prompt_key) is not None:
            continue

        if prompt_type == 'text':
            question = inquirer.Text(**kwargs)
        elif prompt_type == 'checkbox':
            question = inquirer.Checkbox(**kwargs)
        elif prompt_type == 'radio':
            question = inquirer.List(**kwargs)
        elif prompt_type == 'range':
            min_value = kwargs.pop('min', None)
            max_value = kwargs.pop('max', None)
            if min_value is not None and max_value is not None:
                kwargs['validate'] = RangeValidator(min_value, max_value)
            question = inquirer.Text(**kwargs)
        elif prompt_type == 'file':
            question = inquirer.Text(**kwargs)
        else:
            raise ValueError(f'Invalid prompt type: {prompt_type}')

        questions.append(question)

    user_responses = inquirer.prompt(questions)
    responses = {**arguments, **user_responses}

    # Read the contents of the file for 'file' prompt type
    for prompt in prompts:
        prompt_key = prompt.get('key')
        prompt_type = prompt['type']
        if prompt_type == 'file' and responses.get(prompt_key) is not None:
            file_path = responses[prompt_key]
            responses[f"{prompt_key}_content"] = read_file(file_path)

    return {k: v for k, v in responses.items() if v is not None}