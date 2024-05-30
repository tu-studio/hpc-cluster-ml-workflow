from download import DownloadModule

class ModuleFactory:
    def create_module(self, module_type, config):
        if module_type == "download":
            return DownloadModule(config)
