import os
import shutil
from pathlib import Path
from utils import load_data, get_data_path, get_store_path, save_config, save_data


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

