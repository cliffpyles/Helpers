import json
import os
import uuid
from datetime import datetime

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
        obj['id'] = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        obj['created_at'] = current_time
        obj['updated_at'] = current_time
        self.objects.append(obj)
        self.save_items()
        return obj

    def get_items(self):
        return self.objects

    def get_item(self, id):
        current_item = None
        for obj in self.objects:
            if obj['id'] == id:
                current_item = obj
                break
        return current_item
    
    def last_item(self):
        return self.objects[-1]

    def update_item(self, id, updates):
        current_item = None
        for index, obj in enumerate(self.objects):
            if obj['id'] == id:
                updated_obj = merge_dicts(self.objects[index], updates)
                updated_obj['id'] = id
                updated_obj['created_at'] = obj['created_at']
                updated_obj['updated_at'] = datetime.now().isoformat()
                self.objects[index] = updated_obj
                self.save_items()
                current_item = updated_obj
                break
        return current_item

    def delete_item(self, id):
        current_item = None
        for index, obj in enumerate(self.objects):
            if obj['id'] == id:
                deleted_item = self.objects[index]
                del self.objects[index]
                self.save_items()
                current_item = deleted_item
                break
        return current_item

    def search_items(self, query):
        return [obj for obj in self.objects if query in str(obj)]

    def filter_items(self, condition):
        return [obj for obj in self.objects if all(obj.get(key) == value for key, value in condition.items())]

