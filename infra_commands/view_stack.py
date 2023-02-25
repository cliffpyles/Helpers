import boto3

def view_stack(stack_name, show_outputs=False, show_events=False, show_resources=False):
    cf = boto3.client("cloudformation")
    response = cf.describe_stacks(StackName=stack_name)

    stack = response["Stacks"][0]
    if show_outputs:
        print("Outputs:")
        for output in stack.get("Outputs", []):
            print(f"{output['OutputKey']}: {output['OutputValue']}")

    if show_events:
        print("Events:")
        events = cf.describe_stack_events(StackName=stack_name)["StackEvents"]
        for event in events:
            print(f"{event['Timestamp']} - {event['ResourceType']} - {event['ResourceStatus']} - {event['LogicalResourceId']} - {event.get('ResourceStatusReason', '')}")

    if show_resources:
        print("Resources:")
        resources = cf.describe_stack_resources(StackName=stack_name)["StackResources"]
        for resource in resources:
            print(f"{resource['LogicalResourceId']} - {resource['PhysicalResourceId']} - {resource['ResourceType']} - {resource['ResourceStatus']} - {resource.get('ResourceStatusReason', '')}")
