import boto3

def delete_stack(stack_name):
    cf_client = boto3.client('cloudformation')
    cf_client.delete_stack(StackName=stack_name)
    print(f"Stack {stack_name} successfully deleted.")
