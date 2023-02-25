#!/usr/bin/env python3

import argparse
from infra_commands import deploy, delete_stack, create_template

def main():
    parser = argparse.ArgumentParser(description="CLI app for managing CloudFormation templates")
    subparsers = parser.add_subparsers(dest="command")

    deploy_parser = subparsers.add_parser("deploy", help="Create or update a CloudFormation stack")
    deploy_parser.add_argument("stack_name", type=str, help="Name of the stack to create or update")
    deploy_parser.add_argument("template_file", type=str, help="Path to the CloudFormation template file")

    delete_parser = subparsers.add_parser("delete", help="Delete a CloudFormation stack")
    delete_parser.add_argument("stack_name", type=str, help="Name of the stack to delete")

    create_parser = subparsers.add_parser("create", help="Create a new CloudFormation template")
    create_parser.add_argument("template_name", type=str, help="Name of the new CloudFormation template")
    create_parser.add_argument("output_file", type=str, help="Path to the output CloudFormation template file")
    create_parser.add_argument("--template-type", choices=["json", "yaml"], default="yaml", help="Format of the CloudFormation template (default: yaml)")

    args = parser.parse_args()

    if args.command == "deploy":
        deploy.deploy(args.stack_name, args.template_file)
    elif args.command == "delete":
        delete_stack.delete_stack(args.stack_name)
    elif args.command == "create":
        create_template.create_template(args.template_name, args.output_file, args.template_type)

if __name__ == "__main__":
    main()
