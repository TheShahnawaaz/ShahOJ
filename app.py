"""
Flask web application for PocketOJ extensible judge system
"""

from core.config import config
from core.problem_manager import ProblemManager
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
import os
import sys
import traceback

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# Initialize Flask app
app = Flask(__name__)
app.secret_key = config.get('web.secret_key', os.urandom(24).hex())

# Initialize problem manager
problem_manager = ProblemManager()


@app.route('/')
def dashboard():
    """Main dashboard showing all problems"""
    try:
        problems = problem_manager.list_problems()
        stats = problem_manager.get_statistics()
        return render_template('dashboard.html', problems=problems, stats=stats)
    except Exception as e:
        return f"Error loading dashboard: {e}", 500


@app.route('/api/problems')
def api_problems():
    """API endpoint to get all problems as JSON"""
    try:
        problems = problem_manager.list_problems()
        problems_data = []

        for problem in problems:
            problems_data.append({
                'slug': problem.slug,
                'title': problem.config.get('title', problem.slug),
                'difficulty': problem.config.get('difficulty', 'Medium'),
                'tags': problem.config.get('tags', []),
                'test_cases': problem.get_test_cases_count(),
                'created_date': problem.config.get('created_date', ''),
                'files_info': problem.get_files_info()
            })

        stats = problem_manager.get_statistics()
        return jsonify({
            'success': True,
            'problems': problems_data,
            'stats': {
                'total_problems': stats['total_problems'],
                'total_test_cases': stats['total_test_cases'],
                'difficulty_breakdown': stats['difficulty_breakdown']
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/problem/<slug>')
def problem_detail(slug):
    """Show detailed view of a specific problem"""
    try:
        problem = problem_manager.get_problem(slug)
        if not problem:
            return "Problem not found", 404

        return render_template('problem_detail.html', problem=problem)
    except Exception as e:
        return f"Error loading problem: {e}", 500


@app.route('/api/problem/<slug>')
def api_problem_detail(slug):
    """API endpoint to get problem details as JSON"""
    try:
        problem = problem_manager.get_problem(slug)
        if not problem:
            return jsonify({'success': False, 'error': 'Problem not found'}), 404

        return jsonify({
            'success': True,
            'problem': {
                'slug': problem.slug,
                'config': problem.config,
                'files_info': problem.get_files_info(),
                'test_cases': problem.get_test_cases_count()
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/create-problem')
def create_problem_form():
    """Show create problem form (new file-centric version)"""
    return render_template('create_problem_v2.html')


@app.route('/create-problem-legacy')
def create_problem_form_legacy():
    """Show legacy create problem form"""
    return render_template('create_problem.html')


@app.route('/create-problem', methods=['POST'])
def create_problem():
    """Handle problem creation"""
    try:
        # Extract form data (handle both form and JSON requests)
        if request.is_json:
            json_data = request.get_json()
            form_data = {
                'title': json_data.get('title', '').strip(),
                'slug': json_data.get('slug', '').strip(),
                'difficulty': json_data.get('difficulty', 'Medium'),
                'tags': [tag.strip() for tag in json_data.get('tags', '').split(',') if tag.strip()],
                'description': json_data.get('description', '').strip(),
                'time_limit_ms': int(json_data.get('time_limit', 1000)),
                'memory_limit_mb': int(json_data.get('memory_limit', 256)),
                'template': json_data.get('template', 'basic'),
                'solution_code': json_data.get('solution_code', '').strip(),
                'checker_type': json_data.get('checker_type', 'diff'),
                'n_min': int(json_data.get('n_min', 1)),
                'n_max': int(json_data.get('n_max', 100000)),
                'val_min': int(json_data.get('val_min', -1000000000)),
                'val_max': int(json_data.get('val_max', 1000000000)),
                'small_tests': int(json_data.get('small_tests', 3)),
                'medium_tests': int(json_data.get('medium_tests', 5)),
                'large_tests': int(json_data.get('large_tests', 7))
            }
        else:
            form_data = {
                'title': request.form.get('title', '').strip(),
                'slug': request.form.get('slug', '').strip(),
                'difficulty': request.form.get('difficulty', 'Medium'),
                'tags': [tag.strip() for tag in request.form.get('tags', '').split(',') if tag.strip()],
                'description': request.form.get('description', '').strip(),
                'time_limit_ms': int(request.form.get('time_limit', 1000)),
                'memory_limit_mb': int(request.form.get('memory_limit', 256)),
                'template': request.form.get('template', 'basic'),
                'solution_code': request.form.get('solution_code', '').strip(),
                'checker_type': request.form.get('checker_type', 'diff'),
                'n_min': int(request.form.get('n_min', 1)),
                'n_max': int(request.form.get('n_max', 100000)),
                'val_min': int(request.form.get('val_min', -1000000000)),
                'val_max': int(request.form.get('val_max', 1000000000)),
                'small_tests': int(request.form.get('small_tests', 3)),
                'medium_tests': int(request.form.get('medium_tests', 5)),
                'large_tests': int(request.form.get('large_tests', 7))
            }

        # Validate required fields
        if not form_data['title'] or not form_data['slug'] or not form_data['solution_code']:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: title, slug, or solution code'
            }), 400

        # Check if problem already exists
        if problem_manager.problem_exists(form_data['slug']):
            return jsonify({
                'success': False,
                'error': f"Problem with slug '{form_data['slug']}' already exists"
            }), 400

        # Create problem configuration
        config_data = {
            'title': form_data['title'],
            'slug': form_data['slug'],
            'difficulty': form_data['difficulty'],
            'tags': form_data['tags'],
            'description': form_data['description'],
            'author': request.remote_addr or 'web-user',

            # Constraints
            'time_limit_ms': form_data['time_limit_ms'],
            'memory_limit_mb': form_data['memory_limit_mb'],

            # Input constraints
            'constraints': {
                'n': [form_data['n_min'], form_data['n_max']],
                'values': [form_data['val_min'], form_data['val_max']]
            },

            # Checker configuration
            'checker': {
                'type': form_data['checker_type']
            },

            # Test case counts
            'tests': {
                'sample_count': 3,
                'system_count': form_data['small_tests'] + form_data['medium_tests'] + form_data['large_tests']
            },

            # Validation settings
            'validation': {
                'enabled': True,
                'strict_mode': True
            }
        }

        # Create the problem
        problem = problem_manager.create_problem_structure(
            form_data['slug'], config_data)

        # Save reference solution
        solution_file = problem.problem_dir / 'solution.py'
        with open(solution_file, 'w') as f:
            f.write(form_data['solution_code'])

        # Create basic generator and validator from template
        try:
            from problem_templates.template_manager import TemplateManager
            template_manager = TemplateManager()
            template_manager.apply_template(problem, form_data['template'])
        except ImportError:
            # Fallback: create basic files manually
            print("Warning: Template manager not available, creating basic files")

        return jsonify({
            'success': True,
            'problem_slug': form_data['slug'],
            'message': 'Problem created successfully!',
            'redirect_url': url_for('problem_detail', slug=form_data['slug'])
        })

    except Exception as e:
        print(f"Error creating problem: {e}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Error creating problem: {str(e)}'
        }), 500


@app.route('/problem/<slug>/tests')
def manage_test_cases(slug):
    """Test case management page"""
    try:
        problem = problem_manager.get_problem(slug)
        if not problem:
            return "Problem not found", 404

        # Get test case statistics
        from core.test_generator import TestGenerator
        test_generator = TestGenerator(problem)
        stats = test_generator.get_test_case_statistics()

        return render_template('manage_tests.html', problem=problem, stats=stats)
    except Exception as e:
        return f"Error loading test management: {e}", 500


@app.route('/problem/<slug>/test-solution')
def test_solution_page(slug):
    """Solution testing page"""
    try:
        problem = problem_manager.get_problem(slug)
        if not problem:
            return "Problem not found", 404

        return render_template('test_solution.html', problem=problem)
    except Exception as e:
        return f"Error loading solution tester: {e}", 500


@app.route('/api/problem/<slug>/delete', methods=['DELETE'])
def delete_problem_api(slug):
    """API endpoint to delete a problem"""
    try:
        success = problem_manager.delete_problem(slug)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Problem not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/problem/<slug>/generate-tests', methods=['POST'])
def generate_tests_api(slug):
    """API endpoint to generate test cases"""
    try:
        problem = problem_manager.get_problem(slug)
        if not problem:
            return jsonify({'success': False, 'error': 'Problem not found'}), 404

        # Get generation parameters
        data = request.get_json() or {}
        test_category = data.get('category', 'system')
        count = int(data.get('count', problem.config.get('tests.system_count', 20)))
        replace_existing = data.get('replace_existing', False)
        
        print(f"Generating {count} test cases for {test_category} category")

        # Generate test cases
        from core.test_generator import TestGenerator
        test_generator = TestGenerator(problem)
        generated_cases = test_generator.generate_cases(count)

        # Save test cases (append by default, replace only if explicitly requested)
        saved_count = test_generator.save_test_cases(
            generated_cases, test_category, replace_existing)

        action = "Replaced" if replace_existing else "Added"

        # Get updated statistics
        stats = test_generator.get_test_case_statistics()

        return jsonify({
            'success': True,
            'generated_count': saved_count,
            'message': f'{action} {saved_count} test cases in {test_category}',
            'stats': stats,
            'replaced': replace_existing
        })

    except Exception as e:
        print(f"Error generating tests: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error generating tests: {str(e)}'
        }), 500


@app.route('/api/problem/<slug>/add-manual-test', methods=['POST'])
def add_manual_test_api(slug):
    """API endpoint to add manual test case"""
    try:
        problem = problem_manager.get_problem(slug)
        if not problem:
            return jsonify({'success': False, 'error': 'Problem not found'}), 404

        data = request.get_json()
        input_text = data.get('input', '').strip()
        test_category = data.get('category', 'samples')

        if not input_text:
            return jsonify({'success': False, 'error': 'Input text is required'}), 400

        # Add the test case
        from core.test_generator import TestGenerator
        test_generator = TestGenerator(problem)
        success = test_generator.add_manual_test_case(
            input_text, test_category)

        if success:
            # Get updated statistics
            stats = test_generator.get_test_case_statistics()

            return jsonify({
                'success': True,
                'message': f'Manual test case added to {test_category}',
                'stats': stats
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to add manual test case'
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error adding manual test: {str(e)}'
        }), 500


@app.route('/api/problem/<slug>/test-solution', methods=['POST'])
def test_solution_api(slug):
    """API endpoint to test a C++ solution"""
    try:
        problem = problem_manager.get_problem(slug)
        if not problem:
            return jsonify({'success': False, 'error': 'Problem not found'}), 404

        data = request.get_json()
        cpp_code = data.get('code', '').strip()
        test_categories = data.get(
            'categories', ['samples', 'pretests', 'system'])

        if not cpp_code:
            return jsonify({'success': False, 'error': 'C++ code is required'}), 400

        # Test the solution
        from core.solution_tester import SolutionTester
        tester = SolutionTester(problem)
        results = tester.test_solution(cpp_code, test_categories)

        return jsonify({
            'success': True,
            'results': results
        })

    except Exception as e:
        print(f"Error testing solution: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error testing solution: {str(e)}'
        }), 500


@app.route('/api/problem/<slug>/quick-test', methods=['POST'])
def quick_test_api(slug):
    """API endpoint for quick testing against custom input"""
    try:
        problem = problem_manager.get_problem(slug)
        if not problem:
            return jsonify({'success': False, 'error': 'Problem not found'}), 404

        data = request.get_json()
        cpp_code = data.get('code', '').strip()
        test_input = data.get('input', '').strip()

        if not cpp_code or not test_input:
            return jsonify({'success': False, 'error': 'Both code and input are required'}), 400

        # Quick test
        from core.solution_tester import SolutionTester
        tester = SolutionTester(problem)
        success, output, error = tester.quick_test(cpp_code, test_input)

        return jsonify({
            'success': success,
            'output': output,
            'error': error
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error in quick test: {str(e)}'
        }), 500


@app.route('/api/test-file-integration', methods=['POST'])
def test_file_integration_api():
    """API endpoint to test file integration before problem creation"""
    try:
        data = request.get_json()
        files = data.get('files', {})

        if not files:
            return jsonify({'success': False, 'error': 'No files provided'}), 400

        # Test file integration
        from core.file_manager import FileManager

        # Use temporary directory for testing
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            file_manager = FileManager(temp_dir)
            integration_results = file_manager.test_file_integration(files)

        return jsonify(integration_results)

    except Exception as e:
        print(f"Error testing file integration: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error testing files: {str(e)}'
        }), 500


