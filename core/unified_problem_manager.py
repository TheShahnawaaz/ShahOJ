"""
Unified Problem Manager - Database as Single Source of Truth
Eliminates YAML config duplication and uses database for all metadata
"""

import uuid
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

from .database import DatabaseManager
from .config import config


class UnifiedProblemManager:
    """
    Unified problem manager that uses database as single source of truth
    Files are used only for content (statement, solution, etc.)
    All metadata comes from database
    """

    def __init__(self, db_manager: DatabaseManager, problems_dir: str = None):
        self.db = db_manager
        self.problems_dir = Path(problems_dir or config.get(
            'system.problems_dir', 'problems'))
        self.problems_dir.mkdir(parents=True, exist_ok=True)

    def create_problem(self, title: str, author_id: str, **kwargs) -> Dict[str, Any]:
        """Create a new problem with database-only metadata"""
        # Generate unique slug
        slug = self.generate_unique_slug(title)
        problem_id = str(uuid.uuid4())

        # Prepare problem data for database (all metadata)
        problem_data = {
            'id': problem_id,
            'slug': slug,
            'title': title,
            'author_id': author_id,
            'is_public': kwargs.get('is_public', False),
            'difficulty': kwargs.get('difficulty', 'Medium'),
            'tags': kwargs.get('tags', []),

            # Execution limits
            'time_limit_ms': kwargs.get('time_limit_ms', 1000),
            'memory_limit_mb': kwargs.get('memory_limit_mb', 256),

            # Checker configuration
            'checker_type': kwargs.get('checker_type', 'diff'),
            'checker_tolerance': kwargs.get('checker_tolerance', 1e-6),

            # Test configuration
            'sample_count': kwargs.get('sample_count', 3),
            'system_count': kwargs.get('system_count', 20),

            # Validation settings
            'validation_enabled': kwargs.get('validation_enabled', False),
            'validation_strict': kwargs.get('validation_strict', True),

            # File status (will be updated when files are created)
            'has_statement': False,
            'has_solution': False,
            'has_generator': False,
            'has_validator': False,
            'has_custom_checker': False,
        }

        # Insert into database (single source of truth)
        self.db.insert_problem(problem_data)

        # Create file structure (content only, no config.yaml)
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
        slug = re.sub(r'-+', '-', slug)

        # Ensure uniqueness
        original_slug = slug
        counter = 1

        while self.db.get_problem_by_slug(slug):
            slug = f"{original_slug}-{counter}"
            counter += 1

        return slug

    def create_problem_file_structure(self, slug: str, problem_data: Dict) -> None:
        """Create file structure (content only, NO config.yaml)"""
        problem_dir = self.problems_dir / slug

        # Create directories
        (problem_dir / 'tests' / 'samples').mkdir(parents=True, exist_ok=True)
        (problem_dir / 'tests' / 'system').mkdir(parents=True, exist_ok=True)
        (problem_dir / 'checker').mkdir(parents=True, exist_ok=True)

        # Create basic statement template (content only)
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

        # Update file status in database
        self.update_file_status(slug)

    def get_problem(self, slug: str) -> Optional['UnifiedProblem']:
        """Get problem with all data from database"""
        problem_data = self.db.get_problem_by_slug(slug)
        if not problem_data:
            return None

        return UnifiedProblem(slug, self.problems_dir / slug, problem_data, self.db)

    def get_problem_metadata(self, slug: str) -> Optional[Dict]:
        """Get problem metadata directly from database"""
        return self.db.get_problem_by_slug(slug)

    def update_problem_metadata(self, slug: str, metadata: Dict, author_id: str = None) -> bool:
        """Update problem metadata in database"""
        return self.db.update_problem_metadata(slug, metadata, author_id)

    def delete_problem(self, slug: str, author_id: str = None) -> bool:
        """Delete a problem (database + files)"""
        # Delete from database first
        db_success = self.db.delete_problem(slug, author_id)

        if db_success:
            # Delete files
            problem_dir = self.problems_dir / slug
            if problem_dir.exists():
                try:
                    shutil.rmtree(problem_dir)
                    return True
                except Exception as e:
                    print(f"Warning: Failed to delete problem files: {e}")
                    return True  # Database deletion succeeded

        return False

    def problem_exists(self, slug: str) -> bool:
        """Check if a problem exists (database check only)"""
        return self.db.get_problem_by_slug(slug) is not None

    def update_file_status(self, slug: str):
        """Update file status flags in database by scanning actual files"""
        problem_dir = self.problems_dir / slug

        if problem_dir.exists():
            file_status = {
                'has_statement': (problem_dir / 'statement.md').exists(),
                'has_solution': (problem_dir / 'solution.py').exists(),
                'has_generator': (problem_dir / 'generator.py').exists(),
                'has_validator': (problem_dir / 'validator.py').exists(),
                'has_custom_checker': (problem_dir / 'checker' / 'spj.cpp').exists(),
            }

            self.db.update_file_status(slug, file_status)

    def list_problems(self) -> List['UnifiedProblem']:
        """List all problems from database"""
        # Get all public problems
        public_problems = self.db.get_public_problems(page=1, limit=1000)[
            'problems']

        # Get all private problems (from all users)
        try:
            import sqlite3
            with sqlite3.connect(self.db.db_path) as conn:
                conn.row_factory = sqlite3.Row
                private_problems = conn.execute("""
                    SELECT * FROM problems WHERE is_public = 0
                    ORDER BY updated_at DESC
                """).fetchall()
                private_problems = [dict(row) for row in private_problems]
        except Exception as e:
            print(f"Warning: Could not fetch private problems: {e}")
            private_problems = []

        # Combine and create UnifiedProblem objects
        all_problems = []
        seen_slugs = set()

        for problem_data in public_problems + private_problems:
            if problem_data['slug'] not in seen_slugs:
                seen_slugs.add(problem_data['slug'])
                problem_dir = self.problems_dir / problem_data['slug']
                if problem_dir.exists():
                    unified_problem = UnifiedProblem(
                        problem_data['slug'],
                        problem_dir,
                        problem_data,
                        self.db
                    )
                    all_problems.append(unified_problem)

        return all_problems

    def create_problem_structure(self, slug: str, metadata: Dict) -> 'UnifiedProblem':
        """Create problem structure (for backward compatibility with legacy code)"""
        # This method is for backward compatibility with existing routes
        # It creates the file structure and returns a UnifiedProblem object

        problem_dir = self.problems_dir / slug

        # Create directories
        (problem_dir / 'tests' / 'samples').mkdir(parents=True, exist_ok=True)
        (problem_dir / 'tests' / 'system').mkdir(parents=True, exist_ok=True)
        (problem_dir / 'checker').mkdir(parents=True, exist_ok=True)

        # Get problem data from database (should already exist)
        problem_data = self.db.get_problem_by_slug(slug)
        if not problem_data:
            # If not in database, this is a legacy creation, create minimal data
            problem_data = {
                'slug': slug,
                'title': metadata.get('title', slug),
                'difficulty': metadata.get('difficulty', 'Medium'),
                'tags': metadata.get('tags', []),
                'time_limit_ms': metadata.get('time_limit_ms', 1000),
                'memory_limit_mb': metadata.get('memory_limit_mb', 256),
                'checker_type': metadata.get('checker_type', 'diff'),
                'checker_tolerance': metadata.get('checker_tolerance', 1e-6),
                'sample_count': metadata.get('sample_count', 3),
                'system_count': metadata.get('system_count', 20),
                'validation_enabled': metadata.get('validation_enabled', False),
                'validation_strict': metadata.get('validation_strict', True),
                'has_statement': False,
                'has_solution': False,
                'has_generator': False,
                'has_validator': False,
                'has_custom_checker': False,
            }

        return UnifiedProblem(slug, problem_dir, problem_data, self.db)

    def get_statistics(self) -> Dict:
        """Get problem statistics"""
        try:
            import sqlite3
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()

                # Count total problems
                total = cursor.execute(
                    "SELECT COUNT(*) FROM problems").fetchone()[0]

                # Count public problems
                public = cursor.execute(
                    "SELECT COUNT(*) FROM problems WHERE is_public = 1").fetchone()[0]

                # Count by difficulty
                easy = cursor.execute(
                    "SELECT COUNT(*) FROM problems WHERE difficulty = 'Easy'").fetchone()[0]
                medium = cursor.execute(
                    "SELECT COUNT(*) FROM problems WHERE difficulty = 'Medium'").fetchone()[0]
                hard = cursor.execute(
                    "SELECT COUNT(*) FROM problems WHERE difficulty = 'Hard'").fetchone()[0]

                return {
                    'total_problems': total,
                    'public_problems': public,
                    'private_problems': total - public,
                    'difficulty_distribution': {
                        'Easy': easy,
                        'Medium': medium,
                        'Hard': hard
                    }
                }
        except Exception as e:
            print(f"Warning: Could not get statistics: {e}")
            return {
                'total_problems': 0,
                'public_problems': 0,
                'private_problems': 0,
                'difficulty_distribution': {'Easy': 0, 'Medium': 0, 'Hard': 0}
            }


