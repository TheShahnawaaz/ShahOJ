"""
Flask web application for PocketOJ extensible judge system - Multi-User Edition
"""

from dotenv import load_dotenv
from core.middleware import setup_auth_middleware, require_auth, require_problem_access, require_superuser
from core.auth import AuthService
from core.database import DatabaseManager
from core.config import config
from core.problem_manager import ProblemManager
from core.unified_problem_manager import UnifiedProblemManager
from core.time_utils import format_ist, to_ist_iso
from core.jobs import run_auto_build_workflow
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, send_from_directory, g
import os
import sys
import traceback
import hashlib
import json

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Multi-user imports

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = config.get('security.secret_key', os.environ.get(
    'SECRET_KEY', os.urandom(24).hex()))

# Configure OAuth
app.config['GOOGLE_CLIENT_ID'] = os.environ.get('GOOGLE_CLIENT_ID')
app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('GOOGLE_CLIENT_SECRET')

# Initialize multi-user components
db_manager = DatabaseManager(config.get('database.path', 'pocketoj.db'))
auth_service = AuthService(app, db_manager)

# Setup authentication middleware
setup_auth_middleware(app, auth_service)

# Initialize problem managers
problem_manager = ProblemManager()  # Legacy for compatibility
unified_problem_manager = UnifiedProblemManager(
    db_manager)  # New unified manager


@app.route('/')
def dashboard():
    """Main dashboard - shows login prompt if not authenticated, problems if authenticated"""
    try:
        user = g.get('current_user')

        # Get public problems with pagination (available to everyone)
        page = int(request.args.get('page', 1))
        search = request.args.get('search', '')
        difficulty = request.args.get('difficulty', '')

        result = db_manager.get_public_problems(
            search=search,
            difficulty=difficulty,
            page=page,
            limit=12  # Show 12 problems per page on dashboard
        )

        # Get submission counts for all problems on this page
        problem_slugs = [p['slug'] for p in result['problems']]
        submission_counts = db_manager.get_submission_counts_for_problems(
            problem_slugs)
        for p in result['problems']:
            p['submission_count'] = submission_counts.get(p['slug'], 0)

        # Get author information for all problems
        author_info = {}
        for problem in result['problems']:
            if problem.get('author_id') and problem['author_id'] not in author_info:
                author = db_manager.get_user_by_id(problem['author_id'])
                if author:
                    author_info[problem['author_id']] = author

        # Get user's own problems count for stats (only if authenticated)
        user_stats = None
        if user:
            user_problems = db_manager.get_user_problems(user['id'])
            user_stats = {
                'total_problems': len(user_problems),
                'public_count': sum(1 for p in user_problems if p['is_public']),
                'private_count': sum(1 for p in user_problems if not p['is_public'])
            }

        # Get overall system stats
        try:
            import sqlite3
            # Count total public problems
            public_count = result['total']

            # Count total problems in database
            with sqlite3.connect(db_manager.db_path) as conn:
                total_problems = conn.execute(
                    "SELECT COUNT(*) FROM problems").fetchone()[0]
                total_users = conn.execute(
                    "SELECT COUNT(*) FROM users").fetchone()[0]

            system_stats = {
                'total_problems': total_problems,
                'public_problems': public_count,
                'total_users': total_users
            }
        except Exception as e:
            system_stats = {'total_problems': 0,
                            'public_problems': 0, 'total_users': 0}

        # Calculate pagination info
        # Ceiling division for 12 items per page
        limit = 12  # Match the limit used above
        total_pages = (result['total'] + limit - 1) // limit

        return render_template('pages/dashboard.html',
                               problems=result['problems'],
                               author_info=author_info,
                               user_stats=user_stats,
                               system_stats=system_stats,
                               pagination={
                                   'current_page': result['page'],
                                   'total_pages': total_pages,
                                   'total': result['total'],
                                   'has_next': result['has_next']
                               },
                               search=search,
                               difficulty=difficulty,
                               is_authenticated=user is not None)
    except Exception as e:
        return f"Error loading dashboard: {e}", 500


@app.route('/favicon.ico')
def favicon():
    """Serve favicon.ico from static/images directory"""
    return send_from_directory(
        os.path.join(app.root_path, 'static', 'images'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )


@app.route('/playground')
def playground():
    """Code playground for testing without problem context"""
    return render_template('pages/playground.html')


# ============================================================================
# AUTHENTICATION ROUTES (Multi-User)
# ============================================================================

@app.route('/auth/login')
def auth_login():
    """Initiate Google OAuth login"""
    redirect_uri = url_for('auth_callback', _external=True)
    return auth_service.create_login_url(redirect_uri)


@app.route('/auth/callback')
def auth_callback():
    """Handle Google OAuth callback"""
    try:
        user, session_token = auth_service.handle_oauth_callback()

        # Set secure cookie
        # Redirect to dashboard for now
        response = redirect(url_for('dashboard'))
        response.set_cookie(
            'session_token',
            session_token,
            max_age=30*24*60*60,  # 30 days
            secure=request.is_secure,  # Use secure cookies in production
            httponly=True,
            samesite='Lax'
        )

        flash(f'Welcome, {user["name"]}! You are now signed in.', 'success')
        return response

    except Exception as e:
        import traceback
        traceback.print_exc()
        flash('Login failed. Please try again.', 'error')
        return redirect(url_for('dashboard'))


@app.route('/auth/logout')
def auth_logout():
    """Logout user and invalidate session"""
    session_token = request.cookies.get('session_token')
    if session_token:
        auth_service.logout_session(session_token)

    response = redirect(url_for('dashboard'))
    response.delete_cookie('session_token')
    flash('You have been logged out.', 'info')
    return response


@app.route('/api/auth/status')
def auth_status():
    """Get current authentication status"""
    user = g.get('current_user')
    return jsonify({
        'authenticated': user is not None,
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'picture_url': user['picture_url'],
            'is_superuser': bool(user.get('is_superuser'))
        } if user else None
    })


