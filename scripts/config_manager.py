import yaml

class ConfigManager:
    def __init__(self, config_path):
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
    
    def get(self, key):
        return self.config.get(key, None)

