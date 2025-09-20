"""
Middleware for PocketOJ authentication and authorization
"""

from functools import wraps
from flask import request, g, jsonify, redirect, url_for
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
                return redirect(url_for('auth_login'))
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
                    return "Problem not found", 404

            user = g.get('current_user')
            user_id = user['id'] if user else None

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
                    return "Access denied", 403

            # Store problem in g for use in route handler
            g.current_problem = problem
            return f(slug, *args, **kwargs)
        return decorated_function
    return decorator
