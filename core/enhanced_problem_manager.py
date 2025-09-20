"""
Enhanced Problem Manager for multi-user PocketOJ
Integrates database-driven problem management with file-based problem structure
"""

import uuid
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

from .database import DatabaseManager
from .config import config


class EnhancedProblemManager:
    """Enhanced problem manager with multi-user support"""

    def __init__(self, db_manager: DatabaseManager, problems_dir: str = None):
        self.db = db_manager
        self.problems_dir = Path(problems_dir or config.get(
            'system.problems_dir', 'problems'))
        self.problems_dir.mkdir(parents=True, exist_ok=True)

    def create_problem(self, title: str, author_id: str, **kwargs) -> Dict[str, Any]:
        """Create a new problem with multi-user support"""
        # Generate unique slug
        slug = self.generate_unique_slug(title)
        problem_id = str(uuid.uuid4())

        # Prepare problem data for database
        problem_data = {
            'id': problem_id,
            'slug': slug,
            'title': title,
            'author_id': author_id,
            # Start as private by default
            'is_public': kwargs.get('is_public', False),
            'difficulty': kwargs.get('difficulty', 'Medium'),
            'tags': kwargs.get('tags', []),
        }

        # Insert into database
        self.db.insert_problem(problem_data)

        # Create file structure
        self.create_problem_file_structure(slug, problem_data)

        return {
            'id': problem_id,
            'slug': slug,
            'title': title,
            'author_id': author_id,
            'is_public': problem_data['is_public']
        }

    def generate_unique_slug(self, title: str) -> str:
        """Generate a unique slug from title"""
        import re

        # Convert to lowercase and replace spaces/special chars with hyphens
        slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
        slug = re.sub(r'\s+', '-', slug.strip())
        slug = re.sub(r'-+', '-', slug).strip('-')

        # Ensure it's not empty
        if not slug:
            slug = f"problem-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # Check for uniqueness
        original_slug = slug
        counter = 1
        while self.db.get_problem_by_slug(slug) is not None:
            slug = f"{original_slug}-{counter}"
            counter += 1

        return slug

    def create_problem_file_structure(self, slug: str, problem_data: Dict) -> None:
        """Create the file structure for a new problem"""
        problem_dir = self.problems_dir / slug
        problem_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (problem_dir / 'tests' / 'samples').mkdir(parents=True, exist_ok=True)
        (problem_dir / 'tests' / 'system').mkdir(parents=True, exist_ok=True)
        (problem_dir / 'checker').mkdir(parents=True, exist_ok=True)

        # Create config.yaml
        config_content = {
            'title': problem_data['title'],
            'slug': problem_data['slug'],
            'difficulty': problem_data['difficulty'],
            'tags': problem_data['tags'],
            'limits': {
                'time_ms': 1000,
                'memory_mb': 256
            },
            'files': {
                'has_statement': False,
                'has_solution': False,
                'has_generator': False,
                'has_validator': False,
                'has_custom_checker': False
            },
            'checker': {
                'type': 'diff',
                'float_tolerance': 1e-6,
                'spj_path': 'checker/spj'
            },
            'tests': {
                'sample_count': 3,
                'system_count': 20
            },
            'validation': {
                'enabled': False,
                'strict_mode': True
            },
            'created_date': datetime.utcnow().isoformat(),
            '_multiuser_problem': True,
            '_problem_id': problem_data['id']
        }

        config_file = problem_dir / 'config.yaml'
        with open(config_file, 'w') as f:
            import yaml
            yaml.dump(config_content, f,
                      default_flow_style=False, sort_keys=False)

        # Create basic statement template
        statement_content = f"""# {problem_data['title']}

## Problem Statement

*Write your problem description here...*

## Input Format

*Describe the input format...*

## Output Format

*Describe the output format...*

## Sample Test Cases

### Sample Input 1
```
*Add sample input here*
```

### Sample Output 1
```
*Add expected output here*
```

## Constraints

*Add problem constraints here...*

## Notes

*Add any additional notes or explanations...*
"""

        statement_file = problem_dir / 'statement.md'
        with open(statement_file, 'w') as f:
            f.write(statement_content)

        print(f"✅ Created problem structure for '{slug}'")

    def get_user_problems(self, user_id: str) -> List[Dict]:
        """Get all problems created by a user with enhanced metadata"""
        problems = self.db.get_user_problems(user_id)

        # Enhance with file system information
        for problem in problems:
            problem.update(self.get_problem_file_info(problem['slug']))

        return problems

    def get_problem_file_info(self, slug: str) -> Dict[str, Any]:
        """Get file system information for a problem"""
        problem_dir = self.problems_dir / slug

        if not problem_dir.exists():
            return {
                'exists': False,
                'completion_percentage': 0,
                'missing_files': ['problem directory not found']
            }

        # Check essential files
        essential_files = {
            'statement.md': 'Statement',
            'solution.py': 'Reference Solution',
            'generator.py': 'Test Generator',
        }

        optional_files = {
            'validator.py': 'Input Validator',
            'checker/spj.cpp': 'Special Judge'
        }

        existing_files = []
        missing_files = []

        for file_path, description in essential_files.items():
            if (problem_dir / file_path).exists():
                existing_files.append(description)
            else:
                missing_files.append(description)

        for file_path, description in optional_files.items():
            if (problem_dir / file_path).exists():
                existing_files.append(description)

        # Calculate completion percentage
        total_essential = len(essential_files)
        completed_essential = len([f for f in essential_files.keys()
                                   if (problem_dir / f).exists()])
        completion_percentage = int(
            (completed_essential / total_essential) * 100)

        # Check test cases
        test_stats = self.get_test_case_stats(slug)

        return {
            'exists': True,
            'completion_percentage': completion_percentage,
            'existing_files': existing_files,
            'missing_files': missing_files,
            'is_complete': completion_percentage == 100,
            'test_cases': test_stats
        }

    def get_test_case_stats(self, slug: str) -> Dict[str, int]:
        """Get test case statistics for a problem"""
        problem_dir = self.problems_dir / slug
        stats = {}

        for category in ['samples', 'system']:
            test_dir = problem_dir / 'tests' / category
            if test_dir.exists():
                stats[category] = len(list(test_dir.glob('*.in')))
            else:
                stats[category] = 0

        return stats

    def delete_problem(self, slug: str, author_id: str) -> bool:
        """Delete a problem (only by author)"""
        # Delete from database first
        db_success = self.db.delete_problem(slug, author_id)

        if db_success:
            # Delete file structure
            problem_dir = self.problems_dir / slug
            if problem_dir.exists():
                try:
                    shutil.rmtree(problem_dir)
                    print(f"✅ Deleted problem files for '{slug}'")
                except Exception as e:
                    print(
                        f"⚠️  Failed to delete problem files for '{slug}': {e}")

        return db_success

    def toggle_problem_visibility(self, slug: str, author_id: str) -> Optional[bool]:
        """Toggle problem visibility between public and private"""
        return self.db.toggle_problem_visibility(slug, author_id)

    def get_public_problems(self, **kwargs) -> Dict:
        """Get public problems with enhanced metadata"""
        result = self.db.get_public_problems(**kwargs)

        # Enhance problems with file system information
        for problem in result['problems']:
            file_info = self.get_problem_file_info(problem['slug'])
            problem.update({
                'completion_percentage': file_info['completion_percentage'],
                'test_cases': file_info['test_cases']
            })

        return result

    def get_problem_with_legacy_support(self, slug: str) -> Optional[Dict]:
        """Get problem with both database and legacy file system support"""
        # Get from database first
        problem_data = self.db.get_problem_by_slug(slug)

        if problem_data:
            # Enhance with file system information
            file_info = self.get_problem_file_info(slug)
            problem_data.update(file_info)
            return problem_data

        # Fallback: check if it's a legacy problem (file-only)
        problem_dir = self.problems_dir / slug
        if problem_dir.exists():
            config_file = problem_dir / 'config.yaml'
            if config_file.exists():
                try:
                    import yaml
                    with open(config_file, 'r') as f:
                        config_data = yaml.safe_load(f) or {}

                    # Return legacy problem format
                    return {
                        'slug': slug,
                        'title': config_data.get('title', slug.replace('-', ' ').title()),
                        'difficulty': config_data.get('difficulty', 'Medium'),
                        'tags': config_data.get('tags', []),
                        'is_public': False,  # Legacy problems are private by default
                        'author_id': None,   # No author for legacy problems
                        'legacy_problem': True,
                        **self.get_problem_file_info(slug)
                    }
                except Exception as e:
                    print(f"Error reading legacy problem config: {e}")

        return None

    def migrate_legacy_problem(self, slug: str, admin_user_id: str) -> bool:
        """Migrate a legacy problem to the multi-user system"""
        legacy_problem = self.get_problem_with_legacy_support(slug)

        if not legacy_problem or not legacy_problem.get('legacy_problem'):
            return False

        try:
            # Create database entry for legacy problem
            problem_data = {
                'id': str(uuid.uuid4()),
                'slug': slug,
                'title': legacy_problem['title'],
                'author_id': admin_user_id,
                'is_public': True,  # Make legacy problems public by default
                'difficulty': legacy_problem['difficulty'],
                'tags': legacy_problem['tags'],
            }

            self.db.insert_problem(problem_data)

            # Update config file to mark as migrated
            config_file = self.problems_dir / slug / 'config.yaml'
            if config_file.exists():
                import yaml
                with open(config_file, 'r') as f:
                    config_data = yaml.safe_load(f) or {}

                config_data.update({
                    '_migrated_to_multiuser': True,
                    '_migration_date': datetime.utcnow().isoformat(),
                    '_problem_id': problem_data['id']
                })

                with open(config_file, 'w') as f:
                    yaml.dump(config_data, f,
                              default_flow_style=False, sort_keys=False)

            print(f"✅ Migrated legacy problem '{slug}' to multi-user system")
            return True

        except Exception as e:
            print(f"❌ Failed to migrate legacy problem '{slug}': {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get enhanced statistics for the dashboard"""
        # Get basic database stats
        try:
            # Count public problems
            public_result = self.db.get_public_problems(page=1, limit=1)
            public_count = public_result['total']

            # Count total problems in database
            with self.db.db.get_connection() as conn:
                total_problems = conn.execute(
                    "SELECT COUNT(*) FROM problems").fetchone()[0]

            # Get difficulty breakdown
            with self.db.db.get_connection() as conn:
                difficulty_results = conn.execute("""
                    SELECT difficulty, COUNT(*) as count 
                    FROM problems 
                    GROUP BY difficulty
                """).fetchall()

            difficulty_breakdown = {row[0]: row[1]
                                    for row in difficulty_results}

            # Count file system problems (including legacy)
            file_system_count = len([d for d in self.problems_dir.iterdir()
                                     if d.is_dir() and not d.name.startswith('.')])

            return {
                'total_problems': total_problems,
                'public_problems': public_count,
                'private_problems': total_problems - public_count,
                'file_system_problems': file_system_count,
                'difficulty_breakdown': difficulty_breakdown,
                'multiuser_enabled': True
            }

        except Exception as e:
            print(f"Error getting statistics: {e}")
            # Fallback to file system only
            return {
                'total_problems': 0,
                'public_problems': 0,
                'private_problems': 0,
                'file_system_problems': 0,
                'difficulty_breakdown': {},
                'multiuser_enabled': True,
                'error': str(e)
            }
