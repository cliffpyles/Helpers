# file: handlers/item.py

import os
from utils import load_data, get_store_path, get_fields, create_item_object, update_item_object, save_data


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
