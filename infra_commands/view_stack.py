import boto3
from botocore.exceptions import ClientError


def view_stack(stack_name, show_outputs, show_events, show_resources):
    cf = boto3.client("cloudformation")

    try:
        stack = cf.describe_stacks(StackName=stack_name)["Stacks"][0]
        print(f"Stack: {stack['StackName']}")
        print(f"Status: {stack['StackStatus']}")

        if show_outputs:
            outputs = stack["Outputs"]
            if outputs:
                print("Outputs:")
                for output in outputs:
                    print(f"- {output['OutputKey']}: {output['OutputValue']}")
            else:
                print("No outputs found.")

        if show_events:
            events = cf.describe_stack_events(StackName=stack_name)["StackEvents"]
            if events:
                print("Events:")
                for event in events:
                    print(f"- {event['Timestamp']} {event['ResourceType']} {event['LogicalResourceId']} {event['ResourceStatus']} {event['ResourceStatusReason']}")
            else:
                print("No events found.")

        if show_resources:
            resources = cf.describe_stack_resources(StackName=stack_name)["StackResources"]
            if resources:
                print("Resources:")
                for resource in resources:
                    print(f"- {resource['LogicalResourceId']} {resource['ResourceType']} {resource['ResourceStatus']}")
            else:
                print("No resources found.")
    except ClientError as e:
        print(f"Error viewing stack '{stack_name}': {e}")
