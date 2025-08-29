"""
Configuration management for PocketOJ
"""

import os
import yaml
from pathlib import Path


class Config:
    """Global system configuration"""

    def __init__(self, config_path=None):
        # Allow environment variable to override config path
        self.config_path = config_path or os.environ.get(
            'POCKETOJ_CONFIG', 'config.yaml')
        self.data = self._load_config()

    def _load_config(self):
        """Load configuration from YAML file with environment variable substitution"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                content = f.read()
                # Replace environment variables like ${SECRET_KEY}
                import re

                def replace_env_var(match):
                    var_name = match.group(1)
                    return os.environ.get(var_name, match.group(0))
                content = re.sub(r'\$\{([^}]+)\}', replace_env_var, content)
                return yaml.safe_load(content) or {}
        return self._get_default_config()

    def _get_default_config(self):
        """Get default configuration"""
        return {
            'system': {
                'problems_dir': 'problems',
                'judge_dir': 'judge',
                'default_time_limit_ms': 1000,
                'default_memory_limit_mb': 256,
                'max_file_size_mb': 10
            },
            'web': {
                'host': '127.0.0.1',
                'port': 5000,
                'debug': False,  # Default to False - enable explicitly for development
                'secret_key': 'pocket-oj-default-secret-key-change-in-production'
            },
            'compiler': {
                'cpp': {
                    'command': 'g++ -std=c++17 -O2 {src} -o {out}',
                    'timeout': 30
                }
            }
        }

    def save(self):
        """Save current configuration to file"""
        with open(self.config_path, 'w') as f:
            yaml.dump(self.data, f, default_flow_style=False)

    def get(self, key, default=None):
        """Get configuration value using dot notation (e.g., 'system.problems_dir')"""
        keys = key.split('.')
        value = self.data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key, value):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        data = self.data

        for k in keys[:-1]:
            if k not in data or not isinstance(data[k], dict):
                data[k] = {}
            data = data[k]

        data[keys[-1]] = value


# Global configuration instance
config = Config()
