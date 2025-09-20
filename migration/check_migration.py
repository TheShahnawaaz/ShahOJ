#!/usr/bin/env python3
"""
Check what problems would be migrated without actually doing the migration.
"""

import os
import sys
import yaml
from pathlib import Path


def check_problems():
    """Check what problems are available for migration"""

    problem_dirs = [
        Path("problems_backup"),
        Path("problems"),
    ]

    all_problems = []

    for problem_dir in problem_dirs:
        if not problem_dir.exists():
            continue

        print(f"📁 Checking {problem_dir}/")

        for item in problem_dir.iterdir():
            if not item.is_dir():
                continue

            # Look for config files
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
                # Load config to get details
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)

                    title = config.get('title', item.name)
                    difficulty = config.get('difficulty', 'Unknown')
                    tags = config.get('tags', [])

                    problem_info = {
                        'slug': item.name,
                        'title': title,
                        'difficulty': difficulty,
                        'tags': tags,
                        'path': str(item),
                        'config_file': str(config_file)
                    }

                    all_problems.append(problem_info)

                    print(f"  ✅ {item.name}")
                    print(f"     Title: {title}")
                    print(f"     Difficulty: {difficulty}")
                    print(f"     Tags: {', '.join(tags) if tags else 'None'}")
                    print()

                except Exception as e:
                    print(f"  ❌ {item.name} - Error reading config: {e}")
            else:
                print(f"  ⚠️  {item.name} - No config file found")

    print("=" * 60)
    print(f"📊 Summary: Found {len(all_problems)} problems ready for migration")

    if all_problems:
        print("\n🚀 To migrate these problems, run:")
        print("python migrate_production_problems.py your.email@gmail.com")
        print("\n⚠️  Make sure to:")
        print("1. Log in to the website with Google first (to create your user account)")
        print("2. Use the same email address you logged in with")

    return all_problems


if __name__ == "__main__":
    check_problems()
