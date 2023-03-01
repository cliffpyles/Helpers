#!/usr/bin/env python3

import argparse
import os
import shutil
import yaml
import json
import uuid
from datetime import datetime
from pathlib import Path

CONFIG_FILE = os.path.expanduser('~/.store-cli/config.yaml')
DEFAULT_CONFIG = {
    'current_store': 'default',
    'user_stores_dir': os.path.expanduser('~/.store-cli/stores'),
    'data_filename': 'data.json'
}


# Utilities

def load_config():
    with open(CONFIG_FILE) as f:
        config = yaml.safe_load(f)
    return config


def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        yaml.safe_dump(config, f)


def get_store_path(store_name, config):
    stores_dir = Path(config['user_stores_dir']).expanduser()
    store_path = os.path.join(stores_dir, store_name)

    return store_path


def load_data(store_name, config):
    stores_dir = Path(config['user_stores_dir']).expanduser()
    data_filename = config['data_filename']
    data_path = os.path.join(stores_dir, store_name, data_filename)

    with open(data_path) as f:
        data = json.load(f)

    return data


def save_data(store_name, data, config):
    stores_dir = Path(config['user_stores_dir']).expanduser()
    data_filename = config['data_filename']
    data_path = os.path.join(stores_dir, store_name, data_filename)

    with open(data_path, 'w') as f:
        json.dump(data, f)


def get_data_path(store_name, config):
    stores_dir = Path(config['user_stores_dir']).expanduser()
    data_filename = config['data_filename']
    data_path = os.path.join(stores_dir, store_name, data_filename)

    return data_path


def get_fields(fields):
    item = {}

    for field in fields:
        key,value = field.split('=', maxsplit=1)
        item[key] = value

    return item


def create_item_object(fields):
    # Add user defined fields
    item = fields

    # Add protected meta fields
    created_at = str(datetime.now())
    item["_id"] = str(uuid.uuid4())
    item["_created_at"] = created_at
    item["_updated_at"] = created_at
    item["_owner"] = os.getlogin()

    return item


def update_item_object(existing_fields, new_fields):
    item = existing_fields
    created_at = existing_fields.get("_created_at")
    owner = existing_fields.get("_owner")
    id = existing_fields.get("_id")

    item.update(new_fields)

    # Add protected meta fields
    updated_at = datetime.now()
    item["_id"] = id
    item["_created_at"] = created_at
    item["_updated_at"] = updated_at
    item["_owner"] = owner

    return item


def replace_item_object(existing_fields, new_fields):
    item = {}
    created_at = existing_fields.get("_created_at")
    owner = existing_fields.get("_owner")
    id = existing_fields.get("_id")

    # Add/update user defined fields
    item = new_fields

    # Add protected meta fields
    updated_at = datetime.now()
    item["_id"] = id
    item["_created_at"] = created_at
    item["_updated_at"] = updated_at
    item["_owner"] = owner

    return item


# Handlers

# Config Handlers

def get_config(args, config):
    print(config[args.key])


def set_config(args, config):
    config[args.key] = args.value
    save_config(config)
    print(f"Set {args.key} to {args.value}")


def delete_config(args, config):
    del config[args.key]
    save_config(config)
    print(f"Deleted {args.key}")


def list_config(args, config):
    print("Configuration:")
    for key, value in config.items():
        print(f"{key}: {value}")


def reset_config(args, config):
    os.remove(CONFIG_FILE)
    save_config(DEFAULT_CONFIG)
    print("Configuration file reset.")


# Store Handlers

def create_store(args, config):
    store_name = args.name
    store_path = get_store_path(store_name, config)
    data_path = get_data_path(store_name, config)

    # Check if store already exists
    if os.path.exists(store_path):
        print(f"Error: Store {store_name} already exists")
        return

    # Create store directory
    os.mkdir(store_path)

    # Create a file for data
    save_data(store_name, [], config)

    print(f"Store {store_name} created successfully")


def view_store(args, config):
    store_name = args.name
    store_path = get_store_path(store_name, config)
    data = load_data(store_name, config)

    # Check if store exists
    if not os.path.exists(store_path):
        print(f"Error: {store_name} does not exist")
        return

    # Show number of items in store
    item_count = len(data)
    
    if item_count < 1:
        print(f"No items in {store_name}")
        return

    # Print items
    print(f"Number of items in {store_name}: {item_count}")


