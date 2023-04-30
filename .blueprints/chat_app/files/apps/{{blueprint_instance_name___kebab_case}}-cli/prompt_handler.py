from InquirerPy import inquirer
from config_loader import load_config

def display_prompts(prompts, arguments):
    """
    Displays interactive prompts to the user and collects their responses.

    :param prompts: A list of dictionaries containing prompt configurations.
    :param arguments: A dictionary containing values of provided command-line arguments.
    :return: A dictionary containing user responses.
    """
    user_responses = {}

    for prompt in prompts:
        prompt_key = prompt.get('key')
        prompt_type = prompt['type']
        kwargs = prompt['kwargs']

        if prompt_key not in arguments:
            if prompt_type == 'text':
                user_responses[prompt_key] = inquirer.text(**kwargs).execute()
            elif prompt_type == 'checkbox':
                user_responses[prompt_key] = inquirer.checkbox(**kwargs).execute()
            elif prompt_type == 'radio':
                user_responses[prompt_key] = inquirer.select(**kwargs).execute()
            elif prompt_type == 'select':
                user_responses[prompt_key] = inquirer.select(**kwargs).execute()
            elif prompt_type == 'number':
                user_responses[prompt_key] = inquirer.number(**kwargs).execute()
            elif prompt_type == 'range':
                user_responses[prompt_key] = inquirer.number(**kwargs).execute()
            elif prompt_type == 'file':
                user_responses[prompt_key] = inquirer.filepath(only_files=True, **kwargs).execute()
            else:
                raise ValueError(f'Invalid prompt type: {prompt_type}')


    responses = {**arguments, **user_responses}


    return {k: v for k, v in responses.items() if v is not None}