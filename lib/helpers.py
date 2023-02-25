import json
import yaml

def load_template(file_path):
    """
    Load a CloudFormation template from a file.

    Args:
    file_path (str): The path to the file containing the template.

    Returns:
    dict: A dictionary containing the template.
    """
    with open(file_path, "r") as f:
        file_contents = f.read()

    if file_path.endswith(".json"):
        return json.loads(file_contents)
    elif file_path.endswith((".yaml", ".yml")):
        return yaml.safe_load(file_contents)
    else:
        raise ValueError(f"Unrecognized file extension: {file_path}")


def get_parameters(parameters):
    """
    Convert a list of parameters from the command line to a dictionary.

    Args:
    parameters (list): A list of strings containing parameters in the form "Key=Value".

    Returns:
    dict: A dictionary containing the parameters.
    """
    parameters_dict = {}

    for parameter in parameters:
        key, value = parameter.split("=", 1)
        parameters_dict[key] = value

    return parameters_dict

def get_environment_parameters(env):
    with open(f"{env}.json", "r") as f:
        return json.load(f)