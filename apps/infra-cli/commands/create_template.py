import json
import yaml

def create_template(template_name, output_file, template_type="yaml"):
    if template_type == "json":
        template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "Sample CloudFormation template that creates an S3 bucket",
            "Parameters": {
                "BucketName": {
                    "Type": "String",
                    "Description": "Name of the S3 bucket to create"
                }
            },
            "Resources": {
                "MyBucket": {
                    "Type": "AWS::S3::Bucket",
                    "Properties": {
                        "BucketName": {
                            "Ref": "BucketName"
                        }
                    }
                }
            },
            "Outputs": {
                "BucketArn": {
                    "Value": {
                        "Fn::GetAtt": [
                            "MyBucket",
                            "Arn"
                        ]
                    }
                }
            }
        }

        with open(output_file, "w") as f:
            json.dump(template, f)

    elif template_type == "yaml":
        template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "Sample CloudFormation template that creates an S3 bucket",
            "Parameters": {
                "BucketName": {
                    "Type": "String",
                    "Description": "Name of the S3 bucket to create"
                }
            },
            "Resources": {
                "MyBucket": {
                    "Type": "AWS::S3::Bucket",
                    "Properties": {
                        "BucketName": {
                            "Ref": "BucketName"
                        }
                    }
                }
            },
            "Outputs": {
                "BucketArn": {
                    "Value": {
                        "Fn::GetAtt": [
                            "MyBucket",
                            "Arn"
                        ]
                    }
                }
            }
        }

        with open(output_file, "w") as f:
            yaml.dump(template, f)

    else:
        print(f"Unknown template format: {template_type}")
        return

    print(f"Template {template_name} successfully created at {output_file}")
