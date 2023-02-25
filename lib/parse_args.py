import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="CLI tool for managing CloudFormation templates.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    deploy_parser = subparsers.add_parser("deploy", help="deploy a CloudFormation stack")
    deploy_parser.add_argument("stack_name", help="the name of the stack to deploy")
    deploy_parser.add_argument("template_file", help="the path to the template file to deploy")
    deploy_parser.add_argument(
        "--parameters",
        help="a comma-separated list of parameter key-value pairs",
        nargs="*",
        default=[],
    )
    deploy_parser.add_argument(
        "--parameters-file",
        help="the path to a file containing parameter key-value pairs",
    )

    delete_parser = subparsers.add_parser("delete", help="delete a CloudFormation stack")
    delete_parser.add_argument("stack_name", help="the name of the stack to delete")

    create_parser = subparsers.add_parser("create", help="create a CloudFormation template")
    create_parser.add_argument(
        "template_type",
        help="the type of the template to create (either 'json' or 'yaml')",
        choices=["json", "yaml"],
    )
    create_parser.add_argument(
        "output_file",
        help="the path to the file where the template should be saved",
        type=argparse.FileType("w"),
    )

    view_parser = subparsers.add_parser("view", help="view a CloudFormation stack")
    view_parser.add_argument("stack_name", help="the name of the stack to view")
    view_parser.add_argument(
        "--show-outputs", help="show the stack's outputs", action="store_true"
    )
    view_parser.add_argument(
        "--show-events", help="show the stack's events", action="store_true"
    )
    view_parser.add_argument(
        "--show-resources", help="show the stack's resources", action="store_true"
    )

    check_parser = subparsers.add_parser("check", help="check a CloudFormation stack")
    check_parser.add_argument("stack_name", help="the name of the stack to check")
    check_parser.add_argument(
        "template_file", help="the path to the CloudFormation template file to check"
    )

    return parser.parse_args()