@app.route('/api/create-problem-v2', methods=['POST'])
def create_problem_v2_api():
    """API endpoint for new file-centric problem creation"""
    try:
        data = request.get_json()

        # Extract metadata
        metadata = {
            'title': data.get('title', '').strip(),
            'slug': data.get('slug', '').strip(),
            'difficulty': data.get('difficulty', 'Medium'),
            'tags': [tag.strip() for tag in data.get('tags', '').split(',') if tag.strip()],
            'description': data.get('description', '').strip(),
            'time_limit_ms': int(data.get('time_limit', 1000)),
            'memory_limit_mb': int(data.get('memory_limit', 256)),
            'checker_type': data.get('checker_type', 'diff'),
            'sample_count': int(data.get('sample_count', 3)),
            'system_count': int(data.get('system_count', 20))
        }

        files = data.get('files', {})

        # Validate required fields
        if not metadata['title'] or not metadata['slug']:
            return jsonify({'success': False, 'error': 'Title and slug are required'}), 400

        required_files = ['statement.md', 'solution.py', 'generator.py']
        missing_files = [
            f for f in required_files if f not in files or not files[f].strip()]

        if missing_files:
            return jsonify({'success': False, 'error': f'Missing required files: {", ".join(missing_files)}'}), 400

        # Check if problem already exists
        if problem_manager.problem_exists(metadata['slug']):
            # Offer to overwrite or suggest different slug
            return jsonify({
                'success': False,
                'error': f"Problem '{metadata['slug']}' already exists",
                'suggestion': f"Try: {metadata['slug']}-v2 or delete existing problem first",
                'existing_problem_url': url_for('problem_detail', slug=metadata['slug'])
            }), 400

        # Create problem structure
        problem = problem_manager.create_problem_structure(
            metadata['slug'], metadata)

        # Save all files
        from core.file_manager import FileManager
        file_manager = FileManager(problem.problem_dir)

        for filename, content in files.items():
            if not file_manager.save_file(filename, content):
                return jsonify({'success': False, 'error': f'Failed to save {filename}'}), 500

        # Update config with file status
        problem.config.update_file_status(problem.problem_dir)
        problem.save_config(problem.config)

        # Generate initial test cases
        try:
            from core.test_generator import TestGenerator
            test_gen = TestGenerator(problem)

            # Generate system test cases using the provided generator
            generated_cases = test_gen.generate_cases(metadata['system_count'])
            saved_count = test_gen.save_test_cases(
                generated_cases, 'system', replace_existing=True)

        except Exception as e:
            print(f"Warning: Initial test generation failed: {e}")
            # Don't fail problem creation if test generation fails
            saved_count = 0

        return jsonify({
            'success': True,
            'problem_slug': metadata['slug'],
            'message': f'Problem created with {saved_count} initial test cases!',
            'redirect_url': url_for('problem_detail', slug=metadata['slug'])
        })

    except Exception as e:
        print(f"Error creating problem v2: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error creating problem: {str(e)}'
        }), 500


