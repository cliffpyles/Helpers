import json
import os
import uuid
from datetime import datetime

class ObjectManager:
    def __init__(self, file_name):
        self.file_name = file_name
        self.objects = self.load_objects()

    def load_objects(self):
        if os.path.exists(self.file_name):
            with open(self.file_name, "r") as file:
                return json.load(file)
        else:
            return []

    def save_objects(self):
        with open(self.file_name, "w") as file:
            json.dump(self.objects, file)

    def create_object(self, obj):
        obj['id'] = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        obj['created_at'] = current_time
        obj['updated_at'] = current_time
        self.objects.append(obj)
        self.save_objects()

    def list_objects(self):
        return self.objects

    def read_object(self, index):
        return self.objects[index]

    def update_object(self, index, updated_obj):
        updated_obj['id'] = self.objects[index]['id']
        updated_obj['created_at'] = self.objects[index]['created_at']
        updated_obj['updated_at'] = datetime.now().isoformat()
        self.objects[index] = updated_obj
        self.save_objects()

    def delete_object(self, index):
        del self.objects[index]
        self.save_objects()

    def search_objects(self, query):
        return [obj for obj in self.objects if query in str(obj)]

    def filter_objects(self, condition):
        return list(filter(condition, self.objects))