# ============================================================================
# MULTI-USER PROBLEM MANAGEMENT ROUTES
# ============================================================================

# Browse problems route removed - problems now shown in dashboard


@app.route('/my-problems')
@require_auth
def my_problems():
    """User's personal problem dashboard with server-side search and pagination"""
    try:
        user = g.current_user
        page = int(request.args.get('page', 1))
        search = request.args.get('search', '')

        # Get user's problems with search and pagination
        result = db_manager.list_user_problems(
            user['id'],
            page=page,
            limit=12,
            search=search
        )

        # Fetch submission counts for all problems on this page
        problem_slugs = [p['slug'] for p in result['items']]
        submission_counts = db_manager.get_submission_counts_for_problems(
            problem_slugs)
        for p in result['items']:
            p['submission_count'] = submission_counts.get(p['slug'], 0)

        # Calculate pagination info
        limit = 12
        total_pages = max(1, (result['total'] + limit - 1) // limit)

        return render_template('pages/problems/my-problems.html',
                               problems=result['items'],
                               pagination={
                                   'current_page': result['page'],
                                   'total_pages': total_pages,
                                   'total': result['total'],
                                   'has_next': result['has_next']
                               },
                               search=search)
    except Exception as e:
        return f"Error loading problems: {e}", 500


@app.route('/my-submissions')
@require_auth
def my_submissions_page():
    """User's submissions browser with server-side rendering"""
    try:
        user = g.current_user
        page = int(request.args.get('page', 1))
        search = request.args.get('search', '')

        # Get user's submissions with search and pagination
        result = db_manager.list_user_submissions(
            user['id'],
            page=page,
            limit=20,
            search=search
        )

        # Calculate pagination info
        limit = 20
        total_pages = max(1, (result['total'] + limit - 1) // limit)

        return render_template('pages/submissions/my-submissions.html',
                               submissions=result['items'],
                               pagination={
                                   'current_page': result['page'],
                                   'total_pages': total_pages,
                                   'total': result['total'],
                                   'has_next': result['has_next']
                               },
                               search=search)
    except Exception as e:
        return f"Error loading submissions: {e}", 500


@app.route('/admin')
@require_superuser
def admin_dashboard():
    """Admin overview dashboard"""
    stats = db_manager.get_admin_stats()
    recent_problems = db_manager.list_all_problems(
        page=1, limit=5).get('items', [])
    for prob in recent_problems:
        prob['author_display'] = prob.get(
            'author_name') or prob.get('author_email') or 'Unknown'
        prob['author_picture'] = prob.get('author_picture') or ''
    recent_submissions = db_manager.list_all_submissions(
        page=1, limit=5).get('items', [])
    for submission in recent_submissions:
        submission['user_picture'] = submission.get('user_picture') or ''
        submission['verdict_display'] = (submission.get(
            'verdict') or submission.get('status') or '—').upper()
        submission['created_display'] = _format_timestamp(
            submission.get('created_at'))
        submission['created_at_ist'] = to_ist_iso(submission.get('created_at'))
    recent_users = db_manager.list_all_users(page=1, limit=5).get('items', [])
    for user in recent_users:
        user['picture_url'] = user.get('picture_url') or ''
        user['created_display'] = _format_timestamp(user.get('created_at'))
        user['created_at_ist'] = to_ist_iso(user.get('created_at'))
    return render_template('pages/admin/dashboard.html',
                           stats=stats,
                           recent_problems=recent_problems,
                           recent_submissions=recent_submissions,
                           recent_users=recent_users)


@app.route('/admin/problems')
@require_superuser
def admin_problems():
    """Admin problem management view"""
    page = max(1, int(request.args.get('page', 1)))
    search = (request.args.get('search') or '').strip()
    limit = 20
    result = db_manager.list_all_problems(
        page=page, limit=limit, search=search or None)
    problems = result['items']
    for problem in problems:
        problem['author_display'] = problem.get(
            'author_name') or problem.get('author_email') or 'Unknown'
        problem['author_picture'] = problem.get('author_picture') or ''
        problem['updated_display'] = _format_timestamp(
            problem.get('updated_at'))
        problem['created_display'] = _format_timestamp(
            problem.get('created_at'))
        submission_count = problem.get('submission_count')
        problem['submission_count'] = submission_count if submission_count is not None else 0

        # Get test case counts and sizes
        unified_problem = unified_problem_manager.get_problem(problem['slug'])
        if unified_problem:
            from core.test_generator import TestGenerator
            test_generator = TestGenerator(unified_problem)
            test_stats = test_generator.get_test_case_statistics()

            problem['test_stats'] = test_stats
            problem['total_test_cases'] = test_stats.get('total_cases', 0)
            problem['total_test_size_bytes'] = test_stats.get(
                'total_size_bytes', 0)
            problem['total_test_size_formatted'] = _format_file_size(
                test_stats.get('total_size_bytes', 0))
            problem['test_counts'] = {
                'samples': test_stats.get('categories', {}).get('samples', {}).get('count', 0),
                'system': test_stats.get('categories', {}).get('system', {}).get('count', 0)
            }

            # Format individual category sizes
            categories = test_stats.get('categories', {})
            problem['sample_size_formatted'] = _format_file_size(
                categories.get('samples', {}).get('size_bytes', 0))
            problem['system_size_formatted'] = _format_file_size(
                categories.get('system', {}).get('size_bytes', 0))
        else:
            problem['test_stats'] = {'total_cases': 0,
                                     'total_size_bytes': 0, 'categories': {}}
            problem['total_test_cases'] = 0
            problem['total_test_size_bytes'] = 0
            problem['total_test_size_formatted'] = "0 B"
            problem['test_counts'] = {'samples': 0, 'system': 0}
            problem['sample_size_formatted'] = "0 B"
            problem['system_size_formatted'] = "0 B"

    total_pages = max(1, (result['total'] + limit - 1) // limit)
    pagination = {
        'current_page': page,
        'total_pages': total_pages,
        'total': result['total'],
        'has_next': result['has_next']
    }

    return render_template('pages/admin/problems.html',
                           problems=problems,
                           pagination=pagination,
                           search=search,
                           limit=limit)


@app.route('/admin/users')
@require_superuser
def admin_users():
    """Admin user management view"""
    page = max(1, int(request.args.get('page', 1)))
    search = (request.args.get('search') or '').strip()
    limit = 20
    result = db_manager.list_all_users(
        page=page, limit=limit, search=search or None)
    users = result['items']
    for user in users:
        user['created_display'] = _format_timestamp(user.get('created_at'))
        user['last_login_display'] = _format_timestamp(user.get('last_login'))
        user['created_at_ist'] = to_ist_iso(user.get('created_at'))
        user['last_login_ist'] = to_ist_iso(user.get('last_login'))

    total_pages = max(1, (result['total'] + limit - 1) // limit)
    pagination = {
        'current_page': page,
        'total_pages': total_pages,
        'total': result['total'],
        'has_next': result['has_next']
    }

    return render_template('pages/admin/users.html',
                           users=users,
                           pagination=pagination,
                           search=search,
                           limit=limit)


@app.route('/admin/submissions')
@require_superuser
def admin_submissions():
    """Admin submissions monitor view"""
    page = max(1, int(request.args.get('page', 1)))
    search = (request.args.get('search') or '').strip()
    limit = 20
    result = db_manager.list_all_submissions(
        page=page, limit=limit, search=search or None)
    submissions = result['items']
    for submission in submissions:
        submission['created_display'] = _format_timestamp(
            submission.get('created_at'))
        submission['verdict_display'] = (submission.get(
            'verdict') or submission.get('status') or '—').upper()
        submission['user_picture'] = submission.get('user_picture') or ''
        submission['created_at_ist'] = to_ist_iso(submission.get('created_at'))

    total_pages = max(1, (result['total'] + limit - 1) // limit)
    pagination = {
        'current_page': page,
        'total_pages': total_pages,
        'total': result['total'],
        'has_next': result['has_next']
    }

    return render_template('pages/admin/submissions.html',
                           submissions=submissions,
                           pagination=pagination,
                           search=search,
                           limit=limit)


@app.route('/admin/system')
@require_superuser
def admin_system():
    """Admin system health page"""
    stats = db_manager.get_admin_stats()
    db_ok = db_manager.health_check()
    auth_ok = auth_service.health_check()
    problems_dir = unified_problem_manager.problems_dir
    files_ok = problems_dir.exists() and os.access(problems_dir, os.R_OK | os.W_OK)

    return render_template('pages/admin/system.html',
                           stats=stats,
                           health={
                               'database': db_ok,
                               'auth': auth_ok,
                               'files': files_ok
                           },
                           problems_dir=problems_dir)


@app.route('/api/problems/<slug>/toggle-visibility', methods=['POST'])
@require_auth
@require_problem_access('edit')
def toggle_problem_visibility_api(slug):
    """Toggle problem between public and private"""
    user = g.current_user
    is_superuser = bool(user.get('is_superuser'))
    new_visibility = db_manager.toggle_problem_visibility(
        slug, user['id'], force=is_superuser)

    if new_visibility is not None:
        status = "public" if new_visibility else "private"
        return jsonify({
            'success': True,
            'is_public': new_visibility,
            'message': f'Problem is now {status}'
        })
    else:
        return jsonify({'success': False, 'error': 'Failed to update visibility'}), 500


@app.route('/api/problems/<slug>/delete', methods=['DELETE'])
@require_auth
@require_problem_access('delete')
def delete_problem_api(slug):
    """Delete a problem (only by author)"""
    user = g.current_user
    is_superuser = bool(user.get('is_superuser'))

    # Delete from database
    db_success = db_manager.delete_problem(
        slug, user['id'], force=is_superuser)

    if db_success:
        # Delete files
        import shutil
        problem_dir = unified_problem_manager.problems_dir / slug
        if problem_dir.exists():
            try:
                shutil.rmtree(problem_dir)
            except Exception as e:
                pass  # Files might not exist

        return jsonify({'success': True, 'message': 'Problem deleted successfully'})
    else:
        return jsonify({'success': False, 'error': 'Failed to delete problem'}), 500


# ============================================================================
# SUBMISSION ROUTES (MVP: synchronous judging, dedupe by source hash)
# ============================================================================

def _normalize_code_for_hash(code: str) -> str:
    """Moderate normalization: CRLF->LF and strip trailing spaces per line."""
    if code is None:
        return ''
    code = code.replace('\r\n', '\n').replace('\r', '\n')
    lines = code.split('\n')
    return '\n'.join([line.rstrip() for line in lines])


def _format_timestamp(value):
    """Format stored timestamps for display"""
    return format_ist(value)


def _format_file_size(size_bytes):
    """Format file size in bytes to human readable format"""
    if size_bytes == 0:
        return "0 B"

    import math
    size_names = ["B", "KB", "MB", "GB"]
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 1)
    return f"{s} {size_names[i]}"


def _compute_source_hash(problem_slug: str, language: str, source_code: str) -> str:
    payload = f"{problem_slug}\n{language}\n{_normalize_code_for_hash(source_code)}"
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


@app.route('/api/problem/<slug>/submit', methods=['POST'])
@require_auth
@require_problem_access('view')
def submit_solution_api(slug):
    """Submit code for a problem (stores submission and runs judge synchronously)."""
    try:
        user = g.current_user
        data = request.get_json() or {}
        language = (data.get('language') or 'cpp').strip().lower()
        source_code = (data.get('code') or '').rstrip()

        # Validate
        if not source_code:
            return jsonify({'success': False, 'error': 'Source code is required'}), 400
        if language != 'cpp':
            return jsonify({'success': False, 'error': 'Only C++ submissions are supported for now'}), 400
        # Guard: limit size (100KB)
        if len(source_code.encode('utf-8')) > 100 * 1024:
            return jsonify({'success': False, 'error': 'Source too large (max 100KB)'}), 400

        # Dedupe by hash for this user/problem/language
        source_hash = _compute_source_hash(slug, language, source_code)
        existing = db_manager.find_duplicate_submission(
            user['id'], slug, language, source_hash)
        if existing:
            return jsonify({'success': False, 'error': 'Duplicate submission: same code already submitted', 'submission_id': existing}), 409

        # Create submission (status running)
        try:
            submission_id = db_manager.create_submission(
                user_id=user['id'],
                problem_slug=slug,
                language=language,
                source_code=source_code,
                source_hash=source_hash,
                status='running'
            )
        except Exception as e:
            # Handle rare race on unique index
            return jsonify({'success': False, 'error': 'Duplicate submission or DB error'}), 409

        # Judge synchronously
        problem = unified_problem_manager.get_problem(slug)
        if not problem:
            db_manager.update_submission(submission_id, {'status': 'failed'})
            return jsonify({'success': False, 'error': 'Problem not found'}), 404

        from core.solution_tester import SolutionTester
        tester = SolutionTester(problem)
        results = tester.test_solution(source_code, ['samples', 'system'])

        # Map results
        compilation = results.get('compilation', {})
        compile_time_ms = int(compilation.get('time_ms') or 0)
        compile_output = compilation.get('errors') or ''
        statistics = results.get('statistics', {})
        total_time_ms = int(statistics.get('total_time_ms') or 0)
        overall_verdict = results.get('overall_verdict') or 'JE'

        # Create a compact summary instead of truncating full results
        compact_summary = {
            'overall_verdict': results.get('overall_verdict'),
            'compilation': results.get('compilation', {}),
            'statistics': results.get('statistics', {}),
            'categories': results.get('categories', {}),
            # Store metadata for ALL tests, not just failures
            'test_results_summary': {}
        }

        # Add metadata for ALL tests (much smaller than full content)
        test_results = results.get('test_results', {})
        for category, tests in test_results.items():
            compact_summary['test_results_summary'][category] = []
            for test in tests:
                # Store only essential metadata, no input/output content
                test_metadata = {
                    'test_num': test.get('test_num'),
                    'verdict': test.get('verdict'),
                    'time_ms': test.get('time_ms'),
                    'memory_kb': test.get('memory_kb', 0)
                }
                # Only add details for non-AC tests to save space
                if test.get('verdict') != 'AC' and test.get('details'):
                    test_metadata['details'] = test.get('details', '')[:200]

                compact_summary['test_results_summary'][category].append(
                    test_metadata)

        summary_json = json.dumps(compact_summary)

        db_manager.update_submission(submission_id, {
            'status': 'completed',
            'verdict': overall_verdict,
            'compile_time_ms': compile_time_ms,
            'time_ms': total_time_ms,
            'compile_output': compile_output[:100*1024],
            'result_summary_json': summary_json
        })

        return jsonify({
            'success': True,
            'submission_id': submission_id,
            'verdict': overall_verdict,
            'statistics': statistics
        })

    except Exception as e:
        # On unexpected error, attempt to mark submission failed if created
        try:
            if 'submission_id' in locals():
                db_manager.update_submission(
                    submission_id, {'status': 'failed'})
        except Exception:
            pass
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Submission error: {str(e)}'}), 500


@app.route('/api/submissions/<submission_id>')
@require_auth
def get_submission_api(submission_id):
    """Get a single submission; owners see code, others see metadata only (authors allowed)."""
    sub = db_manager.get_submission_by_id(submission_id)
    if not sub:
        return jsonify({'success': False, 'error': 'Submission not found'}), 404

    user = g.current_user
    # Permission: owner, problem author, or superuser
    is_owner = sub['user_id'] == user['id']
    prob = db_manager.get_problem_by_slug(sub['problem_slug'])
    is_author = prob and prob.get('author_id') == user['id']
    is_superuser = bool(user.get('is_superuser'))
    if not (is_owner or is_author or is_superuser):
        # Hide source_code
        sub = {k: v for k, v in sub.items() if k != 'source_code'}
    return jsonify({'success': True, 'submission': sub})


@app.route('/api/problem/<slug>/submissions')
@require_auth
@require_problem_access('view')
def list_problem_submissions_api(slug):
    """List current user's submissions for a problem (owner-only list)."""
    user = g.current_user
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    search = request.args.get('search')
    result = db_manager.list_user_submissions(
        user['id'], problem_slug=slug, page=page, limit=limit, search=search)
    # Do not include source_code in list payload for brevity
    for item in result['items']:
        item.pop('source_code', None)
    return jsonify({'success': True, **result})


@app.route('/api/my/submissions')
@require_auth
def list_my_submissions_api():
    """List current user's submissions across problems (optional problem filter)."""
    user = g.current_user
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    problem_slug = request.args.get('problem')
    search = request.args.get('search')
    result = db_manager.list_user_submissions(
        user['id'], problem_slug=problem_slug, page=page, limit=limit, search=search)
    for item in result['items']:
        item.pop('source_code', None)
    return jsonify({'success': True, **result})


@app.route('/api/problems')
def api_problems():
    """API endpoint to get all problems as JSON"""
    try:
        problems = unified_problem_manager.list_problems()
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

        stats = unified_problem_manager.get_statistics()
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
@require_problem_access('view')
def problem_detail(slug):
    """Show detailed view of a specific problem with multi-user support"""
    try:
        # Get problem from database
        problem_data = db_manager.get_problem_by_slug(slug)
        if not problem_data:
            return "Problem not found", 404

        # Get author information
        author = db_manager.get_user_by_id(
            problem_data['author_id']) if problem_data.get('author_id') else None

        # Get current user
        user = g.get('current_user')

        # Increment view count for public problems (if not author viewing)
        if problem_data['is_public'] and (not user or user['id'] != problem_data['author_id']):
            db_manager.increment_view_count(slug)

        # Get unified problem (database + files)
        unified_problem = unified_problem_manager.get_problem(slug)

        if not unified_problem:
            return "Problem not found", 404

        is_author = bool(
            user and (user['id'] == problem_data.get('author_id')))
        is_superuser = bool(user and user.get('is_superuser'))
        return render_template('pages/problem/detail.html',
                               problem=unified_problem,
                               problem_data=problem_data,
                               author=author,
                               current_user=user,
                               is_author=is_author or is_superuser,
                               is_superuser=is_superuser
                               )
    except Exception as e:
        return f"Error loading problem: {e}", 500


@app.route('/api/problem/<slug>')
def api_problem_detail(slug):
    """API endpoint to get problem details as JSON"""
    try:
        problem = unified_problem_manager.get_problem(slug)
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
@require_auth
def create_problem_form():
    """Show simplified create problem form"""
    return render_template('pages/problem/create-simple.html')


# Deprecated routes - redirect to main create form
@app.route('/create-problem-advanced')
def create_problem_form_advanced():
    """Deprecated: Redirect to simplified create form"""
    return redirect(url_for('create_problem_form'))


@app.route('/create-problem-legacy')
def create_problem_form_legacy():
    """Deprecated: Redirect to simplified create form"""
    return redirect(url_for('create_problem_form'))


@app.route('/create-problem', methods=['POST'])
@require_auth
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
        if unified_problem_manager.problem_exists(form_data['slug']):
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
        problem = unified_problem_manager.create_problem_structure(
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
            pass

        return jsonify({
            'success': True,
            'problem_slug': form_data['slug'],
            'message': 'Problem created successfully!',
            'redirect_url': url_for('problem_detail', slug=form_data['slug'])
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error creating problem: {str(e)}'
        }), 500


@app.route('/problem/<slug>/tests')
@require_problem_access('edit')
def manage_test_cases(slug):
    """Test case management page"""
    try:
        problem = unified_problem_manager.get_problem(slug)
        if not problem:
            return "Problem not found", 404

        # Get test case statistics
        from core.test_generator import TestGenerator
        test_generator = TestGenerator(problem)
        stats = test_generator.get_test_case_statistics()

        files_info = problem.get_files_info()
        solution_path = problem.problem_dir / 'solution.py'
        generator_path = problem.problem_dir / 'generator.py'
        solution_empty = solution_path.exists() and solution_path.stat().st_size == 0
        generator_empty = generator_path.exists() and generator_path.stat().st_size == 0

        return render_template('pages/tests/manage.html',
                               problem=problem,
                               stats=stats,
                               file_status=files_info,
                               solution_empty=solution_empty,
                               generator_empty=generator_empty)
    except Exception as e:
        return f"Error loading test management: {e}", 500


@app.route('/problem/<slug>/test-solution')
@require_problem_access('edit')
def test_solution_page(slug):
    """Solution testing page"""
    try:
        problem = unified_problem_manager.get_problem(slug)
        if not problem:
            return "Problem not found", 404

        return render_template('pages/problem/test-solution.html', problem=problem)
    except Exception as e:
        return f"Error loading solution tester: {e}", 500


# Legacy delete route removed - replaced by multi-user version above


@app.route('/api/problem/<slug>/generate-tests', methods=['POST'])
@require_problem_access('edit')
def generate_tests_api(slug):
    """API endpoint to generate test cases"""
    try:
        problem = unified_problem_manager.get_problem(slug)
        if not problem:
            return jsonify({'success': False, 'error': 'Problem not found'}), 404

        solution_path = problem.problem_dir / 'solution.py'
        if not solution_path.exists() or not solution_path.is_file():
            return jsonify({
                'success': False,
                'error': 'Reference solution (solution.py) is required before generating tests. Add the file and try again.'
            }), 400
        if solution_path.stat().st_size == 0:
            return jsonify({
                'success': False,
                'error': 'Your reference solution (solution.py) is empty. Implement the solution so answers can be generated automatically.'
            }), 400

        generator_path = problem.problem_dir / 'generator.py'
        if not generator_path.exists() or not generator_path.is_file():
            return jsonify({
                'success': False,
                'error': 'Test generator (generator.py) not found. Create it to generate test cases automatically.'
            }), 400
        if generator_path.stat().st_size == 0:
            return jsonify({
                'success': False,
                'error': 'Your generator.py file is empty. Implement it so the platform can create test cases.'
            }), 400

        # Get generation parameters
        data = request.get_json() or {}
        test_category = data.get('category', 'system')
        count = int(
            data.get('count', problem.config.get('tests.system_count', 20)))
        replace_existing = data.get('replace_existing', False)

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
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error generating tests: {str(e)}'
        }), 500


@app.route('/api/problem/<slug>/add-manual-test', methods=['POST'])
@require_problem_access('edit')
def add_manual_test_api(slug):
    """API endpoint to add manual test case"""
    try:
        problem = unified_problem_manager.get_problem(slug)
        if not problem:
            return jsonify({'success': False, 'error': 'Problem not found'}), 404

        solution_path = problem.problem_dir / 'solution.py'
        if not solution_path.exists() or not solution_path.is_file():
            return jsonify({
                'success': False,
                'error': 'Reference solution (solution.py) is required before adding manual tests. Add the file and try again.'
            }), 400
        if solution_path.stat().st_size == 0:
            return jsonify({
                'success': False,
                'error': 'Your reference solution (solution.py) is empty. Implement the solution so answers can be generated automatically.'
            }), 400

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
@require_auth
@require_problem_access('view')
def test_solution_api(slug):
    """API endpoint to test a C++ solution"""
    try:
        problem = unified_problem_manager.get_problem(slug)
        if not problem:
            return jsonify({'success': False, 'error': 'Problem not found'}), 404

        data = request.get_json()
        cpp_code = data.get('code', '').strip()
        test_categories = data.get(
            'categories', ['samples', 'system'])

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
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error testing solution: {str(e)}'
        }), 500


@app.route('/api/quick-test', methods=['POST'])
@require_auth
def independent_quick_test_api():
    """Independent API endpoint for quick testing C++ code (no problem context needed)"""
    try:
        data = request.get_json()
        cpp_code = data.get('code', '').strip()
        test_input = data.get('input', '')  # Don't strip to allow empty input

        if not cpp_code:
            return jsonify({'success': False, 'error': 'Code is required'}), 400

        # Independent quick test using SolutionTester without problem context
        from core.solution_tester import SolutionTester
        tester = SolutionTester(None)  # No problem context needed
        success, output, error = tester.independent_quick_test(
            cpp_code, test_input)

        return jsonify({
            'success': success,
            'output': output,
            'error': error
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error running quick test: {str(e)}'
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
@require_auth
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
        if unified_problem_manager.problem_exists(metadata['slug']):
            # Offer to overwrite or suggest different slug
            return jsonify({
                'success': False,
                'error': f"Problem '{metadata['slug']}' already exists",
                'suggestion': f"Try: {metadata['slug']}-v2 or delete existing problem first",
                'existing_problem_url': url_for('problem_detail', slug=metadata['slug'])
            }), 400

        # Create problem structure
        problem = unified_problem_manager.create_problem_structure(
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
            # Don't fail problem creation if test generation fails
            saved_count = 0

        return jsonify({
            'success': True,
            'problem_slug': metadata['slug'],
            'message': f'Problem created with {saved_count} initial test cases!',
            'redirect_url': url_for('problem_detail', slug=metadata['slug'])
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error creating problem: {str(e)}'
        }), 500


@app.route('/api/create-problem-simple', methods=['POST'])
@require_auth
def create_problem_simple_api():
    """API endpoint for simplified problem creation - only requires statement"""
    try:
        data = request.get_json()

        # Extract metadata
        metadata = {
            'title': data.get('title', '').strip(),
            'slug': data.get('slug', '').strip(),
            'difficulty': data.get('difficulty', 'Medium'),
            'tags': [tag.strip() for tag in data.get('tags', '').split(',') if tag.strip()],
            'time_limit_ms': int(data.get('time_limit', 1000)),
            'memory_limit_mb': int(data.get('memory_limit', 256)),
            'checker_type': data.get('checker_type', 'diff'),
        }

        statement_content = data.get('statement', '').strip()

        # Validate required fields
        if not metadata['title'] or not metadata['slug'] or not statement_content:
            return jsonify({'success': False, 'error': 'Title, slug, and statement are required'}), 400

        # Get current user
        user = g.current_user
        if not user:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401

        # Check if problem already exists (unified check)
        if unified_problem_manager.problem_exists(metadata['slug']):
            return jsonify({
                'success': False,
                'error': f"Problem '{metadata['slug']}' already exists",
                'suggestion': f"Try: {metadata['slug']}-v2 or delete existing problem first",
                'existing_problem_url': url_for('problem_detail', slug=metadata['slug'])
            }), 400

        # Create problem using unified manager (database + files)
        try:
            # Remove title and slug from metadata to avoid duplicate keyword arguments
            # The create_problem method generates its own slug from the title
            metadata_copy = metadata.copy()
            title = metadata_copy.pop('title')
            # Remove slug since it's generated automatically
            metadata_copy.pop('slug', None)

            result = unified_problem_manager.create_problem(
                title=title,
                author_id=user['id'],
                **metadata_copy  # Pass remaining metadata
            )

            # Save the statement content
            problem_dir = unified_problem_manager.problems_dir / \
                result['slug']
            statement_file = problem_dir / 'statement.md'

            with open(statement_file, 'w') as f:
                f.write(statement_content)

            # Update file status in database
            unified_problem_manager.update_file_status(result['slug'])

        except Exception as e:
            return jsonify({'success': False, 'error': f'Failed to create problem: {str(e)}'}), 500

        return jsonify({
            'success': True,
            'problem_slug': metadata['slug'],
            'message': 'Problem created successfully! You can now edit it to add solution, generator, and other files.',
            'redirect_url': url_for('edit_problem_page', slug=metadata['slug'])
        })

    except Exception as e:
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
        problem = unified_problem_manager.get_problem(slug)
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
        problem = unified_problem_manager.get_problem(slug)
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
@require_problem_access('edit')
def edit_problem_page(slug):
    """Problem editing page"""
    try:
        problem = unified_problem_manager.get_problem(slug)
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

        return render_template('pages/problem/edit.html',
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
@require_problem_access('edit')
def save_problem_all_api(slug):
    """API endpoint to save all problem changes"""
    try:
        problem = unified_problem_manager.get_problem(slug)
        if not problem:
            return jsonify({'success': False, 'error': 'Problem not found'}), 404

        data = request.get_json()
        config_data = data.get('config', {})
        files_data = data.get('files', {})
        validator_enabled = data.get('validator_enabled', False)

        # Update configuration in database
        metadata_updates = {}

        for key, value in config_data.items():
            if key == 'tags':
                metadata_updates['tags'] = value
            elif key == 'time_limit_ms':
                metadata_updates['time_limit_ms'] = value
            elif key == 'memory_limit_mb':
                metadata_updates['memory_limit_mb'] = value
            elif key == 'checker_type':
                metadata_updates['checker_type'] = value
            elif key == 'title':
                metadata_updates['title'] = value
            elif key == 'difficulty':
                metadata_updates['difficulty'] = value
            elif key == 'sample_count':
                metadata_updates['sample_count'] = value
            elif key == 'system_count':
                metadata_updates['system_count'] = value
            elif key == 'checker_tolerance':
                metadata_updates['checker_tolerance'] = value

        # Set validator configuration
        metadata_updates['validation_enabled'] = validator_enabled

        # Update metadata in database
        if metadata_updates:
            user = g.current_user
            actor_id = user['id'] if (
                user and not user.get('is_superuser')) else None
            success = unified_problem_manager.update_problem_metadata(
                slug, metadata_updates, actor_id
            )
            if not success:
                return jsonify({'success': False, 'error': 'Failed to update problem metadata'}), 500

        # Save files
        from core.file_manager import FileManager
        file_manager = FileManager(problem.problem_dir)

        saved_files = []
        deleted_files = []

        for filename, content in files_data.items():
            if content and content.strip():  # Save non-empty files
                if file_manager.save_file(filename, content):
                    saved_files.append(filename)
                else:
                    return jsonify({'success': False, 'error': f'Failed to save {filename}'}), 500
            else:
                # Delete empty files
                file_path = problem.problem_dir / filename
                if file_path.exists():
                    try:
                        file_path.unlink()
                        deleted_files.append(filename)
                    except Exception as e:
                        pass  # File might not exist

        # Handle validator file specifically
        if not validator_enabled and 'validator.py' not in files_data:
            validator_path = problem.problem_dir / 'validator.py'
            if validator_path.exists():
                try:
                    validator_path.unlink()
                    deleted_files.append('validator.py')
                except Exception as e:
                    pass  # File might not exist

        # Update file status in database
        unified_problem_manager.update_file_status(slug)

        message_parts = []
        if saved_files:
            message_parts.append(f'Saved {len(saved_files)} files')
        if deleted_files:
            message_parts.append(f'Removed {len(deleted_files)} files')
        message_parts.append('Updated configuration')

        return jsonify({
            'success': True,
            'message': ', '.join(message_parts),
            'saved_files': saved_files,
            'deleted_files': deleted_files,
            'validator_enabled': validator_enabled
        })

    except Exception as e:
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
        problem = unified_problem_manager.get_problem(slug)
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
        problem = unified_problem_manager.get_problem(slug)
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


@app.route('/api/problem/<slug>/ai-auto-build', methods=['POST'])
@require_problem_access('edit')
def ai_auto_build(slug):
    """Run AI auto-build synchronously and return the summary."""
    try:
        problem = unified_problem_manager.get_problem(slug)
        if not problem:
            return jsonify({'success': False, 'error': 'Problem not found'}), 404

        data = request.get_json() or {}
        options = data.get('options') or {}
        user_context = data.get('context', '').strip()

        summary = run_auto_build_workflow(slug, options, user_context)
        return jsonify({'success': True, 'summary': summary})
    except Exception as exc:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(exc)}), 500


@app.route('/api/problem/<slug>/ai-generate', methods=['POST'])
def ai_generate_file_api(slug):
    """API endpoint to generate code files using AI"""
    try:
        problem = unified_problem_manager.get_problem(slug)
        if not problem:
            return jsonify({'success': False, 'error': 'Problem not found'}), 404

        data = request.get_json()
        file_type = data.get('file_type', '').strip()
        user_context = data.get('context', '').strip()

        if file_type not in ['solution', 'generator', 'validator', 'spj']:
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Must be one of: solution, generator, validator, spj'
            }), 400

        # Get problem statement
        statement_file = problem.problem_dir / 'statement.md'
        if not statement_file.exists():
            return jsonify({
                'success': False,
                'error': 'Problem statement not found. Please create statement.md first.'
            }), 400

        with open(statement_file, 'r') as f:
            problem_statement = f.read()

        if not problem_statement.strip():
            return jsonify({
                'success': False,
                'error': 'Problem statement is empty. Please add content to statement.md first.'
            }), 400

        # Import AI service
        from core.ai_service import get_ai_service
        ai_service = get_ai_service()

        if not ai_service:
            return jsonify({
                'success': False,
                'error': 'AI service not available. Please configure OPENAI_API_KEY environment variable.'
            }), 503

        # Generate code based on file type
        try:
            if file_type == 'solution':
                result = ai_service.generate_solution_with_explanation(
                    problem_statement, user_context)
            elif file_type == 'generator':
                result = ai_service.generate_generator_with_explanation(
                    problem_statement, user_context)
            elif file_type == 'validator':
                result = ai_service.generate_validator_with_explanation(
                    problem_statement, user_context)
            elif file_type == 'spj':
                result = ai_service.generate_special_judge_with_explanation(
                    problem_statement, user_context)

            return jsonify({
                'success': True,
                'generated_code': result.code,
                'explanation': result.explanation,
                'file_type': file_type,
                'message': f'Successfully generated {file_type} code using AI'
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'AI generation failed: {str(e)}'
            }), 500

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/problem/<slug>/ai-polish-statement', methods=['POST'])
def ai_polish_statement_api(slug):
    """API endpoint to polish problem statement using AI"""
    try:
        problem = unified_problem_manager.get_problem(slug)
        if not problem:
            return jsonify({'success': False, 'error': 'Problem not found'}), 404

        data = request.get_json()
        raw_statement = data.get('raw_statement', '').strip()
        user_context = data.get('context', '').strip()

        if not raw_statement:
            return jsonify({
                'success': False,
                'error': 'Raw statement content is required'
            }), 400

        # Import AI service
        from core.ai_service import get_ai_service
        ai_service = get_ai_service()

        if not ai_service:
            return jsonify({
                'success': False,
                'error': 'AI service not available. Please configure OPENAI_API_KEY environment variable.'
            }), 503

        # Polish the statement
        try:
            result = ai_service.polish_statement_with_explanation(
                raw_statement, user_context)
            return jsonify({
                'success': True,
                'polished_statement': result.code,
                'explanation': result.explanation,
                'message': 'Statement polished successfully using AI'
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'AI polishing failed: {str(e)}'
            }), 500

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/api/ai/status')
def ai_status_api():
    """Check if AI service is available"""
    try:
        from core.ai_service import get_ai_service
        ai_service = get_ai_service()

        return jsonify({
            'success': True,
            'ai_available': ai_service is not None,
            'model': ai_service.model if ai_service else None
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'ai_available': False,
            'error': str(e)
        })


@app.route('/health')
def health_check():
    """Enhanced health check endpoint with multi-user support"""
    try:
        # Check database connectivity
        db_healthy = db_manager.health_check()

        # Check authentication service
        auth_healthy = auth_service.health_check()

        # Check file system
        problems_accessible = os.access(
            'problems/', os.R_OK | os.W_OK) if os.path.exists('problems/') else True

        # Overall health status
        is_healthy = db_healthy and auth_healthy and problems_accessible

        return jsonify({
            'status': 'healthy' if is_healthy else 'unhealthy',
            'version': '2.0.0-multiuser',
            'multiuser_enabled': True,
            'database': db_healthy,
            'authentication': auth_healthy,
            'file_system': problems_accessible,
            'problems_count': len(unified_problem_manager.list_problems()),
            'timestamp': __import__('datetime').datetime.utcnow().isoformat()
        }), 200 if is_healthy else 503

    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'version': '2.0.0-multiuser'
        }), 503


if __name__ == '__main__':
    # Create config file if it doesn't exist
    if not os.path.exists('config.yaml'):
        config.save()
        pass  # Config created

    # Run the Flask app
    host = config.get('web.host', '127.0.0.1')
    port = config.get('web.port', 5001)
    # Default to False for production safety
    debug = config.get('web.debug', False)

    app.run(host=host, port=port, debug=debug,
            use_reloader=False)  # Disable reloader
