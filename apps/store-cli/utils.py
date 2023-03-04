# file: utils.py

import os
import yaml
import json
import uuid
from datetime import datetime
from pathlib import Path
from itertools import chain

CONFIG_FILE = os.path.expanduser('~/.store-cli/config.yaml')
DEFAULT_CONFIG = {
    'current_store': 'default',
    'user_stores_dir': os.path.expanduser('~/.store-cli/stores'),
    'data_filename': 'data.json'
}

def load_config():
    with open(CONFIG_FILE) as f:
        config = yaml.safe_load(f)
    return config


def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        yaml.safe_dump(config, f)


def restore_default_config():
    os.remove(CONFIG_FILE)
    save_config(DEFAULT_CONFIG)
    print("Configuration file reset.")


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

def get_unique_keys(collection):
    keys = set()
    for record in collection:
        keys.update(record.keys())
    return keys