from config_manager import ConfigManager
from module_factory import ModuleFactory





def main():
    config_manager = ConfigManager("../config.yaml")
    factory = ModuleFactory()
    
    modules = config_manager.get("pipeline")
    for module_config in modules:
        if module_config.get('enabled', True):  # Check if the module is enabled
            module = factory.create_module(module_config['module'], module_config)
            if module is not None:
                module.execute()
            else:
                print(f"Module {module_config['module']} configuration not found, skipping...")

if __name__ == "__main__":
    main()

