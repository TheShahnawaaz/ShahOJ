"""
Middleware for PocketOJ authentication and authorization
"""

from functools import wraps
from flask import request, g, jsonify, redirect, url_for, render_template, abort
from typing import Optional, Dict


def setup_auth_middleware(app, auth_service):
    """Setup authentication middleware for Flask app"""

    @app.before_request
    def load_current_user():
        """Load current user from session token before each request"""
        session_token = request.cookies.get('session_token')
        if session_token:
            user = auth_service.validate_session(session_token)
            g.current_user = user
        else:
            g.current_user = None

    @app.context_processor
    def inject_user():
        """Inject current user into all templates"""
        return {'current_user': g.get('current_user')}


def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = g.get('current_user')
        if not user:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            else:
                # Use our custom unauthorized page instead of redirect
                abort(401)
        return f(*args, **kwargs)
    return decorated_function


def require_superuser(f):
    """Decorator that allows access only to superusers"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = g.get('current_user')
        if not user or not user.get('is_superuser'):
            expects_json = request.is_json or request.path.startswith('/api/')
            if expects_json:
                return jsonify({'error': 'Superuser access required'}), 403
            # Use proper 403 error page instead of redirect
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def require_problem_access(permission_type='view'):
    """Decorator to check problem permissions"""
    def decorator(f):
        @wraps(f)
        def decorated_function(slug, *args, **kwargs):
            from .database import DatabaseManager
            from .config import config

            # Get problem from database
            db = DatabaseManager(config.get('database.path', 'pocketoj.db'))
            problem = db.get_problem_by_slug(slug)

            if not problem:
                if request.is_json:
                    return jsonify({'error': 'Problem not found'}), 404
                else:
                    # Use our custom problem not found page
                    return render_template('errors/problem_not_found.html',
                                           problem_slug=slug), 404

            user = g.get('current_user')
            user_id = user['id'] if user else None
            is_superuser = bool(user.get('is_superuser')) if user else False

            if is_superuser:
                g.current_problem = problem
                return f(slug, *args, **kwargs)

            # Check permissions
            has_permission = False

            if permission_type == 'view':
                # Public problems are viewable by everyone
                # Private problems only by author
                has_permission = (
                    problem['is_public'] or
                    (user_id and problem['author_id'] == user_id)
                )

            elif permission_type == 'edit':
                # Only author can edit
                has_permission = user_id and problem['author_id'] == user_id

            elif permission_type == 'delete':
                # Only author can delete
                has_permission = user_id and problem['author_id'] == user_id

            if not has_permission:
                if request.is_json:
                    return jsonify({'error': 'Access denied'}), 403
                else:
                    # Determine specific error message based on context
                    if not user:
                        # Not authenticated - show sign in page
                        return render_template('errors/unauthorized.html'), 401
                    else:
                        # Authenticated but no permission - show access denied
                        error_message = None
                        if permission_type == 'edit':
                            error_message = "You can only edit problems that you created."
                        elif permission_type == 'delete':
                            error_message = "You can only delete problems that you created."
                        elif permission_type == 'view' and not problem['is_public']:
                            error_message = "This problem is private and you don't have access to view it."

                        return render_template('errors/403.html',
                                               error_message=error_message), 403

            # Store problem in g for use in route handler
            g.current_problem = problem
            return f(slug, *args, **kwargs)
        return decorated_function
    return decorator
