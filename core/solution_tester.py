"""
Solution testing system for PocketOJ
Compiles and tests C++ solutions against problem test cases
"""

import os
import subprocess
import tempfile
import time
import resource
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

from .config import config


class SolutionResult:
    """Represents the result of testing a solution on a single test case"""

    def __init__(self, test_num: int, verdict: str, time_ms: float,
                 memory_kb: int = 0, details: str = "",
                 input_content: str = "", expected_output: str = "", actual_output: str = ""):
        self.test_num = test_num
        self.verdict = verdict  # AC, WA, TLE, RTE, CE, PE
        self.time_ms = time_ms
        self.memory_kb = memory_kb
        self.details = details
        self.input_content = input_content
        self.expected_output = expected_output
        self.actual_output = actual_output

    def to_dict(self) -> Dict[str, Any]:
        def truncate(text: str, max_length: int = 100) -> str:
            """Truncate text for summary display"""
            if len(text) <= max_length:
                return text
            return text[:max_length] + "..."

        return {
            'test_num': self.test_num,
            'verdict': self.verdict,
            'time_ms': round(self.time_ms, 2),
            'memory_kb': self.memory_kb,
            'details': self.details,
            # Full content for modal viewing
            'input_full': self.input_content,
            'expected_full': self.expected_output,
            'actual_full': self.actual_output,
            # Truncated content for summary display
            'input_truncated': truncate(self.input_content, 100),
            'expected_truncated': truncate(self.expected_output, 50),
            'actual_truncated': truncate(self.actual_output, 50),
            # Has content flags
            'has_content': bool(self.input_content or self.expected_output or self.actual_output)
        }


