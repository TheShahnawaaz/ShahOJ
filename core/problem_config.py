"""
New simplified problem configuration system
Focuses on files and metadata, not rigid constraints
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class ProblemConfig:
    """Simplified, flexible problem configuration"""

    def __init__(self, config_data: Dict[str, Any]):
        self.data = config_data

    @classmethod
    def create_minimal(cls, title: str, slug: str, difficulty: str = "Medium") -> 'ProblemConfig':
        """Create minimal configuration for new problems"""
        config_data = {
            # Essential metadata
            'title': title,
            'slug': slug,
            'difficulty': difficulty,
            'tags': [],
            'description': '',

            # Execution settings
            'limits': {
                'time_ms': 1000,
                'memory_mb': 256
            },

            # File configuration
            'files': {
                'has_statement': False,
                'has_solution': False,
                'has_generator': False,
                'has_validator': False,
                'has_custom_checker': False
            },

            # Checker configuration
            'checker': {
                'type': 'diff',  # diff, float, spj
                'float_tolerance': 1e-6,
                'spj_path': 'checker/spj'
            },

            # Test case settings
            'tests': {
                'sample_count': 3,    # Manual examples
                'system_count': 20    # Generated tests
            },

            # Validation settings
            'validation': {
                'enabled': False,  # Default to disabled for simplified workflow
                'strict_mode': True
            }
        }

        return cls(config_data)

    def get(self, key: str, default=None):
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        data = self.data

        for k in keys[:-1]:
            if k not in data or not isinstance(data[k], dict):
                data[k] = {}
            data = data[k]

        data[keys[-1]] = value

    def update_file_status(self, problem_dir: Path):
        """Update file status based on what exists in problem directory"""
        file_checks = {
            'has_statement': 'statement.md',
            'has_solution': 'solution.py',
            'has_generator': 'generator.py',
            'has_validator': 'validator.py',
            'has_custom_checker': 'checker/spj.cpp'
        }

        for key, filename in file_checks.items():
            file_path = problem_dir / filename
            self.set(f'files.{key}', file_path.exists())

    def is_complete(self) -> bool:
        """Check if problem has minimum required files"""
        required_files = ['has_statement', 'has_solution', 'has_generator']
        return all(self.get(f'files.{key}', False) for key in required_files)

    def get_missing_files(self) -> list:
        """Get list of missing required files"""
        required_files = {
            'has_statement': 'statement.md',
            'has_solution': 'solution.py',
            'has_generator': 'generator.py'
        }

        missing = []
        for key, filename in required_files.items():
            if not self.get(f'files.{key}', False):
                missing.append(filename)

        return missing

    def to_yaml(self) -> str:
        """Convert to YAML string"""
        return yaml.dump(self.data, default_flow_style=False, sort_keys=False)

    @classmethod
    def from_yaml(cls, yaml_content: str) -> 'ProblemConfig':
        """Create from YAML string"""
        data = yaml.safe_load(yaml_content) or {}
        return cls(data)
