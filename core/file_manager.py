"""
File management system for problem files
Handles creation, validation, and testing of problem files
"""

import subprocess
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, Tuple, Optional


class FileManager:
    """Manages problem files and their integration"""

    def __init__(self, problem_dir: Path):
        self.problem_dir = Path(problem_dir)

    def save_file(self, filename: str, content: str) -> bool:
        """Save a file with content validation"""
        try:
            file_path = self.problem_dir / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'w') as f:
                f.write(content)

            return True
        except Exception as e:
            print(f"Error saving {filename}: {e}")
            return False

    def load_file(self, filename: str) -> Optional[str]:
        """Load file content"""
        try:
            file_path = self.problem_dir / filename
            if file_path.exists():
                with open(file_path, 'r') as f:
                    return f.read()
            return None
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return None

    def validate_python_syntax(self, content: str) -> Tuple[bool, str]:
        """Validate Python file syntax"""
        try:
            compile(content, '<string>', 'exec')
            return True, "Valid Python syntax"
        except SyntaxError as e:
            return False, f"Python syntax error: {e.msg} at line {e.lineno}"
        except Exception as e:
            return False, f"Python validation error: {str(e)}"

    def validate_cpp_syntax(self, content: str) -> Tuple[bool, str]:
        """Validate C++ file syntax (basic check)"""
        try:
            # Create temporary file and try to compile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as tmp_file:
                tmp_file.write(content)
                tmp_path = tmp_file.name

            try:
                # Try to compile (syntax check only)
                result = subprocess.run(
                    ['g++', '-fsyntax-only', '-std=c++17', tmp_path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0:
                    return True, "Valid C++ syntax"
                else:
                    return False, f"C++ syntax error: {result.stderr}"

            finally:
                os.unlink(tmp_path)

        except Exception as e:
            return False, f"C++ validation error: {str(e)}"

    def compile_spj(self, spj_content: str, problem_slug: str) -> Tuple[bool, str]:
        """Compile Special Judge (SPJ) C++ code"""
        try:
            checker_dir = self.problem_dir / 'checker'
            checker_dir.mkdir(exist_ok=True)

            # Ensure testlib.h exists
            testlib_path = checker_dir / 'testlib.h'
            if not testlib_path.exists():
                # Copy testlib.h from another problem or download it
                self._ensure_testlib(checker_dir)

            # Save SPJ source code
            spj_source = checker_dir / 'spj.cpp'
            with open(spj_source, 'w') as f:
                f.write(spj_content)

            # Compile SPJ
            spj_executable = checker_dir / 'spj'
            compile_cmd = ['g++', '-std=c++17', '-O2',
                           str(spj_source), '-o', str(spj_executable)]

            result = subprocess.run(
                compile_cmd,
                cwd=str(checker_dir),
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return True, f"SPJ compiled successfully: {spj_executable}"
            else:
                return False, f"SPJ compilation failed: {result.stderr}"

        except Exception as e:
            return False, f"SPJ compilation error: {str(e)}"

    def _ensure_testlib(self, checker_dir: Path):
        """Ensure testlib.h exists in checker directory"""
        testlib_path = checker_dir / 'testlib.h'

        # Try to copy from existing problem
        project_root = self.problem_dir.parent.parent if self.problem_dir.parent.name == 'problems' else self.problem_dir.parent
        existing_testlib_locations = [
            project_root / 'problems' / 'strictly-smaller' / 'checker' / 'testlib.h',
            project_root / 'judge' / 'testlib.h',
            project_root / 'testlib.h'
        ]

        for source_path in existing_testlib_locations:
            if source_path.exists():
                import shutil
                shutil.copy2(source_path, testlib_path)
                print(f"Copied testlib.h from {source_path}")
                return

        # If no existing testlib.h found, download it
        try:
            import urllib.request
            print("Downloading testlib.h from GitHub...")
            urllib.request.urlretrieve(
                'https://raw.githubusercontent.com/MikeMirzayanov/testlib/master/testlib.h',
                str(testlib_path)
            )
            print("Downloaded testlib.h successfully")
        except Exception as e:
            print(f"Warning: Could not download testlib.h: {e}")
            # Create a minimal placeholder that will cause compilation error with clear message
            with open(testlib_path, 'w') as f:
                f.write(
                    '// testlib.h not available - download from https://github.com/MikeMirzayanov/testlib\n')

    def test_spj_compilation(self, spj_content: str) -> Tuple[bool, str]:
        """Test SPJ compilation without saving to disk"""
        try:
            # Create temporary directory for testing
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dir_path = Path(temp_dir)
                checker_dir = temp_dir_path / 'checker'
                checker_dir.mkdir()

                # Copy testlib.h
                self._ensure_testlib(checker_dir)

                # Save SPJ source
                spj_source = checker_dir / 'spj.cpp'
                with open(spj_source, 'w') as f:
                    f.write(spj_content)

                # Try to compile
                spj_executable = checker_dir / 'spj'
                result = subprocess.run(
                    ['g++', '-std=c++17', '-O2',
                        str(spj_source), '-o', str(spj_executable)],
                    cwd=str(checker_dir),
                    capture_output=True,
                    text=True,
                    timeout=15
                )

                if result.returncode == 0:
                    return True, "SPJ compiles successfully"
                else:
                    return False, f"SPJ compilation error: {result.stderr}"

        except Exception as e:
            return False, f"SPJ test error: {str(e)}"

    def test_generator_interface(self, generator_content: str) -> Tuple[bool, str, str]:
        """Test that generator follows the standard interface"""
        try:
            # Save generator to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp_file:
                tmp_file.write(generator_content)
                tmp_path = tmp_file.name

            try:
                # Test generator with standard parameters
                result = subprocess.run(
                    ['python3', tmp_path, 'small', '1', '12345'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0:
                    output = result.stdout.strip()
                    if output:
                        return True, "Generator interface works", output
                    else:
                        return False, "Generator produces no output", ""
                else:
                    return False, f"Generator error: {result.stderr}", ""

            finally:
                os.unlink(tmp_path)

        except Exception as e:
            return False, f"Generator test error: {str(e)}", ""

    def test_solution_integration(self, solution_content: str, test_input: str) -> Tuple[bool, str, str]:
        """Test that solution can handle generator output"""
        try:
            # Save solution to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp_file:
                tmp_file.write(solution_content)
                tmp_path = tmp_file.name

            try:
                # Run solution with test input
                result = subprocess.run(
                    ['python3', tmp_path],
                    input=test_input,
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0:
                    output = result.stdout.strip()
                    return True, "Solution handles input correctly", output
                else:
                    return False, f"Solution error: {result.stderr}", ""

            finally:
                os.unlink(tmp_path)

        except Exception as e:
            return False, f"Solution test error: {str(e)}", ""

    def test_validator_integration(self, validator_content: str, test_input: str) -> Tuple[bool, str]:
        """Test that validator accepts generator output"""
        try:
            # Save validator to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp_file:
                tmp_file.write(validator_content)
                tmp_path = tmp_file.name

            try:
                # Run validator with test input
                result = subprocess.run(
                    ['python3', tmp_path],
                    input=test_input,
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0:
                    return True, "Validator accepts input"
                else:
                    return False, f"Validator rejects input: {result.stdout}"

            finally:
                os.unlink(tmp_path)

        except Exception as e:
            return False, f"Validator test error: {str(e)}"

    def test_file_integration(self, files: Dict[str, str]) -> Dict[str, Any]:
        """Test that all provided files work together"""
        results = {
            'success': False,
            'errors': [],
            'warnings': [],
            'preview': {
                'input': '',
                'output': '',
                'valid': False
            }
        }

        # Test generator first
        if 'generator.py' in files:
            gen_ok, gen_msg, test_input = self.test_generator_interface(
                files['generator.py'])
            if not gen_ok:
                results['errors'].append(f"Generator: {gen_msg}")
                return results

            results['preview']['input'] = test_input

            # Test solution with generator output
            if 'solution.py' in files:
                sol_ok, sol_msg, solution_output = self.test_solution_integration(
                    files['solution.py'], test_input)
                if not sol_ok:
                    results['errors'].append(f"Solution: {sol_msg}")
                    return results

                results['preview']['output'] = solution_output

                # Test validator if provided
                if 'validator.py' in files:
                    val_ok, val_msg = self.test_validator_integration(
                        files['validator.py'], test_input)
                    if not val_ok:
                        results['warnings'].append(f"Validator: {val_msg}")
                    else:
                        results['preview']['valid'] = True
                else:
                    results['warnings'].append(
                        "No validator provided - inputs won't be validated")
            else:
                results['errors'].append("Solution: solution.py is required")
                return results
        else:
            results['errors'].append("Generator: generator.py is required")
            return results

        if len(results['errors']) == 0:
            results['success'] = True

        return results