class SolutionTester:
    """Tests C++ solutions against competitive programming problems"""

    def __init__(self, problem):
        self.problem = problem
        self.problem_dir = Path(problem.problem_dir)

        # Get compiler settings
        self.compiler_cmd = config.get(
            'compiler.cpp.command', 'g++ -std=c++17 -O2 {src} -o {out}')
        self.compile_timeout = config.get('compiler.cpp.timeout', 30)

        # Get execution limits from problem config
        self.time_limit_ms = problem.config.get('time_limit_ms', 1000)
        self.memory_limit_mb = problem.config.get('memory_limit_mb', 256)

    def test_solution(self, cpp_code: str, test_categories: List[str] = None) -> Dict[str, Any]:
        """
        Test a C++ solution against all test cases
        Returns comprehensive results dictionary
        """
        if test_categories is None:
            test_categories = ['samples', 'pretests', 'system']

        results = {
            'overall_verdict': 'CE',  # Will be updated based on results
            'compilation': {'success': False, 'errors': '', 'time_ms': 0},
            'test_results': {},
            'statistics': {'total_tests': 0, 'passed': 0, 'failed': 0, 'total_time_ms': 0},
            'categories': {}
        }

        # Step 1: Compile the solution
        compile_result = self._compile_solution(cpp_code)
        results['compilation'] = compile_result

        if not compile_result['success']:
            return results

        executable_path = compile_result['executable_path']

        try:
            # Step 2: Run against all test cases
            for category in test_categories:
                category_results = self._test_category(
                    executable_path, category)
                # Convert SolutionResult objects to dictionaries for JSON serialization
                results['test_results'][category] = [result.to_dict()
                                                     for result in category_results]
                results['categories'][category] = self._summarize_category_results(
                    category_results)

            # Step 3: Calculate overall statistics
            results['statistics'] = self._calculate_statistics(
                results['test_results'])
            results['overall_verdict'] = self._determine_overall_verdict(
                results['test_results'])

        finally:
            # Clean up executable
            if os.path.exists(executable_path):
                os.remove(executable_path)

        return results

    def _compile_solution(self, cpp_code: str) -> Dict[str, Any]:
        """Compile C++ solution and return compilation result"""
        start_time = time.time()

        try:
            # Create temporary files
            with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as src_file:
                src_file.write(cpp_code)
                src_path = src_file.name

            # Create executable path
            exe_path = src_path.replace('.cpp', '')

            # Build compilation command
            compile_cmd = self.compiler_cmd.format(src=src_path, out=exe_path)

            # Compile
            result = subprocess.run(
                compile_cmd.split(),
                capture_output=True,
                text=True,
                timeout=self.compile_timeout
            )

            compile_time = (time.time() - start_time) * 1000

            # Clean up source file
            os.unlink(src_path)

            if result.returncode == 0:
                return {
                    'success': True,
                    'errors': '',
                    'time_ms': compile_time,
                    'executable_path': exe_path
                }
            else:
                # Clean up executable if it exists
                if os.path.exists(exe_path):
                    os.unlink(exe_path)

                return {
                    'success': False,
                    'errors': result.stderr,
                    'time_ms': compile_time,
                    'executable_path': ''
                }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'errors': 'Compilation timed out',
                'time_ms': self.compile_timeout * 1000,
                'executable_path': ''
            }

        except Exception as e:
            return {
                'success': False,
                'errors': str(e),
                'time_ms': (time.time() - start_time) * 1000,
                'executable_path': ''
            }

    def _test_category(self, executable_path: str, category: str) -> List[SolutionResult]:
        """Test solution against all test cases in a category"""
        test_dir = self.problem_dir / 'tests' / category
        results = []

        if not test_dir.exists():
            return results

        # Get all .in files and sort them
        test_files = sorted(test_dir.glob('*.in'), key=lambda x: x.name)

        for test_file in test_files:
            test_num = int(test_file.stem) if test_file.stem.isdigit() else 0
            ans_file = test_dir / (test_file.stem + '.ans')

            if not ans_file.exists():
                # Skip if no answer file
                continue

            # Run this test case
            result = self._run_single_test(
                executable_path, test_file, ans_file, test_num)
            results.append(result)

        return results

    def _run_single_test(self, executable_path: str, input_file: Path,
                         answer_file: Path, test_num: int) -> SolutionResult:
        """Run solution on a single test case"""

        # Read input content for debugging
        with open(input_file, 'r') as f:
            input_content = f.read().strip()

        # Read expected output
        with open(answer_file, 'r') as f:
            expected_output = f.read().strip()

        try:
            with open(input_file, 'rb') as stdin_file, \
                    tempfile.NamedTemporaryFile(mode='w+b') as stdout_file:

                start_time = time.time()

                # Run with time limit
                try:
                    result = subprocess.run(
                        [executable_path],
                        stdin=stdin_file,
                        stdout=stdout_file,
                        stderr=subprocess.PIPE,
                        timeout=self.time_limit_ms / 1000.0
                    )

                    runtime_ms = (time.time() - start_time) * 1000

                    if result.returncode != 0:
                        return SolutionResult(test_num, 'RTE', runtime_ms,
                                              details=f"Runtime error: {result.stderr.decode()[:200]}",
                                              input_content=input_content,
                                              expected_output=expected_output,
                                              actual_output="")

                    # Check output against expected answer
                    stdout_file.seek(0)
                    actual_output = stdout_file.read().decode().strip()

                    # Use problem's checker configuration
                    checker_type = self.problem.config.get(
                        'checker.type') or 'diff'

                    if checker_type == 'diff':
                        # Exact match
                        if actual_output == expected_output:
                            return SolutionResult(test_num, 'AC', runtime_ms,
                                                  input_content=input_content,
                                                  expected_output=expected_output,
                                                  actual_output=actual_output)
                        else:
                            return SolutionResult(test_num, 'WA', runtime_ms,
                                                  details=f"Output differs",
                                                  input_content=input_content,
                                                  expected_output=expected_output,
                                                  actual_output=actual_output)

                    elif checker_type == 'float':
                        # Floating point comparison
                        tolerance = self.problem.config.get(
                            'checker.float_tolerance') or 1e-6
                        if self._compare_float_output(expected_output, actual_output, tolerance):
                            return SolutionResult(test_num, 'AC', runtime_ms,
                                                  input_content=input_content,
                                                  expected_output=expected_output,
                                                  actual_output=actual_output)
                        else:
                            return SolutionResult(test_num, 'WA', runtime_ms,
                                                  details=f"Float comparison failed (tolerance={tolerance})",
                                                  input_content=input_content,
                                                  expected_output=expected_output,
                                                  actual_output=actual_output)

                    elif checker_type == 'spj':
                        # Special judge
                        spj_verdict, spj_details = self._run_special_judge(
                            input_file, stdout_file, answer_file)
                        return SolutionResult(test_num, spj_verdict, runtime_ms,
                                              details=spj_details,
                                              input_content=input_content,
                                              expected_output=expected_output,
                                              actual_output=actual_output)

                    else:
                        # Unknown checker type, default to diff
                        if actual_output == expected_output:
                            return SolutionResult(test_num, 'AC', runtime_ms,
                                                  input_content=input_content,
                                                  expected_output=expected_output,
                                                  actual_output=actual_output)
                        else:
                            return SolutionResult(test_num, 'WA', runtime_ms,
                                                  details="Unknown checker type, used diff",
                                                  input_content=input_content,
                                                  expected_output=expected_output,
                                                  actual_output=actual_output)

                except subprocess.TimeoutExpired:
                    return SolutionResult(test_num, 'TLE', self.time_limit_ms,
                                          input_content=input_content,
                                          expected_output=expected_output,
                                          actual_output="")

        except Exception as e:
            return SolutionResult(test_num, 'JE', 0, details=f"Judge error: {str(e)}",
                                  input_content=input_content,
                                  expected_output=expected_output,
                                  actual_output="")

    def _summarize_category_results(self, results: List[SolutionResult]) -> Dict[str, Any]:
        """Summarize results for a category"""
        if not results:
            return {'count': 0, 'passed': 0, 'failed': 0, 'avg_time_ms': 0}

        passed = sum(1 for r in results if r.verdict == 'AC')
        failed = len(results) - passed
        avg_time = sum(r.time_ms for r in results) / len(results)

        return {
            'count': len(results),
            'passed': passed,
            'failed': failed,
            'avg_time_ms': round(avg_time, 2),
            'pass_rate': round(passed / len(results) * 100, 1) if results else 0
        }

    def _calculate_statistics(self, test_results: Dict[str, List]) -> Dict[str, Any]:
        """Calculate overall statistics"""
        total_tests = 0
        total_passed = 0
        total_time = 0

        for category_results in test_results.values():
            for result in category_results:
                total_tests += 1
                verdict = result['verdict'] if isinstance(
                    result, dict) else result.verdict
                time_ms = result['time_ms'] if isinstance(
                    result, dict) else result.time_ms

                if verdict == 'AC':
                    total_passed += 1
                total_time += time_ms

        return {
            'total_tests': total_tests,
            'passed': total_passed,
            'failed': total_tests - total_passed,
            'total_time_ms': round(total_time, 2),
            'pass_rate': round(total_passed / max(1, total_tests) * 100, 1)
        }

    def _determine_overall_verdict(self, test_results: Dict[str, List]) -> str:
        """Determine overall verdict based on all test results"""
        # Check for compilation errors (should be handled earlier)

        # Check samples first
        if 'samples' in test_results:
            sample_results = test_results['samples']
            for result in sample_results:
                verdict = result['verdict'] if isinstance(
                    result, dict) else result.verdict
                test_num = result['test_num'] if isinstance(
                    result, dict) else result.test_num
                if verdict != 'AC':
                    return f"WA on sample {test_num}"

        # Check pretests
        if 'pretests' in test_results:
            pretest_results = test_results['pretests']
            for result in pretest_results:
                verdict = result['verdict'] if isinstance(
                    result, dict) else result.verdict
                test_num = result['test_num'] if isinstance(
                    result, dict) else result.test_num
                if verdict != 'AC':
                    return f"WA on pretest {test_num}"

        # Check system tests
        if 'system' in test_results:
            system_results = test_results['system']
            for result in system_results:
                verdict = result['verdict'] if isinstance(
                    result, dict) else result.verdict
                test_num = result['test_num'] if isinstance(
                    result, dict) else result.test_num
                if verdict != 'AC':
                    return f"WA on test {test_num}"

        return "AC"

    def quick_test(self, cpp_code: str, test_input: str) -> Tuple[bool, str, str]:
        """
        Quickly test a solution against a single input
        Returns (success, output, error_message)
        """
        try:
            # Compile
            compile_result = self._compile_solution(cpp_code)
            if not compile_result['success']:
                return False, "", f"Compilation Error: {compile_result['errors']}"

            executable_path = compile_result['executable_path']

            try:
                # Run
                result = subprocess.run(
                    [executable_path],
                    input=test_input,
                    capture_output=True,
                    text=True,
                    timeout=self.time_limit_ms / 1000.0
                )

                if result.returncode == 0:
                    return True, result.stdout.strip(), ""
                else:
                    return False, "", f"Runtime Error: {result.stderr}"

            finally:
                if os.path.exists(executable_path):
                    os.remove(executable_path)

        except subprocess.TimeoutExpired:
            return False, "", "Time Limit Exceeded"
        except Exception as e:
            return False, "", f"Error: {str(e)}"

    def _compare_float_output(self, expected: str, actual: str, tolerance: float) -> bool:
        """Compare floating point outputs with tolerance"""
        try:
            expected_nums = [float(x) for x in expected.split()]
            actual_nums = [float(x) for x in actual.split()]

            if len(expected_nums) != len(actual_nums):
                return False

            for exp, act in zip(expected_nums, actual_nums):
                if abs(exp - act) > tolerance:
                    return False

            return True
        except:
            return False

    def _run_special_judge(self, input_file: Path, output_file, answer_file: Path) -> Tuple[str, str]:
        """Compile and run special judge, return (verdict, details)"""
        try:
            # Check if SPJ source exists
            spj_source = self.problem_dir / 'checker' / 'spj.cpp'
            if not spj_source.exists():
                return 'JE', 'Judge Error: SPJ source file (checker/spj.cpp) not found'

            # Step 1: Compile SPJ fresh every time
            spj_executable, compile_error = self._compile_spj(spj_source)
            if not spj_executable:
                return 'JE', f'Judge Error: SPJ compilation failed - {compile_error}'

            # Create temporary output file path for SPJ
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_out:
                output_file.seek(0)
                tmp_out.write(output_file.read().decode())
                tmp_out_path = tmp_out.name

            try:
                # Step 2: Run freshly compiled SPJ
                result = subprocess.run(
                    [str(spj_executable), str(input_file),
                     tmp_out_path, str(answer_file)],
                    capture_output=True,
                    text=True,  # Decode output as text
                    timeout=5
                )

                # Extract SPJ message from stderr (quitf messages)
                spj_message = result.stderr.strip()
                if not spj_message and result.stdout.strip():
                    spj_message = result.stdout.strip()

                # SPJ return codes: 0=AC, 1=WA, 2=PE, others=JE
                if result.returncode == 0:
                    return 'AC', spj_message or 'Answer accepted by special judge'
                elif result.returncode == 1:
                    return 'WA', spj_message or 'Wrong answer (no details from SPJ)'
                elif result.returncode == 2:
                    return 'PE', spj_message or 'Presentation error (no details from SPJ)'
                else:
                    return 'JE', spj_message or f'Judge error: SPJ returned code {result.returncode}'

            finally:
                # Clean up temporary files
                os.unlink(tmp_out_path)
                # Clean up compiled SPJ
                if spj_executable.exists():
                    os.unlink(spj_executable)

        except subprocess.TimeoutExpired:
            return 'JE', 'Judge Error: SPJ timeout (>5s)'
        except Exception as e:
            return 'JE', f'Judge Error: {str(e)}'

    def _compile_spj(self, spj_source: Path) -> Tuple[Optional[Path], str]:
        """Compile SPJ and return (executable_path, error_message)"""
        try:
            checker_dir = spj_source.parent

            # Ensure testlib.h exists
            testlib_path = checker_dir / 'testlib.h'
            if not testlib_path.exists():
                self._ensure_testlib_for_spj(checker_dir)

            # Use a simple executable name in the same directory as the source
            spj_executable = checker_dir / 'spj_temp'

            # Compile SPJ with testlib - use relative paths from checker directory
            compile_cmd = [
                'g++', '-std=c++17', '-O2',
                spj_source.name,  # Just the filename (e.g., 'spj.cpp')
                '-o', spj_executable.name  # Just the executable name
            ]

            result = subprocess.run(
                compile_cmd,
                cwd=str(checker_dir.resolve()),  # Run from checker directory
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return spj_executable, ""
            else:
                # Clean up failed executable
                if spj_executable.exists():
                    os.unlink(spj_executable)
                return None, result.stderr or "Unknown compilation error"

        except subprocess.TimeoutExpired:
            return None, "SPJ compilation timeout (>30s)"
        except Exception as e:
            return None, f"SPJ compilation error: {str(e)}"

    def _ensure_testlib_for_spj(self, checker_dir: Path):
        """Ensure testlib.h exists in checker directory for SPJ compilation"""
        testlib_path = checker_dir / 'testlib.h'

        # Try to copy from another problem first
        problems_dir = self.problem_dir.parent
        for other_problem in problems_dir.iterdir():
            if other_problem.is_dir() and other_problem != self.problem_dir:
                other_testlib = other_problem / 'checker' / 'testlib.h'
                if other_testlib.exists():
                    import shutil
                    shutil.copy2(other_testlib, testlib_path)
                    return

        # If no testlib.h found, create a minimal placeholder
        # This shouldn't happen in a properly set up system, but provides fallback
        placeholder_content = '''// Placeholder testlib.h - replace with actual testlib.h
#ifndef _TESTLIB_H_
#define _TESTLIB_H_
#include <iostream>
#include <string>
#include <cstdlib>
using namespace std;

// Minimal testlib placeholders
#define _ok 0
#define _wa 1
#define _pe 2

void quitf(int exitCode, const char* format, ...) {
    // This is a minimal placeholder - use real testlib.h for full functionality
    if (exitCode == _ok) {
        fprintf(stderr, "ok");
    } else if (exitCode == _wa) {
        fprintf(stderr, "wrong answer");
    } else if (exitCode == _pe) {
        fprintf(stderr, "presentation error");
    }
    exit(exitCode);
}
#endif
'''

        with open(testlib_path, 'w') as f:
            f.write(placeholder_content)
