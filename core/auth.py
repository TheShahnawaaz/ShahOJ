"""
Authentication service for PocketOJ
Handles Google OAuth integration and session management
"""

import os
from typing import Dict, Tuple, Optional, Set
from authlib.integrations.flask_client import OAuth
from flask import Flask

from .config import config
from .database import DatabaseManager


class AuthService:
    """Handles Google OAuth authentication and session management"""

    def __init__(self, app: Flask, db_manager: DatabaseManager):
        self.db = db_manager
        self.oauth = OAuth(app)

        # Initialize Google OAuth with complete manual configuration
        self.google = self.oauth.register(
            name='google',
            client_id=app.config.get('GOOGLE_CLIENT_ID'),
            client_secret=app.config.get('GOOGLE_CLIENT_SECRET'),
            authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
            access_token_url='https://oauth2.googleapis.com/token',
            userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
            jwks_uri='https://www.googleapis.com/oauth2/v3/certs',  # Added missing jwks_uri
            issuer='https://accounts.google.com',  # Added issuer
            client_kwargs={
                'scope': 'openid email profile'
            }
        )

    def _load_superuser_emails(self) -> Set[str]:
        """Load configured superuser emails from config and environment"""
        configured = config.get('security.superusers', []) or []
        emails = []
        if isinstance(configured, str):
            emails.extend(part.strip() for part in configured.split(',') if part.strip())
        else:
            emails.extend(str(item).strip() for item in configured if str(item).strip())

        env_value = os.environ.get('POCKETOJ_SUPERUSERS', '')
        if env_value:
            emails.extend(part.strip() for part in env_value.split(',') if part.strip())

        return {email.lower() for email in emails if email}

    def _is_superuser(self, email: Optional[str]) -> bool:
        """Check if the given email belongs to a configured superuser"""
        if not email:
            return False
        return email.lower() in self._load_superuser_emails()

    def create_login_url(self, redirect_uri: str):
        """Generate Google OAuth login URL"""
        return self.google.authorize_redirect(redirect_uri)

    def handle_oauth_callback(self) -> Tuple[Dict, str]:
        """
        Handle Google OAuth callback and create persistent session
        Returns: (user_dict, session_token)
        """
        # Get token from Google
        token = self.google.authorize_access_token()
        user_info = token.get('userinfo')

        if not user_info:
            raise ValueError("Failed to get user info from Google")

        # Determine if this user should be treated as a superuser
        is_superuser = self._is_superuser(user_info.get('email'))

        # Create or update user in database
        user = self.db.create_or_update_user(user_info, is_superuser=is_superuser)

        # Create long-lived session (30 days)
        session_token = self.db.create_session(user['id'], timeout_days=30)

        return user, session_token

    def validate_session(self, session_token: str) -> Optional[Dict]:
        """Validate session token and return user if valid"""
        return self.db.validate_session(session_token)

    def logout_session(self, session_token: str):
        """Invalidate a specific session"""
        self.db.invalidate_session(session_token)

    def health_check(self) -> bool:
        """Check if authentication service is properly configured"""
        try:
            return (
                self.google.client_id is not None and
                self.google.client_secret is not None
            )
        except Exception:
            return False