def update_store(args, config):
    store_name = args.current_name
    store_path = get_store_path(store_name, config)

    # Ensure the default store isn't being updated
    if store_name == 'default':
        print(f"Error: update of the default store is not allowed")
        return

    # Check if store exists
    if not os.path.exists(store_path):
        print(f"Error: {store_name} does not exist")
        return

    # Check if store name is being updated
    if args.new_name and args.new_name != store_name:
        new_store_path = get_store_path(args.new_name, config)

        # Check if new store name already exists
        if os.path.exists(new_store_path):
            print(f"Error: {args.new_name} already exists")
            return

        # Rename store directory
        os.rename(store_path, new_store_path)

        # If the update is the current store, update the config
        if config['current_store'] == store_name:
            config['current_store'] = args.new_name
            save_config(config)

        print(f"{store_name} renamed to {args.new_name} successfully")
    else:
        print(f"No updates to {store_name}")


def delete_store(args, config):
    store_name = args.name
    store_path = get_store_path(store_name, config)

    # Ensure the default store isn't being deleted
    if store_name == 'default':
        print(f"Error: deletion of the default store is not allowed")
        return

    # Check if store exists
    if not os.path.exists(store_path):
        print(f"Error: {store_name} does not exist")
        return

    # Confirm deletion
    confirm = input(f"Are you sure you want to delete {store_name}? This cannot be undone. (y/n) ")
    if confirm.lower() != 'y':
        return

    # Delete store directory
    shutil.rmtree(store_path)

    # If the current store was deleted, update the config to use the default store
    if config['current_store'] == store_name:
        config['current_store'] = 'default'
        save_config(config)

    print(f"{store_name} deleted successfully")


def list_stores(args, config):
    stores_dir = Path(config['user_stores_dir']).expanduser()

    # List stores in stores directory
    stores = os.listdir(stores_dir)

    if not stores:
        print("No stores found")
        return

    # Print stores
    print("Stores:")
    for store in stores:
        print(f"- {store}")


# Item Handlers

def create_item(args, config):
    store_name = args.store or config['current_store']
    store_path = get_store_path(store_name, config)
    data = load_data(store_name, config)

    # Check if store exists
    if not os.path.exists(store_path):
        print(f"Error: {store_name} does not exist")
        return

    # Create item
    fields = get_fields(args.fields)
    item = create_item_object(fields)
    data.append(item)
    save_data(store_name, data, config)

    print(f"Item created successfully in {store_name}")


def view_item(args, config):
    item_id = args.id
    store_name = args.store or config['current_store']
    store_path = get_store_path(store_name, config)
    data = load_data(store_name, config)

    # Check if store exists
    if not os.path.exists(store_path):
        print(f"Error: {store_name} does not exist")
        return

    # Find item
    item = next((sub for sub in data if sub['_id'] == item_id), None)

    # Check if item exists
    if not item:
        print(f"Error: {item_id} does not exist in {store_name}")
        return

    # Print item
    print(f"Item: {item_id}")
    print(item)


def update_item(args, config):
    store_name = args.store or config['current_store']
    store_path = get_store_path(store_name, config)
    data = load_data(store_name, config)

    # Check if store exists
    if not os.path.exists(store_path):
        print(f"Error: {store_name} does not exist")
        return

    fields = get_fields(args.fields)
    item_id = fields.id
    item = create_item_object(fields)
    # Find item
    item = next((sub for sub in data if sub['_id'] == item_id), None)
    
    # Check if item exists
    if not item:
        print(f"Error: {item_id} does not exist in {store_name}")
        return

    # Update item
    item = update_item_object(item, fields)
    new_data = [sub for sub in data if sub['_id'] != item_id]
    new_data.append(item)

    save_data(store_name, new_data, config)

    print(f"Item {item_id} updated successfully in {store_name}")


def delete_item(args, config):
    item_id = args.item
    store_name = args.store or config['current_store']
    store_path = get_store_path(store_name, config)
    data = load_data(store_name, config)

    # Check if store exists
    if not os.path.exists(store_path):
        print(f"Error: {store_name} does not exist")
        return

    # Find item
    item = next((sub for sub in data if sub['_id'] == item_id), None)

    # Check if item exists
    if not item:
        print(f"Error: {item_id} does not exist in {store_name}")
        return

    # Delete item
    new_data = [sub for sub in data if sub['_id'] != item_id]
    save_data(store_name, new_data, config)

    print(f"Item {item_id} deleted successfully from {store_name}")


def list_items(args, config):
    store_name = args.store or config['current_store']
    data = load_data(store_name, config)

    # Check if store exists
    store_path = get_store_path(store_name, config)
    if not os.path.exists(store_path):
        print(f"Error: {store_name} does not exist")
        return

    # Check if there are items in the store
    if not data:
        print(f"No items in {store_name}")
        return

    # Print items
    print(f"Items in {store_name}:")
    for datum in data:
        print(datum)


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