@app.route('/api/problem/<slug>/validate-input', methods=['POST'])
def validate_input_api(slug):
    """API endpoint to validate test case input"""
    try:
        problem = problem_manager.get_problem(slug)
        if not problem:
            return jsonify({'success': False, 'error': 'Problem not found'}), 404

        data = request.get_json()
        input_text = data.get('input', '').strip()

        if not input_text:
            return jsonify({'success': False, 'error': 'Input text is required'}), 400

        # Validate using problem's validator
        from core.test_generator import TestGenerator
        test_gen = TestGenerator(problem)
        is_valid = test_gen._validate_input(input_text)

        return jsonify({
            'success': True,
            'valid': is_valid,
            'message': 'Input is valid' if is_valid else 'Input validation failed'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error validating input: {str(e)}'
        }), 500


@app.route('/api/problem/<slug>/test-cases/<category>')
def get_test_cases_api(slug, category):
    """API endpoint to get test cases for a category"""
    try:
        problem = problem_manager.get_problem(slug)
        if not problem:
            return jsonify({'success': False, 'error': 'Problem not found'}), 404

        if category not in ['samples', 'pretests', 'system']:
            return jsonify({'success': False, 'error': 'Invalid category'}), 400

        # Get test case files
        test_dir = problem.problem_dir / 'tests' / category
        test_cases = []

        if test_dir.exists():
            in_files = sorted(test_dir.glob('*.in'), key=lambda x: x.name)

            for in_file in in_files:
                ans_file = test_dir / (in_file.stem + '.ans')

                # Read files (limit size for web display)
                with open(in_file, 'r') as f:
                    input_content = f.read()
                    if len(input_content) > 1000:
                        input_preview = input_content[:1000] + \
                            '... (truncated)'
                    else:
                        input_preview = input_content

                answer_content = ''
                if ans_file.exists():
                    with open(ans_file, 'r') as f:
                        answer_content = f.read().strip()

                test_cases.append({
                    'test_num': int(in_file.stem) if in_file.stem.isdigit() else 0,
                    'filename': in_file.stem,
                    'input_preview': input_preview,
                    'answer': answer_content,
                    'input_size': len(input_content),
                    'answer_size': len(answer_content)
                })

        return jsonify({
            'success': True,
            'category': category,
            'test_cases': test_cases,
            'count': len(test_cases)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error loading test cases: {str(e)}'
        }), 500


