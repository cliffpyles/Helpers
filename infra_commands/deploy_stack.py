import boto3

def deploy_stack(stack_name, template_file, parameters=None):
    cf = boto3.client("cloudformation")

    with open(template_file, "r") as f:
        template = f.read()

    try:
        cf.create_stack(StackName=stack_name, TemplateBody=template, Parameters=parameters, Capabilities=["CAPABILITY_NAMED_IAM"])
    except cf.exceptions.AlreadyExistsException:
        cf.update_stack(StackName=stack_name, TemplateBody=template, Parameters=parameters, Capabilities=["CAPABILITY_NAMED_IAM"])

    print(f"Stack {stack_name} successfully created or updated")
