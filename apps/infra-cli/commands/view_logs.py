import boto3


def view_logs(function_name, log_group, start_time, end_time, filter_pattern, limit):
    client = boto3.client('logs')
    log_stream_name = f"/aws/lambda/{function_name}"

    kwargs = {
        "logGroupName": log_group,
        "logStreamName": log_stream_name,
        "startTime": int(start_time) if start_time else None,
        "endTime": int(end_time) if end_time else None,
        "filterPattern": filter_pattern,
        "limit": int(limit) if limit else None
    }

    response = client.filter_log_events(**kwargs)

    for event in response["events"]:
        print(f"[{event['timestamp']}] {event['message']}")