@app.route('/problem/<slug>/edit')
def edit_problem_page(slug):
    """Problem editing page"""
    try:
        problem = problem_manager.get_problem(slug)
        if not problem:
            return "Problem not found", 404

        # Load file contents for editing
        file_contents = {}
        files_to_load = ['statement.md', 'solution.py',
                         'generator.py', 'validator.py', 'checker/spj.cpp']

        from core.file_manager import FileManager
        file_manager = FileManager(problem.problem_dir)

        for filename in files_to_load:
            content = file_manager.load_file(filename)
            file_contents[filename.replace(
                '/', '_').replace('.', '_')] = content or ''

        return render_template('edit_problem.html',
                               problem=problem,
                               statement_content=file_contents.get(
                                   'statement_md', ''),
                               solution_content=file_contents.get(
                                   'solution_py', ''),
                               generator_content=file_contents.get(
                                   'generator_py', ''),
                               validator_content=file_contents.get(
                                   'validator_py', ''),
                               checker_content=file_contents.get('checker_spj_cpp', ''))

    except Exception as e:
        return f"Error loading problem editor: {e}", 500


@app.route('/api/problem/<slug>/save-all', methods=['POST'])
def save_problem_all_api(slug):
    """API endpoint to save all problem changes"""
    try:
        problem = problem_manager.get_problem(slug)
        if not problem:
            return jsonify({'success': False, 'error': 'Problem not found'}), 404

        data = request.get_json()
        config_data = data.get('config', {})
        files_data = data.get('files', {})

        # Update configuration
        for key, value in config_data.items():
            if key == 'tags':
                problem.config.set('tags', value)
            elif key == 'time_limit_ms':
                problem.config.set('limits.time_ms', value)
            elif key == 'memory_limit_mb':
                problem.config.set('limits.memory_mb', value)
            elif key == 'checker_type':
                problem.config.set('checker.type', value)
            else:
                problem.config.set(key, value)

        # Save files
        from core.file_manager import FileManager
        file_manager = FileManager(problem.problem_dir)

        saved_files = []
        for filename, content in files_data.items():
            if content.strip():  # Only save non-empty files
                if file_manager.save_file(filename, content):
                    saved_files.append(filename)
                else:
                    return jsonify({'success': False, 'error': f'Failed to save {filename}'}), 500

        # Update config with new file status
        problem.config.update_file_status(problem.problem_dir)
        problem.save_config(problem.config)

        return jsonify({
            'success': True,
            'message': f'Saved {len(saved_files)} files and configuration',
            'saved_files': saved_files
        })

    except Exception as e:
        print(f"Error saving problem: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error saving problem: {str(e)}'
        }), 500


