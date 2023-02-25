#!/usr/bin/env python3

import argparse
import json
from infra_commands import deploy_stack, delete_stack, create_template, view_stack


def get_parameters(args):
    parameters = None
    if args.parameters:
        parameters = []
        for param in args.parameters:
            key, value = param.split("=")
            parameters.append({"ParameterKey": key, "ParameterValue": value})
    if args.parameters_file:
        with open(args.parameters_file, "r") as f:
            file_params = json.load(f)
            if parameters:
                parameters.extend(file_params)
            else:
                parameters = file_params
    return parameters


def main():
    parser = argparse.ArgumentParser(description="CLI app for managing CloudFormation templates")
    subparsers = parser.add_subparsers(dest="command")

    deploy_parser = subparsers.add_parser("deploy", help="Create or update a CloudFormation stack")
    deploy_parser.add_argument("stack_name", type=str, help="Name of the stack to create or update")
    deploy_parser.add_argument("template_file", type=str, help="Path to the CloudFormation template file")
    deploy_parser.add_argument("--parameters", nargs="*", help="Template parameters in the format ParameterKey=ParameterValue")
    deploy_parser.add_argument("--parameters-file", type=str, help="Path to a JSON file containing template parameters")

    delete_parser = subparsers.add_parser("delete", help="Delete a CloudFormation stack")
    delete_parser.add_argument("stack_name", type=str, help="Name of the stack to delete")

    create_parser = subparsers.add_parser("create", help="Create a new CloudFormation template")
    create_parser.add_argument("template_name", type=str, help="Name of the new CloudFormation template")
    create_parser.add_argument("output_file", type=str, help="Path to the output CloudFormation template file")
    create_parser.add_argument("--template-type", choices=["json", "yaml"], default="yaml", help="Format of the CloudFormation template (default: yaml)")

    view_parser = subparsers.add_parser("view", help="View the status of a CloudFormation stack")
    view_parser.add_argument("stack_name", type=str, help="Name of the stack to view the status of")
    view_parser.add_argument("--show-outputs", "-o", action="store_true", help="Show stack outputs")
    view_parser.add_argument("--show-events", "-e", action="store_true", help="Show stack events")
    view_parser.add_argument("--show-resources", "-r", action="store_true", help="Show stack resources")

    args = parser.parse_args()

    if args.command == "deploy":
        parameters = get_parameters(args)
        deploy_stack.deploy_stack(args.stack_name, args.template_file, parameters)
    elif args.command == "delete":
        delete_stack.delete_stack(args.stack_name)
    elif args.command == "create":
        create_template.create_template(args.template_name, args.output_file, args.template_type)
    elif args.command == "view":
        view_stack.view_stack(args.stack_name, args.show_outputs, args.show_events, args.show_resources)


if __name__ == "__main__":
    main()
