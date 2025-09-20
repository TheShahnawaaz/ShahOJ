#!/usr/bin/env python3
"""
Production Problem Migration Script
Migrates existing problems from YAML files to the new multi-user database system.
"""

from core.database import DatabaseManager
from core.unified_problem_manager import UnifiedProblemManager
import os
import sys
import yaml
import json
import shutil
from pathlib import Path
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ProductionMigrator:
    def __init__(self, owner_email: str):
        """Initialize migrator with owner email"""
        self.db_manager = DatabaseManager()
        self.problem_manager = UnifiedProblemManager(self.db_manager)
        self.owner_email = owner_email
        self.owner_user = None

        # Problem directories to scan
        self.problem_dirs = [
            Path("problems_backup"),
            Path("problems"),
        ]

        self.migrated_count = 0
        self.skipped_count = 0
        self.error_count = 0

    def find_or_create_owner(self):
        """Find or create the owner user"""
        print(f"Looking for user with email: {self.owner_email}")

        # Try to find existing user
        user = self.db_manager.get_user_by_email(self.owner_email)
        if user:
            self.owner_user = user
            print(f"Found existing user: {user['name']} ({user['email']})")
            return

        # Create new user if not found
        print(
            f"User not found. Please create a user account first by logging in with Google.")
        print(f"After logging in once, run this script again.")
        sys.exit(1)

    def find_yaml_problems(self):
        """Find all problems with YAML config files"""
        problems = []

        for problem_dir in self.problem_dirs:
            if not problem_dir.exists():
                continue

            print(f"Scanning {problem_dir}...")

            for item in problem_dir.iterdir():
                if not item.is_dir():
                    continue

                # Look for config.yaml or problem.yaml
                config_files = [
                    item / "config.yaml",
                    item / "problem.yaml"
                ]

                config_file = None
                for cf in config_files:
                    if cf.exists():
                        config_file = cf
                        break

                if config_file:
                    problems.append({
                        'slug': item.name,
                        'path': item,
                        'config_file': config_file
                    })
                    print(f"  Found: {item.name}")

        return problems

    def load_yaml_config(self, config_file: Path):
        """Load and parse YAML config"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading {config_file}: {e}")
            return None

    def check_if_exists(self, slug: str):
        """Check if problem already exists in database"""
        try:
            existing = self.db_manager.get_problem_by_slug(slug)
            return existing is not None
        except:
            return False

    def migrate_problem(self, problem_info):
        """Migrate a single problem"""
        slug = problem_info['slug']
        problem_path = problem_info['path']
        config_file = problem_info['config_file']

        print(f"\nMigrating: {slug}")

        # Check if already exists
        if self.check_if_exists(slug):
            print(
                f"  ⚠️  Problem '{slug}' already exists in database. Skipping.")
            self.skipped_count += 1
            return

        # Load YAML config
        config = self.load_yaml_config(config_file)
        if not config:
            print(f"  ❌ Failed to load config for '{slug}'")
            self.error_count += 1
            return

        try:
            # Handle different YAML formats
            if isinstance(config, str):
                print(
                    f"  ❌ Invalid YAML format for '{slug}': config is a string")
                self.error_count += 1
                return

            # Prepare problem metadata with robust handling of different formats
            metadata = {
                'title': config.get('title', slug.replace('-', ' ').title()),
                'difficulty': config.get('difficulty', 'Medium'),
                'tags': config.get('tags', []),
                'author_id': self.owner_user['id'],
                'is_public': True,  # Make all migrated problems public by default

                # Limits - handle both nested and flat formats
                'time_limit_ms': (
                    config.get('time_limit_ms') or
                    (config.get('limits', {}).get('time_ms') if isinstance(config.get('limits'), dict) else None) or
                    1000
                ),
                'memory_limit_mb': (
                    config.get('memory_limit_mb') or
                    (config.get('limits', {}).get('memory_mb') if isinstance(config.get('limits'), dict) else None) or
                    256
                ),

                # Checker - handle both nested and flat formats
                'checker_type': (
                    config.get('checker') if isinstance(config.get('checker'), str) else
                    (config.get('checker', {}).get('type') if isinstance(
                        config.get('checker'), dict) else 'diff')
                ),
                'checker_tolerance': (
                    config.get('checker', {}).get('float_tolerance') if isinstance(
                        config.get('checker'), dict) else 1e-6
                ),

                # Tests
                'sample_count': (
                    config.get('tests', {}).get('sample_count') if isinstance(
                        config.get('tests'), dict) else 3
                ),
                'system_count': (
                    config.get('tests', {}).get('system_count') if isinstance(
                        config.get('tests'), dict) else 20
                ),

                # Validation
                'validation_enabled': (
                    config.get('validation', {}).get('enabled') if isinstance(
                        config.get('validation'), dict) else False
                ),
                'validation_strict': (
                    config.get('validation', {}).get('strict') if isinstance(
                        config.get('validation'), dict) else True
                ),

                # File flags
                'has_statement': (problem_path / 'statement.md').exists(),
                'has_solution': (problem_path / 'solution.py').exists(),
                'has_generator': (problem_path / 'generator.py').exists(),
                'has_validator': (problem_path / 'validator.py').exists(),
                'has_custom_checker': (problem_path / 'checker' / 'checker.cpp').exists(),
            }

            # Create problem in database
            result = self.problem_manager.create_problem(
                title=metadata['title'],
                **{k: v for k, v in metadata.items() if k not in ['title']}
            )

            if not result or not result.get('slug'):
                print(f"  ❌ Failed to create problem in database: {result}")
                self.error_count += 1
                return

            # Get the generated slug
            generated_slug = result['slug']

            # Copy files to new location
            new_problem_path = self.problem_manager.problems_dir / generated_slug

            # Remove any existing directory (in case of partial migration)
            if new_problem_path.exists():
                shutil.rmtree(new_problem_path)

            # Copy entire problem directory
            shutil.copytree(problem_path, new_problem_path)

            # Remove the old config.yaml file (we use database now)
            old_config = new_problem_path / 'config.yaml'
            if old_config.exists():
                old_config.unlink()

            old_problem_yaml = new_problem_path / 'problem.yaml'
            if old_problem_yaml.exists():
                old_problem_yaml.unlink()

            print(f"  ✅ Successfully migrated '{slug}' as '{generated_slug}'")
            self.migrated_count += 1

        except Exception as e:
            print(f"  ❌ Error migrating '{slug}': {e}")
            self.error_count += 1

    def run_migration(self):
        """Run the complete migration process"""
        print("🚀 Starting Production Problem Migration")
        print("=" * 50)

        # Find or create owner user
        self.find_or_create_owner()

        # Find all YAML problems
        problems = self.find_yaml_problems()

        if not problems:
            print("No problems with YAML configs found.")
            return

        print(f"\nFound {len(problems)} problems to migrate:")
        for p in problems:
            print(f"  - {p['slug']} ({p['path']})")

        # Confirm migration
        response = input(f"\nProceed with migration? (y/N): ").strip().lower()
        if response != 'y':
            print("Migration cancelled.")
            return

        # Migrate each problem
        print(f"\nMigrating problems as user: {self.owner_user['name']}")
        print("-" * 50)

        for problem in problems:
            self.migrate_problem(problem)

        # Summary
        print("\n" + "=" * 50)
        print("Migration Summary:")
        print(f"  ✅ Migrated: {self.migrated_count}")
        print(f"  ⚠️  Skipped:  {self.skipped_count}")
        print(f"  ❌ Errors:   {self.error_count}")
        print(f"  📊 Total:    {len(problems)}")

        if self.migrated_count > 0:
            print(f"\n🎉 Successfully migrated {self.migrated_count} problems!")
            print("You can now view them in the dashboard.")


def main():
    if len(sys.argv) != 2:
        print("Usage: python migrate_production_problems.py <owner_email>")
        print("Example: python migrate_production_problems.py your.email@gmail.com")
        sys.exit(1)

    owner_email = sys.argv[1]

    migrator = ProductionMigrator(owner_email)
    migrator.run_migration()


if __name__ == "__main__":
    main()