@app.route('/api/validate-file', methods=['POST'])
def validate_file_api():
    """API endpoint to validate a single file"""
    try:
        data = request.get_json()
        filename = data.get('filename', '')
        content = data.get('content', '')

        from core.file_manager import FileManager
        import tempfile

        # Use temporary directory for validation
        with tempfile.TemporaryDirectory() as temp_dir:
            file_manager = FileManager(temp_dir)

            if filename.endswith('.py'):
                valid, message = file_manager.validate_python_syntax(content)
            elif filename.endswith('.cpp'):
                valid, message = file_manager.validate_cpp_syntax(content)
            else:
                # For other files (like .md), just check they're not empty
                valid = bool(content.strip())
                message = "Valid" if valid else "File is empty"

        return jsonify({
            'success': True,
            'valid': valid,
            'error': message if not valid else None
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Validation error: {str(e)}'
        }), 500


@app.route('/api/problem/<slug>/compile-spj', methods=['POST'])
def compile_spj_api(slug):
    """API endpoint to compile Special Judge"""
    try:
        problem = problem_manager.get_problem(slug)
        if not problem:
            return jsonify({'success': False, 'error': 'Problem not found'}), 404

        data = request.get_json()
        spj_content = data.get('content', '').strip()

        if not spj_content:
            return jsonify({'success': False, 'error': 'SPJ code is required'}), 400

        # Test compilation first
        from core.file_manager import FileManager
        file_manager = FileManager(problem.problem_dir)

        # Test compilation
        test_ok, test_msg = file_manager.test_spj_compilation(spj_content)
        if not test_ok:
            return jsonify({
                'success': False,
                'error': f'SPJ compilation test failed: {test_msg}'
            }), 400

        # Actual compilation and save
        compile_ok, compile_msg = file_manager.compile_spj(spj_content, slug)
        if compile_ok:
            # Update problem config to use SPJ
            problem.config.set('checker.type', 'spj')
            problem.config.set('checker.spj_path', 'checker/spj')
            problem.config.set('files.has_custom_checker', True)
            problem.save_config(problem.config)

            return jsonify({
                'success': True,
                'message': 'SPJ compiled and configured successfully',
                'details': compile_msg
            })
        else:
            return jsonify({
                'success': False,
                'error': compile_msg
            }), 500

    except Exception as e:
        print(f"Error compiling SPJ: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'SPJ compilation error: {str(e)}'
        }), 500


@app.route('/api/problem/<slug>/statement')
def get_problem_statement_api(slug):
    """API endpoint to get problem statement"""
    try:
        problem = problem_manager.get_problem(slug)
        if not problem:
            return jsonify({'success': False, 'error': 'Problem not found'}), 404

        statement_file = problem.problem_dir / 'statement.md'

        if statement_file.exists():
            with open(statement_file, 'r') as f:
                statement_content = f.read()

            return jsonify({
                'success': True,
                'statement': statement_content
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Statement file not found'
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error loading statement: {str(e)}'
        }), 500


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'problems_count': len(problem_manager.list_problems())
    })


if __name__ == '__main__':
    # Create config file if it doesn't exist
    if not os.path.exists('config.yaml'):
        config.save()
        print("Created default config.yaml")

    # Run the Flask app
    host = config.get('web.host', '127.0.0.1')
    port = config.get('web.port', 5001)
    # Default to False for production safety
    debug = config.get('web.debug', False)

    print(f"Starting PocketOJ web interface...")
    print(f"Dashboard: http://{host}:{port}/")
    print(f"API: http://{host}:{port}/api/problems")

    app.run(host=host, port=port, debug=debug,
            use_reloader=False)  # Disable reloader
