class use_state:
    def __init__(self, initial_value):
        self.value = initial_value
        self._listeners = []

    def set(self, new_value):
        self.value = new_value
        self._notify_listeners()

    def get(self):
        return self.value

    def get_key(self, key):
        if not isinstance(self.value, dict):
            raise TypeError("State must be a dictionary to use get_key method.")
        
        keys = key.split('.')
        value = self.value
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        return value

    def set_key(self, key, value):
        if not isinstance(self.value, dict):
            raise TypeError("State must be a dictionary to use set_key method.")
        
        keys = key.split('.')
        current = self.value
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
        self._notify_listeners()

    def patch(self, updates):
        if not isinstance(self.value, dict):
            raise TypeError("State must be a dictionary to use patch method.")
        
        for key, value in updates.items():
            self.value[key] = value

        self._notify_listeners()

    def subscribe(self, listener):
        self._listeners.append(listener)
        return lambda: self._listeners.remove(listener)

    def _notify_listeners(self):
        for listener in self._listeners:
            listener()