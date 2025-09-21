#!/usr/bin/env python3
"""
Script to delete all submissions from PocketOJ database
Use this for testing or cleanup purposes
"""

from core.config import config
from core.database import DatabaseManager
import os
import sys
import sqlite3
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def clear_all_submissions():
    """Delete all submissions from the database"""

    # Get database path
    db_path = config.get('database.path', 'pocketoj.db')

    # Check if database exists
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False

    try:
        # Connect to database
        with sqlite3.connect(db_path) as conn:
            # Check current submission count
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM submissions")
            count_before = cursor.fetchone()[0]

            if count_before == 0:
                print("✅ No submissions found in database")
                return True

            print(f"📊 Found {count_before} submissions in database")

            # Confirm deletion
            response = input(
                f"⚠️  Are you sure you want to delete all {count_before} submissions? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("❌ Operation cancelled")
                return False

            # Delete all submissions
            cursor.execute("DELETE FROM submissions")
            deleted_count = cursor.rowcount

            # Verify deletion
            cursor.execute("SELECT COUNT(*) FROM submissions")
            count_after = cursor.fetchone()[0]

            print(f"✅ Successfully deleted {deleted_count} submissions")
            print(f"📊 Submissions remaining: {count_after}")

            return True

    except Exception as e:
        print(f"❌ Error clearing submissions: {e}")
        return False


def clear_submissions_by_user(user_email: str):
    """Delete submissions for a specific user"""

    db_path = config.get('database.path', 'pocketoj.db')

    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Find user by email
            cursor.execute(
                "SELECT id, name FROM users WHERE email = ?", (user_email,))
            user = cursor.fetchone()

            if not user:
                print(f"❌ User not found: {user_email}")
                return False

            user_id, user_name = user

            # Count user's submissions
            cursor.execute(
                "SELECT COUNT(*) FROM submissions WHERE user_id = ?", (user_id,))
            count = cursor.fetchone()[0]

            if count == 0:
                print(
                    f"✅ No submissions found for user: {user_name} ({user_email})")
                return True

            print(
                f"📊 Found {count} submissions for user: {user_name} ({user_email})")

            # Confirm deletion
            response = input(
                f"⚠️  Delete all {count} submissions for {user_name}? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("❌ Operation cancelled")
                return False

            # Delete user's submissions
            cursor.execute(
                "DELETE FROM submissions WHERE user_id = ?", (user_id,))
            deleted_count = cursor.rowcount

            print(
                f"✅ Successfully deleted {deleted_count} submissions for {user_name}")
            return True

    except Exception as e:
        print(f"❌ Error clearing user submissions: {e}")
        return False


def clear_submissions_by_problem(problem_slug: str):
    """Delete submissions for a specific problem"""

    db_path = config.get('database.path', 'pocketoj.db')

    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Count problem's submissions
            cursor.execute(
                "SELECT COUNT(*) FROM submissions WHERE problem_slug = ?", (problem_slug,))
            count = cursor.fetchone()[0]

            if count == 0:
                print(f"✅ No submissions found for problem: {problem_slug}")
                return True

            print(f"📊 Found {count} submissions for problem: {problem_slug}")

            # Confirm deletion
            response = input(
                f"⚠️  Delete all {count} submissions for {problem_slug}? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("❌ Operation cancelled")
                return False

            # Delete problem's submissions
            cursor.execute(
                "DELETE FROM submissions WHERE problem_slug = ?", (problem_slug,))
            deleted_count = cursor.rowcount

            print(
                f"✅ Successfully deleted {deleted_count} submissions for {problem_slug}")
            return True

    except Exception as e:
        print(f"❌ Error clearing problem submissions: {e}")
        return False


def show_submission_stats():
    """Show submission statistics"""

    db_path = config.get('database.path', 'pocketoj.db')

    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Total submissions
            cursor.execute("SELECT COUNT(*) FROM submissions")
            total = cursor.fetchone()[0]

            # By verdict
            cursor.execute("""
                SELECT verdict, COUNT(*) 
                FROM submissions 
                WHERE verdict IS NOT NULL 
                GROUP BY verdict 
                ORDER BY COUNT(*) DESC
            """)
            verdicts = cursor.fetchall()

            # By user
            cursor.execute("""
                SELECT u.name, u.email, COUNT(*) as submission_count
                FROM submissions s
                JOIN users u ON s.user_id = u.id
                GROUP BY s.user_id
                ORDER BY submission_count DESC
                LIMIT 5
            """)
            top_users = cursor.fetchall()

            # By problem
            cursor.execute("""
                SELECT problem_slug, COUNT(*) as submission_count
                FROM submissions
                GROUP BY problem_slug
                ORDER BY submission_count DESC
                LIMIT 5
            """)
            top_problems = cursor.fetchall()

            print("📊 SUBMISSION STATISTICS")
            print("=" * 50)
            print(f"Total Submissions: {total}")

            if verdicts:
                print("\n🏆 By Verdict:")
                for verdict, count in verdicts:
                    print(f"  {verdict}: {count}")

            if top_users:
                print("\n👥 Top Users:")
                for name, email, count in top_users:
                    print(f"  {name} ({email}): {count}")

            if top_problems:
                print("\n🧩 Top Problems:")
                for slug, count in top_problems:
                    print(f"  {slug}: {count}")

    except Exception as e:
        print(f"❌ Error getting statistics: {e}")


def main():
    """Main function with menu"""
    print("🗑️  PocketOJ Submission Cleanup Tool")
    print("=" * 40)
    print("1. Delete ALL submissions")
    print("2. Delete submissions by user email")
    print("3. Delete submissions by problem slug")
    print("4. Show submission statistics")
    print("5. Exit")

    while True:
        try:
            choice = input("\nEnter your choice (1-5): ").strip()

            if choice == '1':
                clear_all_submissions()
            elif choice == '2':
                email = input("Enter user email: ").strip()
                if email:
                    clear_submissions_by_user(email)
            elif choice == '3':
                slug = input("Enter problem slug: ").strip()
                if slug:
                    clear_submissions_by_problem(slug)
            elif choice == '4':
                show_submission_stats()
            elif choice == '5':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-5.")

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == '__main__':
    main()
