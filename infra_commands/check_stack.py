import boto3
import yaml
import json
import difflib

def check_stack(stack_name, template_file):
    client = boto3.client("cloudformation")

    # Load the current stack's template
    current_template = client.get_template(StackName=stack_name)["TemplateBody"]

    # Convert the current template to JSON
    current_template = json.dumps(current_template, indent=2)

    # Load the template file from disk
    if template_file.endswith(".json"):
        with open(template_file, "r") as f:
            desired_template = json.load(f)
    elif template_file.endswith(".yaml"):
        with open(template_file, "r") as f:
            desired_template = yaml.safe_load(f)
            desired_template = json.dumps(desired_template, indent=2)
    else:
        raise ValueError("Unsupported file type: %s" % template_file)

    # Compare the templates
    if current_template == desired_template:
        print("The stack is up to date.")
    else:
        print("The stack is out of date. Differences:\n")
        diff = difflib.unified_diff(
            current_template.splitlines(),
            desired_template.splitlines(),
            fromfile='current_template',
            tofile='desired_template'
        )
        print('\n'.join(diff))
