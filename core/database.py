"""
Database manager for PocketOJ multi-user system
Handles SQLite database operations for users, problems, and sessions
"""

import sqlite3
import uuid
import secrets
import json
from datetime import timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

from .time_utils import format_ist, to_ist, to_ist_iso, to_utc, utc_now, utc_now_iso


class DatabaseManager:
    """Manages SQLite database for multi-user PocketOJ"""

    def __init__(self, db_path: str = "pocketoj.db"):
        self.db_path = Path(db_path)
        self.init_database()

    def init_database(self):
        """Initialize SQLite database with all required tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")

            # Create tables
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    google_id TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    picture_url TEXT,
                    is_superuser BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS problems (

                    id TEXT PRIMARY KEY,
                    slug TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    author_id TEXT NOT NULL,
                    is_public BOOLEAN DEFAULT FALSE,
                    difficulty TEXT DEFAULT 'Medium',
                    tags TEXT DEFAULT '[]',
                    
                    -- Execution limits
                    time_limit_ms INTEGER DEFAULT 1000,
                    memory_limit_mb INTEGER DEFAULT 256,
                    
                    -- Checker configuration
                    checker_type TEXT DEFAULT 'diff',
                    checker_tolerance REAL DEFAULT 1e-6,
                    
                    -- Test configuration
                    sample_count INTEGER DEFAULT 3,
                    system_count INTEGER DEFAULT 20,
                    
                    -- Validation settings
                    validation_enabled BOOLEAN DEFAULT FALSE,
                    validation_strict BOOLEAN DEFAULT TRUE,
                    
                    -- File status tracking
                    has_statement BOOLEAN DEFAULT FALSE,
                    has_solution BOOLEAN DEFAULT FALSE,
                    has_generator BOOLEAN DEFAULT FALSE,
                    has_validator BOOLEAN DEFAULT FALSE,
                    has_custom_checker BOOLEAN DEFAULT FALSE,
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    view_count INTEGER DEFAULT 0,
                    FOREIGN KEY (author_id) REFERENCES users(id)
                );
                
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_token TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_problems_author_public ON problems(author_id, is_public);
                CREATE INDEX IF NOT EXISTS idx_problems_public_updated ON problems(is_public, updated_at);
                CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(session_token);
                CREATE INDEX IF NOT EXISTS idx_sessions_expires ON user_sessions(expires_at);
            """)

            # Create submissions table (for storing user submissions)
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS submissions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    problem_slug TEXT NOT NULL,
                    language TEXT NOT NULL,
                    source_code TEXT NOT NULL,
                    source_hash TEXT NOT NULL,
                    status TEXT NOT NULL CHECK (status IN ('queued','running','completed','failed')),
                    verdict TEXT,
                    compile_time_ms INTEGER,
                    time_ms INTEGER,
                    memory_kb INTEGER,
                    compile_output TEXT,
                    runtime_stderr TEXT,
                    result_summary_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );

                CREATE UNIQUE INDEX IF NOT EXISTS idx_submissions_dedupe
                    ON submissions(user_id, problem_slug, language, source_hash);
                CREATE INDEX IF NOT EXISTS idx_submissions_user_created
                    ON submissions(user_id, created_at);
                CREATE INDEX IF NOT EXISTS idx_submissions_problem_created
                    ON submissions(problem_slug, created_at);
                CREATE INDEX IF NOT EXISTS idx_submissions_status
                    ON submissions(status);
            """)

            # Run migrations for existing databases
            self._run_migrations()
            self._remove_description_column()

    def _normalize_user_row(self, row: sqlite3.Row) -> Optional[Dict]:
        """Convert SQLite row to dict with proper boolean types"""
        if row is None:
            return None
        user = dict(row)
        if 'is_superuser' in user:
            user['is_superuser'] = bool(user['is_superuser'])
        return user

    def _run_migrations(self):
        """Run database migrations for existing databases"""
        with sqlite3.connect(self.db_path) as conn:
            # Check if new columns exist, if not add them
            cursor = conn.cursor()

            # Get current table schema
            cursor.execute("PRAGMA table_info(problems)")
            columns = [row[1] for row in cursor.fetchall()]

            # List of new columns to add
            new_columns = [
                ('time_limit_ms', 'INTEGER DEFAULT 1000'),
                ('memory_limit_mb', 'INTEGER DEFAULT 256'),
                ('checker_type', 'TEXT DEFAULT "diff"'),
                ('checker_tolerance', 'REAL DEFAULT 1e-6'),
                ('sample_count', 'INTEGER DEFAULT 3'),
                ('system_count', 'INTEGER DEFAULT 20'),
                ('validation_enabled', 'BOOLEAN DEFAULT FALSE'),
                ('validation_strict', 'BOOLEAN DEFAULT TRUE'),
                ('has_statement', 'BOOLEAN DEFAULT FALSE'),
                ('has_solution', 'BOOLEAN DEFAULT FALSE'),
                ('has_generator', 'BOOLEAN DEFAULT FALSE'),
                ('has_validator', 'BOOLEAN DEFAULT FALSE'),
                ('has_custom_checker', 'BOOLEAN DEFAULT FALSE'),
            ]

            # Add missing columns
            for column_name, column_def in new_columns:
                if column_name not in columns:
                    try:
                        conn.execute(
                            f"ALTER TABLE problems ADD COLUMN {column_name} {column_def}")
                        pass  # Column added successfully
                    except Exception as e:
                        pass  # Column might already exist

            # Ensure users table has is_superuser column
            cursor.execute("PRAGMA table_info(users)")
            user_columns = [row[1] for row in cursor.fetchall()]
            if 'is_superuser' not in user_columns:
                try:
                    conn.execute("ALTER TABLE users ADD COLUMN is_superuser BOOLEAN DEFAULT FALSE")
                except Exception:
                    pass

    def _remove_description_column(self):
        """Remove description column from problems table if it exists"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check if description column exists
            cursor.execute("PRAGMA table_info(problems)")
            columns = [row[1] for row in cursor.fetchall()]

            if 'description' in columns:
                try:
                    # SQLite doesn't support DROP COLUMN directly, so we need to recreate the table
                    # First, get all data from the current table
                    cursor.execute("SELECT * FROM problems")
                    all_data = cursor.fetchall()

                    # Get column names excluding description
                    cursor.execute("PRAGMA table_info(problems)")
                    all_columns = cursor.fetchall()
                    new_columns = [
                        col for col in all_columns if col[1] != 'description']

                    # Create new table without description column
                    cursor.execute("DROP TABLE IF EXISTS problems_new")

                    # Recreate the table structure without description
                    cursor.execute("""
                        CREATE TABLE problems_new (
                            id TEXT PRIMARY KEY,
                            slug TEXT UNIQUE NOT NULL,
                            title TEXT NOT NULL,
                            author_id TEXT NOT NULL,
                            is_public BOOLEAN DEFAULT FALSE,
                            difficulty TEXT DEFAULT 'Medium',
                            tags TEXT DEFAULT '[]',
                            
                            -- Execution limits
                            time_limit_ms INTEGER DEFAULT 1000,
                            memory_limit_mb INTEGER DEFAULT 256,
                            
                            -- Checker configuration
                            checker_type TEXT DEFAULT 'diff',
                            checker_tolerance REAL DEFAULT 1e-6,
                            
                            -- Test configuration
                            sample_count INTEGER DEFAULT 3,
                            system_count INTEGER DEFAULT 20,
                            
                            -- Validation settings
                            validation_enabled BOOLEAN DEFAULT FALSE,
                            validation_strict BOOLEAN DEFAULT TRUE,
                            
                            -- File status tracking
                            has_statement BOOLEAN DEFAULT FALSE,
                            has_solution BOOLEAN DEFAULT FALSE,
                            has_generator BOOLEAN DEFAULT FALSE,
                            has_validator BOOLEAN DEFAULT FALSE,
                            has_custom_checker BOOLEAN DEFAULT FALSE,
                            
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            view_count INTEGER DEFAULT 0,
                            FOREIGN KEY (author_id) REFERENCES users(id)
                        )
                    """)

                    # Copy data excluding description column
                    if all_data:
                        # Get the column indices excluding description
                        old_column_names = [col[1] for col in all_columns]
                        description_index = old_column_names.index(
                            'description')

                        # Prepare insert statement for new table
                        new_column_names = [col[1] for col in new_columns]
                        placeholders = ', '.join(
                            ['?' for _ in new_column_names])
                        insert_sql = f"INSERT INTO problems_new ({', '.join(new_column_names)}) VALUES ({placeholders})"

                        # Copy data row by row, excluding description column
                        for row in all_data:
                            new_row = list(row)
                            # Remove description value
                            new_row.pop(description_index)
                            cursor.execute(insert_sql, new_row)

                    # Replace old table with new table
                    cursor.execute("DROP TABLE problems")
                    cursor.execute(
                        "ALTER TABLE problems_new RENAME TO problems")

                    # Recreate indices
                    cursor.execute(
                        "CREATE INDEX IF NOT EXISTS idx_problems_author_public ON problems(author_id, is_public)")
                    cursor.execute(
                        "CREATE INDEX IF NOT EXISTS idx_problems_public_updated ON problems(is_public, updated_at)")

                    pass  # Column removed successfully

                except Exception as e:
                    # Rollback by dropping the new table if it exists
                    try:
                        cursor.execute("DROP TABLE IF EXISTS problems_new")
                    except:
                        pass
            else:
                pass  # Description column not found, no migration needed

    def create_or_update_user(self, google_user_info: Dict, is_superuser: bool = False) -> Dict:
        """Create new user or update existing user from Google OAuth info"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            # Determine current record, if any
            user = conn.execute(
                "SELECT * FROM users WHERE google_id = ?",
                (google_user_info['sub'],)
            ).fetchone()

            is_superuser_int = 1 if is_superuser else 0

            if user:
                # Update existing user information and superuser flag
                conn.execute("""
                    UPDATE users SET 
                        name = ?, 
                        picture_url = ?, 
                        last_login = CURRENT_TIMESTAMP,
                        is_superuser = ?
                    WHERE google_id = ?
                """, (
                    google_user_info['name'],
                    google_user_info.get('picture', ''),
                    is_superuser_int,
                    google_user_info['sub']
                ))

                updated_user = conn.execute(
                    "SELECT * FROM users WHERE google_id = ?",
                    (google_user_info['sub'],)
                ).fetchone()
                return self._normalize_user_row(updated_user)

            # Create new user
            user_id = str(uuid.uuid4())
            conn.execute("""
                INSERT INTO users (id, google_id, email, name, picture_url, is_superuser)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                google_user_info['sub'],
                google_user_info['email'],
                google_user_info['name'],
                google_user_info.get('picture', ''),
                is_superuser_int
            ))

            new_user = conn.execute(
                "SELECT * FROM users WHERE google_id = ?",
                (google_user_info['sub'],)
            ).fetchone()
            return self._normalize_user_row(new_user)


    def create_session(self, user_id: str, timeout_days: int = 30) -> str:
        """Create a new session for user"""
        session_token = secrets.token_urlsafe(32)
        session_id = str(uuid.uuid4())
        expires_at = (utc_now() + timedelta(days=timeout_days)).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            # Clean up old sessions for this user (keep only latest 5)
            conn.execute("""
                DELETE FROM user_sessions 
                WHERE user_id = ? AND id NOT IN (
                    SELECT id FROM user_sessions 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT 5
                )
            """, (user_id, user_id))

            # Create new session
            conn.execute("""
                INSERT INTO user_sessions (id, user_id, session_token, expires_at)
                VALUES (?, ?, ?, ?)
            """, (session_id, user_id, session_token, expires_at))

        return session_token

    def validate_session(self, session_token: str) -> Optional[Dict]:
        """Validate session token and return user if valid"""
        if not session_token:
            return None

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            # Get session and user info
            result = conn.execute("""
                SELECT u.*, s.expires_at, s.id as session_id
                FROM users u
                JOIN user_sessions s ON u.id = s.user_id
                WHERE s.session_token = ? AND s.expires_at > CURRENT_TIMESTAMP
            """, (session_token,)).fetchone()

            if result:
                # Update last_used_at
                conn.execute("""
                    UPDATE user_sessions 
                    SET last_used_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (result['session_id'],))

                user = self._normalize_user_row(result)
                if user:
                    user['session_id'] = result['session_id']
                    user['expires_at'] = result['expires_at']
                return user

        return None

    def invalidate_session(self, session_token: str):
        """Invalidate a specific session"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "DELETE FROM user_sessions WHERE session_token = ?",
                (session_token,)
            )

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            result = conn.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            return self._normalize_user_row(result)

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            result = conn.execute(
                "SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            return self._normalize_user_row(result)

    def insert_problem(self, problem_data: Dict):
        """Insert new problem into database with all metadata"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                    INSERT INTO problems (
                        id, slug, title, author_id, is_public, difficulty, tags,
                        time_limit_ms, memory_limit_mb, checker_type, checker_tolerance,
                        sample_count, system_count, validation_enabled, validation_strict,
                        has_statement, has_solution, has_generator, has_validator, has_custom_checker,
                        created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                problem_data['id'],
                problem_data['slug'],
                problem_data['title'],
                problem_data['author_id'],
                problem_data.get('is_public', False),
                problem_data.get('difficulty', 'Medium'),
                json.dumps(problem_data.get('tags', [])),
                problem_data.get('time_limit_ms', 1000),
                problem_data.get('memory_limit_mb', 256),
                problem_data.get('checker_type', 'diff'),
                problem_data.get('checker_tolerance', 1e-6),
                problem_data.get('sample_count', 3),
                problem_data.get('system_count', 20),
                problem_data.get('validation_enabled', False),
                problem_data.get('validation_strict', True),
                problem_data.get('has_statement', False),
                problem_data.get('has_solution', False),
                problem_data.get('has_generator', False),
                problem_data.get('has_validator', False),
                problem_data.get('has_custom_checker', False),
                (to_utc(problem_data.get('created_at')) or utc_now()).isoformat()
            ))

    def update_problem_metadata(self, slug: str, metadata: Dict, author_id: str = None):
        """Update problem metadata in database"""
        with sqlite3.connect(self.db_path) as conn:
            # Build dynamic update query
            update_fields = []
            values = []

            # List of updatable fields
            updatable_fields = [
                'title', 'difficulty', 'tags', 'is_public',
                'time_limit_ms', 'memory_limit_mb', 'checker_type', 'checker_tolerance',
                'sample_count', 'system_count', 'validation_enabled', 'validation_strict',
                'has_statement', 'has_solution', 'has_generator', 'has_validator', 'has_custom_checker'
            ]

            for field in updatable_fields:
                if field in metadata:
                    if field == 'tags':
                        update_fields.append(f"{field} = ?")
                        values.append(json.dumps(metadata[field]))
                    else:
                        update_fields.append(f"{field} = ?")
                        values.append(metadata[field])

            if update_fields:
                # Add updated_at timestamp
                update_fields.append("updated_at = ?")
                values.append(utc_now_iso())

                # Add slug for WHERE clause
                values.append(slug)

                # Add author_id for WHERE clause if provided (for security)
                where_clause = "slug = ?"
                if author_id:
                    where_clause += " AND author_id = ?"
                    values.append(author_id)

                query = f"UPDATE problems SET {', '.join(update_fields)} WHERE {where_clause}"
                conn.execute(query, values)
                return conn.total_changes > 0

            return False

    def update_file_status(self, slug: str, file_status: Dict):
        """Update file status flags for a problem"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE problems SET 
                    has_statement = ?, has_solution = ?, has_generator = ?, 
                    has_validator = ?, has_custom_checker = ?, updated_at = ?
                WHERE slug = ?
            """, (
                file_status.get('has_statement', False),
                file_status.get('has_solution', False),
                file_status.get('has_generator', False),
                file_status.get('has_validator', False),
                file_status.get('has_custom_checker', False),
                utc_now_iso(),
                slug
            ))

    def get_problem_by_slug(self, slug: str) -> Optional[Dict]:
        """Get problem by slug"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            result = conn.execute(
                "SELECT * FROM problems WHERE slug = ?", (slug,)).fetchone()
            if result:
                problem = dict(result)
                # Parse tags JSON
                problem['tags'] = json.loads(problem['tags'])

                for date_field in ['created_at', 'updated_at']:
                    raw_value = problem.get(date_field)
                    localized = to_ist(raw_value)
                    problem[f'{date_field}_display'] = format_ist(raw_value)
                    problem[f'{date_field}_iso'] = localized.isoformat() if localized else ''
                    problem[date_field] = localized

                return problem
            return None

    def get_user_problems(self, user_id: str) -> List[Dict]:
        """Get all problems by a user"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            results = conn.execute("""
                SELECT * FROM problems 
                WHERE author_id = ? 
                ORDER BY updated_at DESC
            """, (user_id,)).fetchall()

            problems = []
            for row in results:
                problem = dict(row)
                problem['tags'] = json.loads(problem['tags'])

                for date_field in ['created_at', 'updated_at']:
                    raw_value = problem.get(date_field)
                    localized = to_ist(raw_value)
                    problem[f'{date_field}_display'] = format_ist(raw_value)
                    problem[f'{date_field}_iso'] = localized.isoformat() if localized else ''
                    problem[date_field] = localized

                problems.append(problem)
            return problems

    def list_user_problems(self, user_id: str, page: int = 1, limit: int = 20, search: Optional[str] = None) -> Dict[str, Any]:
        """List a user's problems with search and pagination"""
        offset = max(0, (page - 1) * limit)
        base_where = "WHERE author_id = ?"
        params: List[Any] = [user_id]

        if search:
            like = f"%{search}%"
            base_where += """ AND (
                title LIKE ? OR 
                slug LIKE ? OR 
                difficulty LIKE ? OR 
                tags LIKE ? OR 
                CASE WHEN is_public = 1 THEN 'public' ELSE 'private' END LIKE ?
            )"""
            params.extend([like, like, like, like, like])

        query = f"""
            SELECT * FROM problems
            {base_where}
            ORDER BY updated_at DESC
            LIMIT ? OFFSET ?
        """
        count_query = f"SELECT COUNT(*) FROM problems {base_where}"

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            items = conn.execute(query, params + [limit, offset]).fetchall()
            total = conn.execute(count_query, params).fetchone()[0]

            problems = []
            for row in items:
                problem = dict(row)
                problem['tags'] = json.loads(problem['tags'])

                for date_field in ['created_at', 'updated_at']:
                    raw_value = problem.get(date_field)
                    localized = to_ist(raw_value)
                    problem[f'{date_field}_display'] = format_ist(raw_value)
                    problem[f'{date_field}_iso'] = localized.isoformat() if localized else ''
                    problem[date_field] = localized

                problems.append(problem)

            return {
                'items': problems,
                'total': total,
                'page': page,
                'has_next': (page * limit) < total
            }

    def get_submission_counts_for_problems(self, problem_slugs: List[str]) -> Dict[str, int]:
        """Return a dict mapping problem_slug to total submission count (globally)"""
        if not problem_slugs:
            return {}
        placeholders = ','.join(['?'] * len(problem_slugs))
        query = f"""
            SELECT problem_slug, COUNT(*) as count
            FROM submissions
            WHERE problem_slug IN ({placeholders})
            GROUP BY problem_slug
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, problem_slugs).fetchall()
            return {row['problem_slug']: row['count'] for row in rows}

    def get_user_solve_status_for_problems(self, user_id: str, problem_slugs: List[str]) -> Dict[str, str]:
        """
        Get solve status for a user across multiple problems.
        Returns dict mapping problem_slug to status: 'solved', 'attempted', or 'not_attempted'
        
        Status logic:
        - solved: Has at least one submission with verdict 'AC'
        - attempted: Has submissions but none with verdict 'AC'
        - not_attempted: No submissions
        """
        if not problem_slugs or not user_id:
            return {}
        
        placeholders = ','.join(['?'] * len(problem_slugs))
        query = f"""
            SELECT 
                problem_slug,
                MAX(CASE WHEN verdict = 'AC' THEN 1 ELSE 0 END) as has_accepted,
                COUNT(*) as submission_count
            FROM submissions
            WHERE user_id = ? AND problem_slug IN ({placeholders})
            GROUP BY problem_slug
        """
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, [user_id] + problem_slugs).fetchall()
            
            status_map = {}
            for row in rows:
                slug = row['problem_slug']
                if row['has_accepted']:
                    status_map[slug] = 'solved'
                else:
                    status_map[slug] = 'attempted'
            
            # Mark problems with no submissions as not_attempted
            for slug in problem_slugs:
                if slug not in status_map:
                    status_map[slug] = 'not_attempted'
            
            return status_map

    def get_public_problems(self, search: str = None, difficulty: str = None,
                            page: int = 1, limit: int = 20) -> Dict:
        """Get public problems with filtering and pagination"""
        offset = (page - 1) * limit

        # Build query
        query = """
            SELECT p.*, u.name as author_name, u.picture_url as author_picture 
            FROM problems p 
            JOIN users u ON p.author_id = u.id 
            WHERE p.is_public = 1
        """
        params = []

        if search:
            # Enhanced search: match against title, tags, difficulty, and author name
            query += """ AND (
                p.title LIKE ? OR 
                p.tags LIKE ? OR 
                p.difficulty LIKE ? OR 
                u.name LIKE ?
            )"""
            search_param = f"%{search}%"
            params.extend([search_param, search_param,
                          search_param, search_param])

        if difficulty:
            query += " AND p.difficulty = ?"
            params.append(difficulty)

        query += " ORDER BY p.updated_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            results = conn.execute(query, params).fetchall()

            problems = []
            for row in results:
                problem = dict(row)
                problem['tags'] = json.loads(problem['tags'])

                for date_field in ['created_at', 'updated_at']:
                    raw_value = problem.get(date_field)
                    localized = to_ist(raw_value)
                    problem[f'{date_field}_display'] = format_ist(raw_value)
                    problem[f'{date_field}_iso'] = localized.isoformat() if localized else ''
                    problem[date_field] = localized

                # Add author info
                problem['author'] = {
                    'name': problem['author_name'],
                    'picture_url': problem['author_picture']
                }
                problems.append(problem)

            # Get total count
            count_query = """
                SELECT COUNT(*) FROM problems p 
                JOIN users u ON p.author_id = u.id 
                WHERE p.is_public = 1
            """
            count_params = []

            if search:
                # Enhanced search: match against title, tags, difficulty, and author name
                count_query += """ AND (
                    p.title LIKE ? OR 
                    p.tags LIKE ? OR 
                    p.difficulty LIKE ? OR 
                    u.name LIKE ?
                )"""
                search_param = f"%{search}%"
                count_params.extend(
                    [search_param, search_param, search_param, search_param])

            if difficulty:
                count_query += " AND p.difficulty = ?"
                count_params.append(difficulty)

            total = conn.execute(count_query, count_params).fetchone()[0]

        return {
            'problems': problems,
            'total': total,
            'page': page,
            'has_next': (page * limit) < total
        }

    def toggle_problem_visibility(self, slug: str, author_id: Optional[str], force: bool = False) -> Optional[bool]:
        """Toggle problem visibility, returns new visibility state"""
        with sqlite3.connect(self.db_path) as conn:
            if force or not author_id:
                result = conn.execute("""
                    SELECT is_public FROM problems 
                    WHERE slug = ?
                """, (slug,)).fetchone()
            else:
                result = conn.execute("""
                    SELECT is_public FROM problems 
                    WHERE slug = ? AND author_id = ?
                """, (slug, author_id)).fetchone()

            if not result:
                return None

            current_visibility = result[0] if not isinstance(result, dict) else result['is_public']
            new_visibility = not current_visibility

            if force or not author_id:
                conn.execute("""
                    UPDATE problems 
                    SET is_public = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE slug = ?
                """, (new_visibility, slug))
            else:
                conn.execute("""
                    UPDATE problems 
                    SET is_public = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE slug = ? AND author_id = ?
                """, (new_visibility, slug, author_id))

            return new_visibility

    def delete_problem(self, slug: str, author_id: Optional[str], force: bool = False) -> bool:
        """Delete problem. Requires author ownership unless force is True"""
        with sqlite3.connect(self.db_path) as conn:
            if force or not author_id:
                result = conn.execute("""
                    SELECT id FROM problems 
                    WHERE slug = ?
                """, (slug,)).fetchone()
            else:
                result = conn.execute("""
                    SELECT id FROM problems 
                    WHERE slug = ? AND author_id = ?
                """, (slug, author_id)).fetchone()

            if not result:
                return False

            if force or not author_id:
                conn.execute(
                    "DELETE FROM problems WHERE slug = ?", (slug,))
            else:
                conn.execute(
                    "DELETE FROM problems WHERE slug = ? AND author_id = ?", (slug, author_id))
            return True


    def increment_view_count(self, slug: str):
        """Increment view count for public problems"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE problems 
                SET view_count = view_count + 1 
                WHERE slug = ? AND is_public = 1
            """, (slug,))

    def health_check(self) -> bool:
        """Check database health"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("SELECT COUNT(*) FROM users").fetchone()
                return True
        except Exception:
            return False

    # ===========================
    # Submissions - CRUD helpers
    # ===========================

    def create_submission(self, user_id: str, problem_slug: str, language: str,
                          source_code: str, source_hash: str, status: str = 'running') -> str:
        """Create a new submission and return its id.

        Status defaults to 'running' for synchronous judging.
        """
        submission_id = str(uuid.uuid4())
        # Store timestamps in UTC for consistent conversions
        created_at = utc_now_iso()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO submissions (
                    id, user_id, problem_slug, language, source_code, source_hash, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (submission_id, user_id, problem_slug,
                 language, source_code, source_hash, status, created_at)
            )
        return submission_id

    def update_submission(self, submission_id: str, fields: Dict[str, Any]) -> bool:
        """Update fields on a submission. Returns True if any row updated."""
        if not fields:
            return False

        allowed = {
            'status', 'verdict', 'compile_time_ms', 'time_ms', 'memory_kb',
            'compile_output', 'runtime_stderr', 'result_summary_json'
        }
        set_parts = []
        values: List[Any] = []
        for key, value in fields.items():
            if key in allowed:
                set_parts.append(f"{key} = ?")
                values.append(value)

        if not set_parts:
            return False

        # Always update modified timestamp in UTC
        set_parts.append("updated_at = ?")
        values.append(utc_now_iso())
        values.append(submission_id)

        sql = f"UPDATE submissions SET {', '.join(set_parts)} WHERE id = ?"
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(sql, values)
            return conn.total_changes > 0

    def get_submission_by_id(self, submission_id: str) -> Optional[Dict]:
        """Fetch a submission by id."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM submissions WHERE id = ?",
                (submission_id,)
            ).fetchone()
            if not row:
                return None

            submission = dict(row)
            submission['created_display'] = format_ist(submission.get('created_at'))
            submission['created_at_ist'] = to_ist_iso(submission.get('created_at'))
            submission['updated_display'] = format_ist(submission.get('updated_at'))
            submission['updated_at_ist'] = to_ist_iso(submission.get('updated_at'))
            return submission

    def find_duplicate_submission(self, user_id: str, problem_slug: str, language: str,
                                  source_hash: str) -> Optional[str]:
        """Return an existing submission id if same hash exists for this user/problem/language."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT id FROM submissions
                WHERE user_id = ? AND problem_slug = ? AND language = ? AND source_hash = ?
                LIMIT 1
                """,
                (user_id, problem_slug, language, source_hash)
            ).fetchone()
            return row[0] if row else None

    def list_user_submissions(self, user_id: str, problem_slug: Optional[str] = None,
                              page: int = 1, limit: int = 20, search: Optional[str] = None) -> Dict[str, Any]:
        """List a user's submissions, optionally filtered by problem_slug."""
        offset = max(0, (page - 1) * limit)
        base_where = "WHERE user_id = ?"
        params: List[Any] = [user_id]
        if problem_slug:
            base_where += " AND problem_slug = ?"
            params.append(problem_slug)
        if search:
            like = f"%{search}%"
            base_where += " AND (problem_slug LIKE ? OR language LIKE ? OR IFNULL(verdict,'') LIKE ? OR IFNULL(status,'') LIKE ?)"
            params.extend([like, like, like, like])

        query = f"""
            SELECT * FROM submissions
            {base_where}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        count_query = f"SELECT COUNT(*) FROM submissions {base_where}"

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            items = conn.execute(query, params + [limit, offset]).fetchall()
            total = conn.execute(count_query, params).fetchone()[0]

        submissions: List[Dict[str, Any]] = []
        for row in items:
            submission = dict(row)
            submission['created_display'] = format_ist(submission.get('created_at'))
            submission['created_at_ist'] = to_ist_iso(submission.get('created_at'))
            submission['updated_display'] = format_ist(submission.get('updated_at'))
            submission['updated_at_ist'] = to_ist_iso(submission.get('updated_at'))
            submissions.append(submission)

        return {
            'items': submissions,
            'total': total,
            'page': page,
            'has_next': (page * limit) < total
        }

    def list_all_problems(self, page: int = 1, limit: int = 20, search: Optional[str] = None) -> Dict[str, Any]:
        """List problems for admin view with author and submission counts"""
        offset = max(0, (page - 1) * limit)
        base_where = "WHERE 1=1"
        params: List[Any] = []

        if search:
            like = f"%{search}%"
            base_where += " AND (p.slug LIKE ? OR p.title LIKE ? OR p.tags LIKE ? OR p.difficulty LIKE ? OR IFNULL(u.name,'') LIKE ? OR IFNULL(u.email,'') LIKE ?)"
            params.extend([like, like, like, like, like, like])

        query = f"""
            SELECT p.*,
                   u.name AS author_name,
                   u.email AS author_email,
                   u.picture_url AS author_picture,
                   COUNT(s.id) AS submission_count
            FROM problems p
            LEFT JOIN users u ON p.author_id = u.id
            LEFT JOIN submissions s ON s.problem_slug = p.slug
            {base_where}
            GROUP BY p.id
            ORDER BY p.updated_at DESC
            LIMIT ? OFFSET ?
        """

        count_query = f"""
            SELECT COUNT(*)
            FROM problems p
            LEFT JOIN users u ON p.author_id = u.id
            {base_where}
        """

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            items = conn.execute(query, params + [limit, offset]).fetchall()
            total = conn.execute(count_query, params).fetchone()[0]

        problems: List[Dict[str, Any]] = []
        for row in items:
            problem = dict(row)
            tags = problem.get('tags')
            if isinstance(tags, str):
                try:
                    problem['tags'] = json.loads(tags)
                except Exception:
                    problem['tags'] = []
            problem['is_public'] = bool(problem.get('is_public'))
            for date_field in ['created_at', 'updated_at']:
                raw_value = problem.get(date_field)
                localized = to_ist(raw_value)
                problem[f'{date_field}_display'] = format_ist(raw_value)
                problem[f'{date_field}_iso'] = localized.isoformat() if localized else ''
                problem[date_field] = localized
            problems.append(problem)

        return {
            'items': problems,
            'total': total,
            'page': page,
            'has_next': (page * limit) < total
        }

    def list_all_users(self, page: int = 1, limit: int = 20, search: Optional[str] = None) -> Dict[str, Any]:
        """List all users for admin view with problem/submission counts"""
        offset = max(0, (page - 1) * limit)
        params: List[Any] = []
        base_where = "WHERE 1=1"
        if search:
            like = f"%{search}%"
            base_where += " AND (u.name LIKE ? OR u.email LIKE ?)"
            params.extend([like, like])

        query = f"""
            SELECT u.*, 
                   (SELECT COUNT(*) FROM problems p WHERE p.author_id = u.id) AS problem_count,
                   (SELECT COUNT(*) FROM submissions s WHERE s.user_id = u.id) AS submission_count,
                   IFNULL(u.picture_url, '') AS picture_url
            FROM users u
            {base_where}
            ORDER BY u.created_at DESC
            LIMIT ? OFFSET ?
        """
        count_query = f"SELECT COUNT(*) FROM users u {base_where}"

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            items = conn.execute(query, params + [limit, offset]).fetchall()
            total = conn.execute(count_query, params).fetchone()[0]

        users: List[Dict[str, Any]] = []
        for row in items:
            user = self._normalize_user_row(row)
            users.append(user)

        return {
            'items': users,
            'total': total,
            'page': page,
            'has_next': (page * limit) < total
        }

    def list_all_submissions(self, page: int = 1, limit: int = 20, search: Optional[str] = None) -> Dict[str, Any]:
        """List submissions across all users for admin view"""
        offset = max(0, (page - 1) * limit)
        params: List[Any] = []
        base_where = "WHERE 1=1"
        if search:
            like = f"%{search}%"
            base_where += (" AND (s.problem_slug LIKE ? OR IFNULL(s.verdict,'') LIKE ? OR IFNULL(s.language,'') LIKE ? \n                           OR IFNULL(u.name,'') LIKE ? OR IFNULL(u.email,'') LIKE ? OR IFNULL(p.title,'') LIKE ?)")
            params.extend([like, like, like, like, like, like])

        query = f"""
            SELECT s.*, u.name AS user_name, u.email AS user_email, u.picture_url AS user_picture, p.title AS problem_title
            FROM submissions s
            LEFT JOIN users u ON s.user_id = u.id
            LEFT JOIN problems p ON s.problem_slug = p.slug
            {base_where}
            ORDER BY s.created_at DESC
            LIMIT ? OFFSET ?
        """
        count_query = f"""
            SELECT COUNT(*)
            FROM submissions s
            LEFT JOIN users u ON s.user_id = u.id
            LEFT JOIN problems p ON s.problem_slug = p.slug
            {base_where}
        """

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            items = conn.execute(query, params + [limit, offset]).fetchall()
            total = conn.execute(count_query, params).fetchone()[0]

        submissions: List[Dict[str, Any]] = []
        for row in items:
            submission = dict(row)
            submission['created_display'] = format_ist(submission.get('created_at'))
            submission['created_at_ist'] = to_ist_iso(submission.get('created_at'))
            submission['updated_display'] = format_ist(submission.get('updated_at'))
            submission['updated_at_ist'] = to_ist_iso(submission.get('updated_at'))
            submissions.append(submission)

        return {
            'items': submissions,
            'total': total,
            'page': page,
            'has_next': (page * limit) < total
        }

    def get_admin_stats(self) -> Dict[str, Any]:
        """Compute aggregate statistics for admin dashboard"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            total_problems = conn.execute("SELECT COUNT(*) FROM problems").fetchone()[0]
            public_problems = conn.execute("SELECT COUNT(*) FROM problems WHERE is_public = 1").fetchone()[0]
            private_problems = total_problems - public_problems
            total_submissions = conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0]
            running_submissions = conn.execute("SELECT COUNT(*) FROM submissions WHERE status = 'running'").fetchone()[0]
        return {
            'total_users': total_users,
            'total_problems': total_problems,
            'public_problems': public_problems,
            'private_problems': private_problems,
            'total_submissions': total_submissions,
            'running_submissions': running_submissions
        }
