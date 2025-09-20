"""
Authentication service for PocketOJ
Handles Google OAuth integration and session management
"""

import os
from typing import Dict, Tuple, Optional
from authlib.integrations.flask_client import OAuth
from flask import Flask

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

        # Create or update user in database
        user = self.db.create_or_update_user(user_info)

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
