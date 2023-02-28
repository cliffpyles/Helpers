import boto3


def validate_template(template_file):
    with open(template_file, "r") as f:
        template_body = f.read()

    cf_client = boto3.client("cloudformation")
    response = cf_client.validate_template(TemplateBody=template_body)

    print(f"Template is valid: {response}")
    