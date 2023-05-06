import json
import os
import uuid
from datetime import datetime

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

    def create_item(self, obj):
        obj['id'] = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        obj['created_at'] = current_time
        obj['updated_at'] = current_time
        self.objects.append(obj)
        self.save_items()
        return obj

    def get_items(self):
        return self.objects

    def get_item(self, index):
        return self.objects[index]

    def update_item(self, index, updated_obj):
        updated_obj['id'] = self.objects[index]['id']
        updated_obj['created_at'] = self.objects[index]['created_at']
        updated_obj['updated_at'] = datetime.now().isoformat()
        self.objects[index] = updated_obj
        self.save_items()

        return updated_obj

    def delete_item(self, index):
        deleted_item = self.objects[index]
        del self.objects[index]
        self.save_items()

        return deleted_item

    def search_items(self, query):
        return [obj for obj in self.objects if query in str(obj)]

    def filter_items(self, condition):
        return list(filter(condition, self.objects))
