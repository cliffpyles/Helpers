#!/usr/bin/env python3

import argparse
from commands import create, update, delete, fetch

def main(args=None):
    parser = argparse.ArgumentParser(description="A simple CLI for working with data")
    subparsers = parser.add_subparsers(dest="command")

    create_parser = subparsers.add_parser("create", help="Create a new object")
    create_parser.add_argument("input", help="Input for create command")

    update_parser = subparsers.add_parser("update", help="Update an object")
    update_parser.add_argument("input", help="Input for update command")

    delete_parser = subparsers.add_parser("delete", help="Delete an object")
    delete_parser.add_argument("input", help="Input for delete command")

    fetch_parser = subparsers.add_parser("fetch", help="Fetch data from an external source")
    fetch_parser.add_argument("url", help="URL to fetch data from")
    fetch_parser.add_argument("-o", "--output", help="Output file path or S3 URI")

    args = parser.parse_args(args)

    if args.command == "create":
        create.create(args.input)
    elif args.command == "update":
        update.update(args.input)
    elif args.command == "delete":
        delete.delete(args.input)
    elif args.command == "fetch":
        fetch.fetch(args.url, args.output)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
