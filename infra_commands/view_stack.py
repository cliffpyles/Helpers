import boto3

def view_stack(stack_name, show_outputs, show_events, show_resources):
    cf = boto3.client("cloudformation")
    stack = cf.describe_stacks(StackName=stack_name)["Stacks"][0]
    print(f"Stack Name: {stack_name}")
    print(f"Stack Status: {stack['StackStatus']}")
    print(f"Stack Outputs: {stack.get('Outputs', [])}" if show_outputs else "")
    print(f"Stack Events: {stack.get('StackEvents', [])}" if show_events else "")
    print(f"Stack Resources: {stack.get('Resources', [])}" if show_resources else "")