class UnifiedProblem:
    """
    Unified Problem class that gets all metadata from database
    No more YAML config files - database is the single source of truth
    """

    def __init__(self, slug: str, problem_dir: Path, problem_data: Dict, db_manager: DatabaseManager):
        self.slug = slug
        self.problem_dir = Path(problem_dir)
        self.db_data = problem_data
        self.db = db_manager

    @property
    def config(self) -> Dict:
        """Get problem configuration from database (compatibility with old code)"""
        return {
            'title': self.db_data.get('title', ''),
            'slug': self.db_data.get('slug', ''),
            'difficulty': self.db_data.get('difficulty', 'Medium'),
            'tags': self.db_data.get('tags', []),
            'limits': {
                'time_ms': self.db_data.get('time_limit_ms', 1000),
                'memory_mb': self.db_data.get('memory_limit_mb', 256)
            },
            'checker': {
                'type': self.db_data.get('checker_type', 'diff'),
                'float_tolerance': self.db_data.get('checker_tolerance', 1e-6)
            },
            'tests': {
                'sample_count': self.db_data.get('sample_count', 3),
                'system_count': self.db_data.get('system_count', 20)
            },
            'validation': {
                'enabled': self.db_data.get('validation_enabled', False),
                'strict_mode': self.db_data.get('validation_strict', True)
            },
            'files': {
                'has_statement': self.db_data.get('has_statement', False),
                'has_solution': self.db_data.get('has_solution', False),
                'has_generator': self.db_data.get('has_generator', False),
                'has_validator': self.db_data.get('has_validator', False),
                'has_custom_checker': self.db_data.get('has_custom_checker', False)
            }
        }

    def get(self, key: str, default=None):
        """Get configuration value (compatibility method)"""
        config = self.config
        keys = key.split('.')

        current = config
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default

        return current

    def exists(self) -> bool:
        """Check if problem exists (directory exists)"""
        return self.problem_dir.exists()

    def get_test_cases_count(self) -> Dict[str, int]:
        """Get test case counts by scanning directories"""
        counts = {'samples': 0, 'system': 0, 'pretests': 0}

        # Count sample test cases
        samples_dir = self.problem_dir / 'tests' / 'samples'
        if samples_dir.exists():
            input_files = list(samples_dir.glob('*.in'))
            counts['samples'] = len(input_files)

        # Count system test cases
        system_dir = self.problem_dir / 'tests' / 'system'
        if system_dir.exists():
            input_files = list(system_dir.glob('*.in'))
            counts['system'] = len(input_files)

        return counts

    def get_files_info(self) -> Dict[str, bool]:
        """Get file existence information"""
        return {
            'statement.md': (self.problem_dir / 'statement.md').exists(),
            'solution.py': (self.problem_dir / 'solution.py').exists(),
            'generator.py': (self.problem_dir / 'generator.py').exists(),
            'validator.py': (self.problem_dir / 'validator.py').exists(),
            'checker/spj.cpp': (self.problem_dir / 'checker' / 'spj.cpp').exists(),
        }

    def save_config(self, config_data):
        """
        Save configuration to database (NO MORE YAML FILES)
        This method updates the database with new metadata
        """
        metadata = {}

        # Extract metadata from config_data
        if 'title' in config_data:
            metadata['title'] = config_data['title']
        if 'difficulty' in config_data:
            metadata['difficulty'] = config_data['difficulty']
        if 'tags' in config_data:
            metadata['tags'] = config_data['tags']

        # Extract limits
        if 'limits' in config_data:
            limits = config_data['limits']
            if 'time_ms' in limits:
                metadata['time_limit_ms'] = limits['time_ms']
            if 'memory_mb' in limits:
                metadata['memory_limit_mb'] = limits['memory_mb']

        # Extract checker config
        if 'checker' in config_data:
            checker = config_data['checker']
            if 'type' in checker:
                metadata['checker_type'] = checker['type']
            if 'float_tolerance' in checker:
                metadata['checker_tolerance'] = checker['float_tolerance']

        # Extract test config
        if 'tests' in config_data:
            tests = config_data['tests']
            if 'sample_count' in tests:
                metadata['sample_count'] = tests['sample_count']
            if 'system_count' in tests:
                metadata['system_count'] = tests['system_count']

        # Extract validation config
        if 'validation' in config_data:
            validation = config_data['validation']
            if 'enabled' in validation:
                metadata['validation_enabled'] = validation['enabled']
            if 'strict_mode' in validation:
                metadata['validation_strict'] = validation['strict_mode']

        # Update database
        if metadata:
            self.db.update_problem_metadata(self.slug, metadata)

        # Update file status
        from core.unified_problem_manager import UnifiedProblemManager
        manager = UnifiedProblemManager(self.db)
        manager.update_file_status(self.slug)
