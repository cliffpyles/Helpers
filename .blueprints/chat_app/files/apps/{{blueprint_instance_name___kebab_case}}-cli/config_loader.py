import json
import yaml

def load_config(file_path):
    """Load configuration from a JSON or YAML file."""
    with open(file_path, 'r') as config_file:
        if file_path.endswith('.json'):
            return json.load(config_file)
        elif file_path.endswith('.yml') or file_path.endswith('.yaml'):
            return yaml.safe_load(config_file)
        else:
            raise ValueError('Invalid file format. Use JSON or YAML.')
