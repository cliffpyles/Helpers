import requests
import boto3
from urllib.parse import urlparse

def fetch(url, output=None):
    if url.startswith("s3://"):
        s3 = boto3.client("s3")
        parsed_url = urlparse(url)
        bucket_name = parsed_url.netloc
        key_name = parsed_url.path.strip("/")
        response = s3.get_object(Bucket=bucket_name, Key=key_name)
        content = response["Body"].read()
    else:
        response = requests.get(url)
        content = response.content

    if output:
        if output.startswith("s3://"):
            s3 = boto3.client("s3")
            parsed_url = urlparse(output)
            bucket_name = parsed_url.netloc
            key_name = parsed_url.path.strip("/")
            s3.put_object(Body=content, Bucket=bucket_name, Key=key_name)
            print(f"Data fetched and saved to s3://{bucket_name}/{key_name}")
        else:
            with open(output, "wb") as f:
                f.write(content)
            print(f"Data fetched and saved to {output}")
    else:
        print(content.decode())
        print("Data fetched and printed to console")
