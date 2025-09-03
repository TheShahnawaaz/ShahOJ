"""
Problem management system for ShahOJ - New File-Centric Architecture
"""

import os
import yaml
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

from .config import config
from .problem_config import ProblemConfig


class Problem:
    """Represents a single competitive programming problem"""

    def __init__(self, slug: str, problem_dir: Path):
        self.slug = slug
        self.problem_dir = Path(problem_dir)
        self.config_file = self.problem_dir / "config.yaml"
        self._config_data = None

    @property
    def config(self) -> ProblemConfig:
        """Get problem configuration"""
        if self._config_data is None:
            self._load_config()
        return self._config_data

    def _load_config(self):
        """Load problem configuration from config.yaml"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                yaml_content = f.read()
                self._config_data = ProblemConfig.from_yaml(yaml_content)
        else:
            # Create minimal config
            self._config_data = ProblemConfig.create_minimal(
                self.slug, self.slug)

        # Update file status
        self._config_data.update_file_status(self.problem_dir)

    def save_config(self, config: ProblemConfig):
        """Save problem configuration"""
        self._config_data = config
        self.problem_dir.mkdir(parents=True, exist_ok=True)

        # Update file status before saving
        config.update_file_status(self.problem_dir)

        with open(self.config_file, 'w') as f:
            f.write(config.to_yaml())

    def get_test_cases_count(self) -> Dict[str, int]:
        """Get count of test cases in each category (simplified: samples + system only)"""
        counts = {}
        test_dirs = ['samples', 'system']  # Removed pretests

        for test_dir in test_dirs:
            test_path = self.problem_dir / 'tests' / test_dir
            if test_path.exists():
                # Count .in files
                counts[test_dir] = len(list(test_path.glob('*.in')))
            else:
                counts[test_dir] = 0

        return counts

    def exists(self) -> bool:
        """Check if problem directory and basic files exist"""
        return (self.problem_dir.exists() and
                self.config_file.exists())

    def get_files_info(self) -> Dict[str, Any]:
        """Get information about problem files"""
        info = {
            'config_exists': self.config_file.exists(),
            'statement_exists': (self.problem_dir / 'statement.md').exists(),
            'solution_exists': (self.problem_dir / 'solution.py').exists(),
            'generator_exists': (self.problem_dir / 'generator.py').exists(),
            'validator_exists': (self.problem_dir / 'validator.py').exists(),
            'checker_exists': (self.problem_dir / 'checker').exists(),
            'test_cases': self.get_test_cases_count(),
            'is_complete': self.config.is_complete() if hasattr(self, '_config_data') and self._config_data else False,
            'missing_files': self.config.get_missing_files() if hasattr(self, '_config_data') and self._config_data else []
        }
        return info


class ProblemManager:
    """Manages all competitive programming problems"""

    def __init__(self, problems_dir: Optional[str] = None):
        self.problems_dir = Path(problems_dir or config.get(
            'system.problems_dir', 'problems'))
        self.problems_dir.mkdir(parents=True, exist_ok=True)

    def list_problems(self) -> List[Problem]:
        """Get list of all problems"""
        problems = []

        if not self.problems_dir.exists():
            return problems

        for item in self.problems_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                problem = Problem(item.name, item)
                if problem.exists():  # Only include valid problems
                    problems.append(problem)

        # Sort by creation date if available, otherwise by slug
        def sort_key(p):
            return p.config.get('created_date', p.slug)

        return sorted(problems, key=sort_key, reverse=True)

    def get_problem(self, slug: str) -> Optional[Problem]:
        """Get a specific problem by slug"""
        problem_dir = self.problems_dir / slug
        problem = Problem(slug, problem_dir)

        return problem if problem.exists() else None

    def create_problem_structure(self, slug: str, metadata: Dict[str, Any]) -> Problem:
        """Create basic problem directory structure with new file-centric approach"""
        problem_dir = self.problems_dir / slug

        # Create simplified directory structure (no pretests)
        directories = [
            'tests/samples',   # Manual test cases
            'tests/system',    # Generated test cases
            'checker'          # Custom checker (if needed)
        ]

        for dir_path in directories:
            (problem_dir / dir_path).mkdir(parents=True, exist_ok=True)

        # Create minimal configuration
        config = ProblemConfig.create_minimal(
            title=metadata.get('title', slug),
            slug=slug,
            difficulty=metadata.get('difficulty', 'Medium')
        )

        # Set additional metadata
        config.set('tags', metadata.get('tags', []))
        config.set('description', metadata.get('description', ''))
        config.set('limits.time_ms', metadata.get('time_limit_ms', 1000))
        config.set('limits.memory_mb', metadata.get('memory_limit_mb', 256))
        config.set('checker.type', metadata.get('checker_type', 'diff'))
        config.set('tests.sample_count', metadata.get('sample_count', 3))
        config.set('tests.system_count', metadata.get('system_count', 20))
        config.set('created_date', datetime.now().isoformat())

        # Create problem instance and save config
        problem = Problem(slug, problem_dir)
        problem.save_config(config)

        return problem

    def delete_problem(self, slug: str) -> bool:
        """Delete a problem and all its data"""
        problem_dir = self.problems_dir / slug

        if problem_dir.exists():
            try:
                shutil.rmtree(problem_dir)
                return True
            except Exception as e:
                print(f"Error deleting problem {slug}: {e}")
                return False

        return False

    def problem_exists(self, slug: str) -> bool:
        """Check if a problem with the given slug exists"""
        return (self.problems_dir / slug).exists()

    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics about all problems"""
        problems = self.list_problems()

        total_test_cases = 0
        difficulty_counts = {'Easy': 0, 'Medium': 0, 'Hard': 0}

        for problem in problems:
            # Count test cases
            test_counts = problem.get_test_cases_count()
            total_test_cases += sum(test_counts.values())

            # Count by difficulty
            difficulty = problem.config.get('difficulty', 'Medium')
            if difficulty in difficulty_counts:
                difficulty_counts[difficulty] += 1

        return {
            'total_problems': len(problems),
            'total_test_cases': total_test_cases,
            'difficulty_breakdown': difficulty_counts,
            'recent_problems': problems[:5]  # Last 5 problems
        }
