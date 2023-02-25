import boto3
import json
import yaml


def deploy_stack(stack_name, template_file, parameters):
    cf = boto3.client("cloudformation")
    with open(template_file, "r") as f:
        if template_file.endswith(".json"):
            template = json.load(f)
        elif template_file.endswith(".yaml") or template_file.endswith(".yml"):
            template = yaml.safe_load(f)
        else:
            raise ValueError("Unsupported template format")
    try:
        stack = cf.describe_stacks(StackName=stack_name)
        print(f"Updating stack: {stack_name}")
        cf.update_stack(StackName=stack_name, TemplateBody=json.dumps(template), Parameters=parameters)
        waiter = cf.get_waiter("stack_update_complete")
        waiter.wait(StackName=stack_name)
    except cf.exceptions.ClientError as e:
        if "does not exist" in str(e):
            print(f"Creating stack: {stack_name}")
            cf.create_stack(StackName=stack_name, TemplateBody=json.dumps(template), Parameters=parameters)
            waiter = cf.get_waiter("stack_create_complete")
            waiter.wait(StackName=stack_name)
        else:
            raise e
