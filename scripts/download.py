import os
# import requests 
# import subprocess
# import platform
import wget
import zipfile


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

        
