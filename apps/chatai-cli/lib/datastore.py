import json
import os
import uuid
from datetime import datetime
from copy import deepcopy


def merge_dicts(dict1, dict2):
    """Recursively merge two dictionaries."""
    for key, value in dict2.items():
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
            merge_dicts(dict1[key], value)
        else:
            dict1[key] = value
    return dict1


class Datastore:
    def __init__(self, file_name):
        self.file_name = file_name
        self.objects = self.load_items()
        self.event_hooks = {"before": {}, "after": {}}

    def register_event_hook(self, hook_type, operation, callback):
        if hook_type not in self.event_hooks:
            raise ValueError(
                f"Invalid hook_type: {hook_type}. Must be 'before' or 'after'."
            )

        if operation not in self.event_hooks[hook_type]:
            self.event_hooks[hook_type][operation] = []

        self.event_hooks[hook_type][operation].append(callback)

    def execute_event_hooks(self, hook_type, operation, *args, **kwargs):
        if operation in self.event_hooks[hook_type]:
            for callback in self.event_hooks[hook_type][operation]:
                callback(*args, **kwargs)

    def load_items(self):
        if os.path.exists(self.file_name):
            with open(self.file_name, "r") as file:
                return json.load(file)
        else:
            return []

    def save_items(self):
        with open(self.file_name, "w") as file:
            json.dump(self.objects, file)

    def add_item(self, obj):
        self.execute_event_hooks("before", "add_item", obj)
        obj["id"] = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        obj["created_at"] = current_time
        obj["updated_at"] = current_time
        self.objects.append(obj)
        self.save_items()
        self.execute_event_hooks("after", "add_item", obj)
        return obj

    def get_items(self, ids=None):
        if not ids:
            return self.objects

        if isinstance(ids, list):
            return [obj for obj in self.objects if obj["id"] in ids]

        elif isinstance(ids, str):
            start_id, end_id = ids.split(":", 1) if ":" in ids else (ids, None)
            start_index = next(
                (
                    index
                    for index, obj in enumerate(self.objects)
                    if obj["id"] == start_id
                ),
                None,
            )
            end_index = (
                next(
                    (
                        index
                        for index, obj in enumerate(self.objects)
                        if obj["id"] == end_id
                    ),
                    None,
                )
                if end_id
                else None
            )

            if start_index is None:
                raise ValueError(f"Invalid start ID: {start_id}")

            if end_id and end_index is None:
                raise ValueError(f"Invalid end ID: {end_id}")

            if end_index:
                return self.objects[start_index : end_index + 1]
            else:
                return self.objects[start_index:]

        else:
            raise TypeError("Invalid argument type for ids. Must be a list or string.")

    def get_item(self, id):
        current_item = None
        for obj in self.objects:
            if obj["id"] == id:
                current_item = obj
                break
        return current_item

    def last_item(self):
        return self.objects[-1]

    def update_item(self, id, updates):
        self.execute_event_hooks("before", "update_item", id, updates)
        current_item = None
        for index, obj in enumerate(self.objects):
            if obj["id"] == id:
                updated_obj = merge_dicts(self.objects[index], updates)
                updated_obj["id"] = id
                updated_obj["created_at"] = obj["created_at"]
                updated_obj["updated_at"] = datetime.now().isoformat()
                self.objects[index] = updated_obj
                self.save_items()
                current_item = updated_obj
                break
        self.execute_event_hooks("after", "update_item", current_item)
        return current_item

    def remove_item(self, id):
        self.execute_event_hooks("before", "remove_item", id)
        deleted_item = None
        for index, obj in enumerate(self.objects):
            if obj["id"] == id:
                deleted_item = deepcopy(self.objects[index])
                del self.objects[index]
                self.save_items()
                break
        self.execute_event_hooks("after", "remove_item", deleted_item)
        return deleted_item

    def search_items(self, query):
        return [obj for obj in self.objects if query in str(obj)]

    def filter_items(self, condition):
        return [
            obj
            for obj in self.objects
            if all(obj.get(key) == value for key, value in condition.items())
        ]
