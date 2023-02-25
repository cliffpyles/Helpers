import boto3
from botocore.exceptions import ClientError


def deploy_stack(stack_name, template_file, parameters):
    cf = boto3.client("cloudformation")

    try:
        with open(template_file, "r") as f:
            template_body = f.read()

        cf.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=parameters,
            Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"]
        )
        print(f"Stack '{stack_name}' creation in progress...")
    except ClientError as e:
        if e.response["Error"]["Code"] == "AlreadyExistsException":
            try:
                with open(template_file, "r") as f:
                    template_body = f.read()

                cf.update_stack(
                    StackName=stack_name,
                    TemplateBody=template_body,
                    Parameters=parameters,
                    Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"]
                )
                print(f"Stack '{stack_name}' update in progress...")
            except ClientError as e:
                print(f"Error updating stack '{stack_name}': {e}")
        else:
            print(f"Error creating stack '{stack_name}': {e}")
