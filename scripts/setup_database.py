"""
Setup Database Schema

Run this script to create/update database tables automatically.
This is an alternative to manually running db_schema.sql in Supabase.

Usage:
    python scripts/setup_database.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_supabase_client

def setup_database():
    """Create database tables by running SQL schema."""

    print("=" * 60)
    print("AR PLATFORM - DATABASE SETUP")
    print("=" * 60)
    print()

    # Read SQL schema file
    schema_file = Path(__file__).parent.parent / 'config' / 'db_schema.sql'

    try:
        with open(schema_file, 'r', encoding='utf-8') as f:
            sql_schema = f.read()
    except FileNotFoundError:
        print(f"ERROR: Schema file not found: {schema_file}")
        return False

    print(f"Loaded schema from: {schema_file}")
    print(f"SQL size: {len(sql_schema)} characters")
    print()

    # Get Supabase client
    try:
        supabase = get_supabase_client()
        print("Supabase client connected successfully")
    except Exception as e:
        print(f"ERROR: Failed to connect to Supabase: {e}")
        return False

    print()
    print("IMPORTANT:")
    print("-" * 60)
    print("The Python Supabase client doesn't support raw SQL execution.")
    print("You need to run the SQL schema manually in Supabase dashboard.")
    print()
    print("STEPS:")
    print("1. Go to: https://supabase.com/dashboard")
    print("2. Click your project")
    print("3. Go to 'SQL Editor' in left sidebar")
    print("4. Click 'New Query'")
    print("5. Copy the ENTIRE contents of this file:")
    print(f"   {schema_file}")
    print("6. Paste into the SQL editor")
    print("7. Click 'Run' (or press Ctrl+Enter)")
    print("8. Wait for success message")
    print()
    print("Alternative:")
    print("I'll show you the SQL content below - you can copy it directly:")
    print("-" * 60)
    print()

    # Ask user if they want to see the SQL
    response = input("Show SQL schema for copy-paste? (y/n): ").strip().lower()

    if response == 'y':
        print()
        print("=" * 60)
        print("SQL SCHEMA (COPY EVERYTHING BELOW)")
        print("=" * 60)
        print()
        print(sql_schema)
        print()
        print("=" * 60)
        print("END OF SQL SCHEMA")
        print("=" * 60)
        print()
        print("Copy everything above (from CREATE TABLE to the end)")
        print("Then paste in Supabase SQL Editor and click Run")

    return True


if __name__ == '__main__':
    setup_database()
