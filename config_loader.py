# Configuration Loader
# Loads and manages configuration from YAML file

import yaml
import os

class Config:
    """Load and access configuration"""
    
    def __init__(self, config_file="config.yaml"):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration from YAML file"""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Config file not found: {self.config_file}")
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def get(self, key_path, default=None):
        """
        Get configuration value by dot-separated path.
        
        Example:
            config.get('ai_model.model_name')
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_all(self):
        """Get entire configuration"""
        return self.config

# Global config instance
config = Config()

if __name__ == "__main__":
    # Test the config loader
    print("Configuration loaded successfully!")
    print(f"AI Model: {config.get('ai_model.model_name')}")
    print(f"Max file size: {config.get('file_processing.max_file_size_mb')} MB")
    print(f"Logging enabled: {config.get('governance.enable_logging')}")
