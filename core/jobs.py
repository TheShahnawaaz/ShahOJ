"""Auto-build workflow helpers for PocketOJ."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, Optional

from core.ai_service import get_ai_service
from core.file_manager import FileManager
from core.test_generator import TestGenerator
from core.config import config


def run_auto_build_workflow(
    slug: str,
    raw_options: Optional[Dict[str, Any]] = None,
    *,
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
) -> Dict[str, Any]:
    """Execute the auto-build workflow synchronously and return a summary."""

    # Import lazily to avoid circular references during module import.
    from app import unified_problem_manager  # type: ignore

    default_options = {
        'polish_statement': True,
        'generate_solution': True,
        'generate_generator': True,
        'generate_validator': False,
        'generate_spj': False,
        'generate_tests': True,
        'sample_case_count': 3,
        'system_case_count': 10,
        'solution_timeout_ms': config.get('system.default_time_limit_ms', 1000),
    }
    options = {**default_options, **(raw_options or {})}

    problem = unified_problem_manager.get_problem(slug)
    if not problem:
        raise ValueError(f'Problem {slug} not found')

    problem_dir = Path(problem.problem_dir)
    file_manager = FileManager(problem_dir)

    ai_service = get_ai_service()
    if not ai_service:
        raise RuntimeError('AI service not configured (missing OPENAI_API_KEY)')

    planned_steps: list[str] = []
    if options['polish_statement']:
        planned_steps.append('Polish statement')
    if options['generate_solution']:
        planned_steps.append('Generate reference solution')
    if options['generate_generator']:
        planned_steps.append('Generate test generator')
    if options['generate_validator']:
        planned_steps.append('Generate input validator')
    if options['generate_spj']:
        planned_steps.append('Generate special judge')
    if options['generate_tests']:
        planned_steps.append('Generate test cases')

    total_steps = len(planned_steps)
    current_step = 0

    summary_steps: list[Dict[str, Any]] = []
    summary: Dict[str, Any] = {
        'slug': slug,
        'options': options,
        'steps': summary_steps,
        'status': 'pending',
    }

    def emit_progress(message: str) -> None:
        if progress_callback:
            progress_callback(current_step, max(total_steps, 1), message)

    def clean_code(text: str) -> str:
        stripped = text.strip()
        if stripped.startswith('```'):
            stripped = stripped.split('\n', 1)[1] if '\n' in stripped else ''
        if stripped.endswith('```'):
            stripped = stripped.rsplit('\n', 1)[0]
        return stripped.strip() + '\n'

    def run_step(name: str, func: Callable[[], Optional[Dict[str, Any]]]) -> None:
        nonlocal current_step
        current_step += 1
        emit_progress(name)
        try:
            details = func() or {}
        except Exception as exc:
            summary_steps.append({'name': name, 'status': 'failed', 'error': str(exc)})
            summary['status'] = 'failed'
            summary['error'] = str(exc)
            raise
        else:
            summary_steps.append({'name': name, 'status': 'completed', 'details': details})

    statement_path = problem_dir / 'statement.md'
    if not statement_path.exists():
        raise RuntimeError('statement.md does not exist')
    original_statement = statement_path.read_text().strip()
    if not original_statement:
        raise RuntimeError('statement.md is empty')

    if options['polish_statement']:

        def step_polish() -> Dict[str, Any]:
            result = ai_service.polish_statement_with_explanation(original_statement)
            polished = result.code.strip() + '\n'
            file_manager.save_file('statement.md', polished)
            return {
                'explanation': result.explanation,
                'characters': len(polished),
            }

        run_step('Polish statement', step_polish)
        original_statement = (problem_dir / 'statement.md').read_text().strip()

    if options['generate_solution']:

        def step_generate_solution() -> Dict[str, Any]:
            result = ai_service.generate_solution_with_explanation(original_statement)
            solution_code = clean_code(result.code)
            file_manager.save_file('solution.py', solution_code)
            return {
                'lines': len(solution_code.splitlines()),
                'explanation': result.explanation,
            }

        run_step('Generate reference solution', step_generate_solution)

    if options['generate_generator']:

        def step_generate_generator() -> Dict[str, Any]:
            result = ai_service.generate_generator_with_explanation(original_statement)
            generator_code = clean_code(result.code)
            file_manager.save_file('generator.py', generator_code)
            return {
                'lines': len(generator_code.splitlines()),
                'explanation': result.explanation,
            }

        run_step('Generate test generator', step_generate_generator)

    if options['generate_validator']:

        def step_generate_validator() -> Dict[str, Any]:
            result = ai_service.generate_validator_with_explanation(original_statement)
            validator_code = clean_code(result.code)
            file_manager.save_file('validator.py', validator_code)
            return {
                'lines': len(validator_code.splitlines()),
                'explanation': result.explanation,
            }

        run_step('Generate input validator', step_generate_validator)

    if options['generate_spj']:

        def step_generate_spj() -> Dict[str, Any]:
            result = ai_service.generate_special_judge_with_explanation(original_statement)
            spj_code = clean_code(result.code)
            file_manager.save_file('checker/spj.cpp', spj_code)
            return {
                'lines': len(spj_code.splitlines()),
                'explanation': result.explanation,
            }

        run_step('Generate special judge', step_generate_spj)

    tests_summary: Dict[str, Any] = {}
    if options['generate_tests']:

        def step_generate_tests() -> Dict[str, Any]:
            refreshed_problem = unified_problem_manager.get_problem(slug)
            if not refreshed_problem:
                raise RuntimeError('Problem disappeared during processing')

            test_gen = TestGenerator(refreshed_problem)
            samples = options.get('sample_case_count', 3) or 0
            systems = options.get('system_case_count', 10) or 0

            saved_samples = 0
            saved_system = 0

            if samples > 0:
                sample_cases = test_gen.generate_cases(samples)
                saved_samples = test_gen.save_test_cases(
                    sample_cases,
                    test_category='samples',
                    replace_existing=True,
                )

            if systems > 0:
                system_cases = test_gen.generate_cases(systems)
                saved_system = test_gen.save_test_cases(
                    system_cases,
                    test_category='system',
                    replace_existing=True,
                )

            tests_summary.update({
                'samples': saved_samples,
                'system': saved_system,
            })
            return tests_summary

        run_step('Generate test cases', step_generate_tests)

    def step_update_metadata() -> Dict[str, Any]:
        unified_problem_manager.update_file_status(slug)
        refreshed = unified_problem_manager.get_problem(slug)
        return {'test_counts': refreshed.get_test_cases_count() if refreshed else {}}

    try:
        step_update_metadata()
    except Exception as exc:
        summary['status'] = 'failed'
        summary['error'] = str(exc)
        raise

    if tests_summary:
        summary['tests'] = tests_summary
    summary['status'] = 'succeeded'

    return summary
