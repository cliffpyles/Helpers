import requests
import boto3
from urllib.parse import urlparse

def fetch(url, output=None):
    response = requests.get(url)
    if output:
        if output.startswith("s3://"):
            s3 = boto3.client("s3")
            parsed_url = urlparse(output)
            bucket_name = parsed_url.netloc
            key_name = parsed_url.path.strip("/")
            s3.put_object(Body=response.content, Bucket=bucket_name, Key=key_name)
            print(f"Data fetched and saved to s3://{bucket_name}/{key_name}")
        else:
            with open(output, "w") as f:
                f.write(response.text)
            print(f"Data fetched and saved to {output}")
    else:
        print(response.text)
        print("Data fetched and printed to console")