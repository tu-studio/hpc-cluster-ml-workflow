# This script is used to collect files from the internet and save them to the data/raw directory.
# It reads the configuration from collect_config.yaml file and executes the modules defined in the configuration.
# It is handled as a pipeline, where each module is executed in sequence.
# It could be extended to support more modules for data collection tasks.

import os
import wget
import zipfile
import yaml

class ConfigManager:
    def __init__(self, config_path):
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
    
    def get(self, key):
        return self.config.get(key, None)

class ModuleFactory:
    def create_module(self, module_type, config):
        if module_type == "download":
            return DownloadModule(config)

class DownloadModule:
    def __init__(self, config):
        self.config = config
    
    def execute(self):
        if not self.config['enabled']:
            print("Download module is disabled.")
            return
        
        urls = self.config.get('urls', [])
        save_dir = self.config.get('output_directory')
        save_dir = os.path.abspath(save_dir) 
    
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            print(f"Created directory {save_dir}")
            gitkeep_path = os.path.join(save_dir, '.gitkeep')
            with open(gitkeep_path, 'w') as f:
                pass  
            print(f"Created .gitkeep file in {save_dir}")


        for url in urls:
            print(f"Downloading from {url} to {save_dir}...")
            try:
                filepath = wget.download(url, out=save_dir)
                print(f"Downloaded {filepath} successfully from {url} to {save_dir}")

                if zipfile.is_zipfile(filepath):
                    print(f"Unzipping {filepath}...")
                    with zipfile.ZipFile(filepath, 'r') as zip_ref:
                        zip_ref.extractall(save_dir)
                        print(f"Unzipped {filepath} successfully")
                    os.remove(filepath)
                    print(f"Deleted zip file {filepath}")

            except Exception as e:
                print(f"Error downloading {url}: {e}")

        
def main():
    config_manager = ConfigManager("collect_config.yaml")
    factory = ModuleFactory()
    
    modules = config_manager.get("collect")
    print(f"Modules: {modules}")
    if modules is not None:
        for module_config in modules:
            if module_config.get('enabled', True):  # Check if the module is enabled
                module = factory.create_module(module_config['module'], module_config)
                if module is not None:
                    module.execute()
                else:
                    print(f"Module {module_config['module']} configuration not found, skipping...")
    else:
        print("No modules found in the configuration.")

if __name__ == "__main__":
    main()