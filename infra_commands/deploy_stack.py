import boto3
from botocore.exceptions import ClientError


def deploy_stack(stack_name, template_file, parameters, capabilities=None):
    """
    Create or update a CloudFormation stack with the given name and template.

    Args:
    stack_name (str): The name of the stack.
    template_file (str): The path to the file containing the template.
    parameters (dict): A dictionary containing parameter values for the stack.
    capabilities (list): A list of capabilities required by the stack.

    Returns:
    dict: A dictionary containing information about the created or updated stack.
    """
    cf = boto3.client("cloudformation")

    with open(template_file, "r") as f:
        template = f.read()

    try:
        stack = cf.describe_stacks(StackName=stack_name)
        action = "update"
    except ClientError as e:
        if "does not exist" in str(e):
            action = "create"
        else:
            raise e

    if capabilities is None:
        capabilities = ["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"]

    if action == "create":
        response = cf.create_stack(
            StackName=stack_name,
            TemplateBody=template,
            Parameters=[{"ParameterKey": k, "ParameterValue": v} for k, v in parameters.items()],
            Capabilities=capabilities
        )
    elif action == "update":
        try:
            response = cf.update_stack(
                StackName=stack_name,
                TemplateBody=template,
                Parameters=[{"ParameterKey": k, "ParameterValue": v} for k, v in parameters.items()],
                Capabilities=capabilities
            )
        except ClientError as e:
            if "ValidationError" in str(e):
                print("ERROR: Stack update failed due to a validation error.")
                print(str(e))
                return
            elif "InsufficientCapabilitiesException" in str(e):
                print("ERROR: Stack update failed due to insufficient capabilities.")
                print(f"Required capabilities: {', '.join(capabilities)}")
                print("Add the capabilities to the command with the --capabilities option and try again.")
                return
            else:
                raise e

    stack_id = response["StackId"]
    print(f"Stack {action} initiated: {stack_id}")

    try:
        waiter = cf.get_waiter(f"stack_{action}_complete")
        waiter.wait(StackName=stack_id)
    except Exception as e:
        print("ERROR: Stack operation failed.")
        print(str(e))
        return

    stack = cf.describe_stacks(StackName=stack_name)["Stacks"][0]
    stack_info = {
        "StackName": stack["StackName"],
        "StackId": stack["StackId"],
        "CreationTime": stack["CreationTime"],
        "StackStatus": stack["StackStatus"],
        "Outputs": stack.get("Outputs", [])
    }

    print(f"Stack {action} complete: {stack_info['StackStatus']}")

    return stack_info
