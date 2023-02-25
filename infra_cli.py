#!/usr/bin/env python3

from infra_commands.create_template import create_template
from infra_commands.deploy_stack import deploy_stack
from infra_commands.delete_stack import delete_stack
from infra_commands.view_stack import view_stack
from infra_commands.check_stack import check_stack
from lib.parse_args import parse_args

if __name__ == "__main__":
    args = parse_args()

    if args.command == "deploy":
        deploy_stack(args.stack_name, args.template_file, args.parameters, args.parameters_file)

    elif args.command == "delete":
        delete_stack(args.stack_name)

    elif args.command == "create":
        create_template(args.template_type, args.output_file)

    elif args.command == "view":
        view_stack(args.stack_name, args.show_outputs, args.show_events, args.show_resources)

    elif args.command == "check":
        check_stack(args.stack_name, args.template_file)
