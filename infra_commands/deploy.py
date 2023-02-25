import boto3

def deploy(stack_name, template_file):
    cf_client = boto3.client('cloudformation')
    with open(template_file, 'r') as f:
        template_body = f.read()
    cf_client.create_stack(
        StackName=stack_name,
        TemplateBody=template_body,
        Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM']
    )
    print(f"Stack {stack_name} successfully created or updated.")
