#!/usr/bin/env python3

import argparse
import sys
import os
from lib import helpers
from commands import deploy_stack, create_template, view_stack, check_stack, validate_template, lint_template, view_logs


def parse_args(args):
    parser = argparse.ArgumentParser(description="CLI tool for managing CloudFormation stacks")
    subparsers = parser.add_subparsers(dest="command")

    # Deploy stack command
    deploy_parser = subparsers.add_parser("deploy")
    deploy_parser.add_argument("stack_name", help="The name of the CloudFormation stack to create or update")
    deploy_parser.add_argument("template_file", help="The path to the CloudFormation template file to use")
    deploy_parser.add_argument("--parameters", nargs="+", help="A list of parameter values to use for the stack")
    deploy_parser.add_argument("--parameters-file", help="The path to a file containing parameter values to use for the stack")
    deploy_parser.add_argument("--capabilities", nargs="+", help="A list of capabilities required by the stack")

    # Create template command
    create_parser = subparsers.add_parser("create-template")
    create_parser.add_argument("stack_name", help="The name of the CloudFormation stack to create a template for")
    create_parser.add_argument("--output-file", "-o", help="The path to write the output file to")
    create_parser.add_argument("--format", "-f", choices=["json", "yaml"], default="yaml", help="The format of the output file")

    # View stack command
    view_parser = subparsers.add_parser("view", aliases=["show"])
    view_parser.add_argument("stack_name", help="The name of the CloudFormation stack to view")
    view_parser.add_argument("--events", "-e", action="store_true", help="Show stack events")
    view_parser.add_argument("--resources", "-r", action="store_true", help="Show stack resources")

    # Check stack command
    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("stack_name", help="The name of the CloudFormation stack to check")
    check_parser.add_argument("template_file", help="The path to the CloudFormation template file to check")

    # Validate stack command
    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("template_file", help="The path to the CloudFormation template file to validate")

    # Lint template command
    lint_parser = subparsers.add_parser("lint")
    lint_parser.add_argument("template_file", help="The path to the CloudFormation template file to lint")

    logs_parser = subparsers.add_parser("logs")
    logs_parser.add_argument("function_name", help="The name of the Lambda function")
    logs_parser.add_argument("--log-group", help="The name of the CloudWatch Logs log group")
    logs_parser.add_argument("--start-time", help="The start time for the log query")
    logs_parser.add_argument("--end-time", help="The end time for the log query")
    logs_parser.add_argument("--filter-pattern", help="The filter pattern for the log query")
    logs_parser.add_argument("--limit", help="The maximum number of log events to return")

    return parser.parse_args(args)


def main():
    args = parse_args(sys.argv[1:])

    if args.command == "deploy":
        if args.parameters_file:
            with open(args.parameters_file, "r") as f:
                parameters = helpers.get_parameters(f.read().split())
        elif args.parameters:
            parameters = helpers.get_parameters(args.parameters)
        else:
            parameters = {}

        deploy_stack.deploy_stack(args.stack_name, args.template_file, parameters, args.capabilities)

    elif args.command == "create-template":
        output_file = args.output_file or f"{args.stack_name}.{args.format}"
        create_template.create_template(args.stack_name, output_file, args.format)

    elif args.command == "view":
        view_stack.view_stack(args.stack_name, args.events, args.resources)

    elif args.command == "check":
        check_stack.check_stack(args.stack_name, args.template_file)
    
    elif args.command == "validate":
        validate_template.validate_template(args.template_file)

    elif args.command == "lint":
        lint_template.lint_template(args.template_file)

    elif args.command == "logs":
        view_logs.view_logs(args.function_name, args.log_group, args.start_time, args.end_time, args.filter_pattern, args.limit)

if __name__ == "__main__":
    main()
