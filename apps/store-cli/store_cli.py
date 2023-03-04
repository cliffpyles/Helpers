#!/usr/bin/env python3

import argparse
from handlers.item import create_item, view_item, update_item, delete_item, list_items
from handlers.store import create_store, view_store, update_store, delete_store, list_stores
from handlers.config import get_config, set_config, delete_config, list_config, reset_config
from utils import load_config


# CLI Parser

def create_parser():
    parser = argparse.ArgumentParser(description='Store CLI')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Config Commands

    # add `config` command
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_subparsers = config_parser.add_subparsers(dest='subcommand', help='Configuration subcommands')

    # add `config get` subcommand
    get_config_prop_parser = config_subparsers.add_parser('get', help='Get a configuration value')
    get_config_prop_parser.add_argument('key', type=str, help='Name of the configuration key to get')

    # add `config set` subcommand
    set_config_prop_parser = config_subparsers.add_parser('set', help='Set a configuration value')
    set_config_prop_parser.add_argument('key', type=str, help='Name of the configuration key to set')
    set_config_prop_parser.add_argument('value', type=str, help='Value to set the configuration key to')

    # add `config delete` subcommand
    delete_config_prop_parser = config_subparsers.add_parser('delete', help='Delete a configuration value')
    delete_config_prop_parser.add_argument('key', type=str, help='Name of the configuration key to delete')

    # add `config list` subcommand
    config_subparsers.add_parser('list', help='List all configuration values')

    # add `config reset` subcommand
    config_subparsers.add_parser('reset', help='Reset the configuration file')

    # Store Commands

    # add `store` command
    store_parser = subparsers.add_parser('store', help='Store management')
    store_subparsers = store_parser.add_subparsers(dest='subcommand', help='Store subcommands')

    # add `store create` subcommand
    create_store_parser = store_subparsers.add_parser('create', help='Create a new store')
    create_store_parser.add_argument('name', type=str, help='Name of the store to create')

    # add `store view` subcommand
    view_store_parser = store_subparsers.add_parser('view', help='View a store')
    view_store_parser.add_argument('name', type=str, help='Name of the store to view')

    # add `store update` subcommand
    update_store_parser = store_subparsers.add_parser('update', help='Update a store')
    update_store_parser.add_argument('current_name', type=str, help='Current name of the store')
    update_store_parser.add_argument('new_name', type=str, help='New name of the store')

    # add `store delete` subcommand
    delete_store_parser = store_subparsers.add_parser('delete', help='Delete a store')
    delete_store_parser.add_argument('name', type=str, help='Name of the store to delete')

    # add `store list` subcommand
    store_subparsers.add_parser('list', help='List all stores')

    # Item Commands

    # add `item` command
    item_parser = subparsers.add_parser('item', help='Item management')
    item_subparsers = item_parser.add_subparsers(dest='subcommand', help='Item subcommands')

    # add `item create` subcommand
    create_item_parser = item_subparsers.add_parser('create', help='Create an item in the store')
    create_item_parser.add_argument('--store', type=str, help='Name of the store to create the item in')
    create_item_parser.add_argument('fields', nargs='*', type=str, help='Dynamic fields in Key=Value format')

    # add `item view` subcommand
    view_item_parser = item_subparsers.add_parser('view', help='View an item in the store')
    view_item_parser.add_argument('item', type=str, help='Name of the item to view')
    view_item_parser.add_argument('--store', type=str, help='Name of the store that contains the item')

    # add `item update` subcommand
    update_item_parser = item_subparsers.add_parser('update', help='Update an item in the store')
    update_item_parser.add_argument('item', type=str, help='Name of the item to update')
    update_item_parser.add_argument('--store', type=str, help='Name of the store that contains the item')
    update_item_parser.add_argument('fields', nargs='*', type=str, help='Dynamic fields in Key=Value format')

    # add `item delete` subcommand
    delete_item_parser = item_subparsers.add_parser('delete', help='Delete an item from the store')
    delete_item_parser.add_argument('item', type=str, help='Name of the item to delete')
    delete_item_parser.add_argument('--store', type=str, help='Name of the store that contains the item')

    # add `item list` subcommand
    list_items_parser = item_subparsers.add_parser('list', help='List all items in the store')
    list_items_parser.add_argument('--store', type=str, help='Name of the store to list the items from')

    return parser


# Initialization

def main():
    config = load_config()
    parser = create_parser()
    args = parser.parse_args()
    
    config_subcommands = {
        'get': get_config,
        'set': set_config,
        'delete': delete_config,
        'list': list_config,
        'reset': reset_config,
    }

    store_subcommands = {
        'create': create_store,
        'view': view_store,
        'update': update_store,
        'delete': delete_store,
        'list': list_stores,
    }

    item_subcommands = {
        'create': create_item,
        'view': view_item,
        'update': update_item,
        'delete': delete_item,
        'list': list_items,
    }

    commands = {
        'config': config_subcommands,
        'store': store_subcommands,
        'item': item_subcommands,
    }

    subcommands = commands.get(args.command)
    handler = subcommands.get(args.subcommand)
    if handler:
        handler(args, config)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
