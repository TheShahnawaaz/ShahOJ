"""
Test case generation system for ShahOJ
"""

import os
import subprocess
import tempfile
import random
from pathlib import Path
from typing import Dict, List, Tuple, Any


class TestGenerator:
    """Generates test cases for competitive programming problems"""

    def __init__(self, problem):
        self.problem = problem
        self.problem_dir = Path(problem.problem_dir)
        self.solution_file = self.problem_dir / 'solution.py'
        self.generator_file = self.problem_dir / 'generator.py'
        self.validator_file = self.problem_dir / 'validator.py'

    def generate_test_case(self, case_num: int, seed: int) -> Tuple[str, str]:
        """
        Generate a single test case and its answer.
        Returns (input_text, answer_text)
        """
        # Generate input using the problem's generator
        input_text = self._run_generator(case_num, seed)

        # Validate the generated input
        if not self._validate_input(input_text):
            raise ValueError("Generated input failed validation")

        # Generate answer using reference solution
        answer_text = self._run_solution(input_text)

        return input_text.strip(), answer_text.strip()

    def generate_cases(self, count: int) -> List[Dict[str, Any]]:
        """Generate multiple test cases"""
        test_cases = []
        base_seed = random.randint(10000, 99999)

        for i in range(count):
            seed = base_seed + i
            try:
                input_text, answer_text = self.generate_test_case(i + 1, seed)

                test_case_info = {
                    'case_num': i + 1,
                    'seed': seed,
                    'input': input_text,
                    'answer': answer_text,
                    'input_size': len(input_text.encode('utf-8')),
                    'lines': len(input_text.split('\n'))
                }

                test_cases.append(test_case_info)

            except Exception as e:
                print(f"Warning: Failed to generate case {i+1}: {e}")
                continue

        return test_cases

    def save_test_cases(self, test_cases: List[Dict[str, Any]],
                        test_category: str = 'system', replace_existing: bool = False):
        """
        Save generated test cases to files
        test_category: 'samples', 'pretests', or 'system'
        replace_existing: if True, clear existing tests first; if False, append to existing
        """
        test_dir = self.problem_dir / 'tests' / test_category
        test_dir.mkdir(parents=True, exist_ok=True)

        # Find next available test number
        if replace_existing:
            # Clear existing test cases first
            for existing_file in test_dir.glob('*.in'):
                existing_file.unlink()
            for existing_file in test_dir.glob('*.ans'):
                existing_file.unlink()
            test_num = 1
        else:
            # Find next available number to append
            existing_tests = list(test_dir.glob('*.in'))
            if existing_tests:
                test_numbers = [int(f.stem)
                                for f in existing_tests if f.stem.isdigit()]
                test_num = max(test_numbers) + 1 if test_numbers else 1
            else:
                test_num = 1

        total_saved = 0

        for test_case in test_cases:
            # Save input file
            in_file = test_dir / f"{test_num:02d}.in"
            with open(in_file, 'w') as f:
                f.write(test_case['input'] + '\n')

            # Save answer file
            ans_file = test_dir / f"{test_num:02d}.ans"
            with open(ans_file, 'w') as f:
                f.write(test_case['answer'] + '\n')

            test_num += 1
            total_saved += 1

        return total_saved

    def add_manual_test_case(self, input_text: str, test_category: str = 'samples') -> bool:
        """
        Add a manual test case with auto-generated answer
        Returns True if successful
        """
        try:
            # Validate input
            if not self._validate_input(input_text):
                raise ValueError("Input failed validation")

            # Generate answer
            answer_text = self._run_solution(input_text)

            # Find next available test number
            test_dir = self.problem_dir / 'tests' / test_category
            test_dir.mkdir(parents=True, exist_ok=True)

            existing_tests = list(test_dir.glob('*.in'))
            if existing_tests:
                test_numbers = [int(f.stem)
                                for f in existing_tests if f.stem.isdigit()]
                next_num = max(test_numbers) + 1 if test_numbers else 1
            else:
                next_num = 1

            # Save files
            in_file = test_dir / f"{next_num:02d}.in"
            ans_file = test_dir / f"{next_num:02d}.ans"

            with open(in_file, 'w') as f:
                f.write(input_text.strip() + '\n')

            with open(ans_file, 'w') as f:
                f.write(answer_text.strip() + '\n')

            return True

        except Exception as e:
            print(f"Error adding manual test case: {e}")
            return False

    def _run_generator(self, case_num: int, seed: int) -> str:
        """Run the problem's generator script"""
        if not self.generator_file.exists():
            raise FileNotFoundError(
                f"Generator not found: {self.generator_file}")

        try:
            generator_name = self.generator_file.name
            result = subprocess.run(
                ['python3', generator_name, str(case_num), str(seed)],
                cwd=str(self.problem_dir),
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                raise RuntimeError(f"Generator failed: {result.stderr}")

            return result.stdout

        except subprocess.TimeoutExpired:
            raise RuntimeError("Generator timed out")

    def _run_solution(self, input_text: str) -> str:
        """Run the reference solution to get the correct answer"""
        if not self.solution_file.exists():
            raise FileNotFoundError(
                f"Reference solution not found: {self.solution_file}")

        try:
            # Use relative path for solution within problem directory
            solution_name = self.solution_file.name
            result = subprocess.run(
                ['python3', solution_name],
                input=input_text,
                cwd=str(self.problem_dir),
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                raise RuntimeError(
                    f"Reference solution failed: {result.stderr}")

            return result.stdout

        except subprocess.TimeoutExpired:
            raise RuntimeError("Reference solution timed out")

    def _validate_input(self, input_text: str) -> bool:
        """Validate input using the problem's validator"""
        # Check if validation is enabled in config
        validation_enabled = self.problem.config.get(
            'validation.enabled', False)

        if not validation_enabled:
            return True  # Skip validation if disabled

        if not self.validator_file.exists():
            print(
                f"Warning: Validation enabled but no validator found at {self.validator_file}")
            return True  # Skip validation if no validator

        try:
            # Use relative path for validator within problem directory
            validator_name = self.validator_file.name
            result = subprocess.run(
                ['python3', validator_name],
                input=input_text,
                cwd=str(self.problem_dir),
                capture_output=True,
                text=True,
                timeout=5
            )

            return result.returncode == 0

        except Exception as e:
            print(f"Warning: Validation failed: {e}")
            return True  # Skip validation on error

    def get_test_case_statistics(self) -> Dict[str, Any]:
        """Get statistics about existing test cases"""
        stats = {
            'categories': {},
            'total_cases': 0,
            'total_size_bytes': 0
        }

        test_categories = ['samples', 'system']  # Removed pretests

        for category in test_categories:
            test_dir = self.problem_dir / 'tests' / category

            if test_dir.exists():
                in_files = list(test_dir.glob('*.in'))
                ans_files = list(test_dir.glob('*.ans'))

                total_size = sum(
                    f.stat().st_size for f in in_files + ans_files)

                stats['categories'][category] = {
                    'count': len(in_files),
                    'size_bytes': total_size,
                    'avg_size_bytes': total_size // max(1, len(in_files))
                }

                stats['total_cases'] += len(in_files)
                stats['total_size_bytes'] += total_size
            else:
                stats['categories'][category] = {
                    'count': 0,
                    'size_bytes': 0,
                    'avg_size_bytes': 0
                }

        return stats

    def delete_test_cases(self, category: str, test_numbers: List[int] = None) -> int:
        """
        Delete test cases from a category
        If test_numbers is None, deletes all test cases in category
        Returns number of test cases deleted
        """
        test_dir = self.problem_dir / 'tests' / category

        if not test_dir.exists():
            return 0

        deleted_count = 0

        if test_numbers is None:
            # Delete all test cases in category
            for in_file in test_dir.glob('*.in'):
                ans_file = test_dir / (in_file.stem + '.ans')
                in_file.unlink()
                if ans_file.exists():
                    ans_file.unlink()
                deleted_count += 1
        else:
            # Delete specific test numbers
            for test_num in test_numbers:
                in_file = test_dir / f"{test_num:02d}.in"
                ans_file = test_dir / f"{test_num:02d}.ans"

                if in_file.exists():
                    in_file.unlink()
                    deleted_count += 1
                if ans_file.exists():
                    ans_file.unlink()

        return deleted_count
