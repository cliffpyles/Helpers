import click

def generate_options(prompts):
    """
    Generates click options for command-line arguments based on the provided prompts.

    :param prompts: A list of dictionaries containing prompt configurations.
    :return: A list of click.Option objects.
    """
    options = []

    for prompt in prompts:
        prompt_key = prompt.get('key')
        prompt_type = prompt['type']
        kwargs = prompt.get('kwargs', {})
        default = kwargs.get('default', None)
        required = kwargs.get('mandatory', False)
        description = prompt.get('description', None)

        if prompt_key:
            help_text = description or f'Pass your {prompt_key} as an argument.'
            if default is not None:
                help_text += f' Default: {default}.'

            if prompt_type == 'radio':
                choices = kwargs.get('choices')
                option = click.Option(param_decls=[f'--{prompt_key}'],
                                      type=click.Choice(choices, case_sensitive=False),
                                      default=default,
                                      required=required,
                                      help=help_text)
            elif prompt_type == 'file':
                option = click.Option(param_decls=[f'--{prompt_key}'],
                                      type=click.Path(exists=True, dir_okay=False, resolve_path=True),
                                      default=default,
                                      required=required,
                                      help=help_text)
            else:
                option = click.Option(param_decls=[f'--{prompt_key}'],
                                      type=str,
                                      default=default,
                                      required=required,
                                      help=help_text)
            options.append(option)

    return options
