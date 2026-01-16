"""
Setup Supabase Test Schema

Creates required tables for testing in local Supabase instance.

Run this script once before running tests to ensure Supabase has the required schema.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import os
import asyncio
from symphainy_platform.foundations.public_works.adapters.supabase_adapter import SupabaseAdapter

# Test Supabase configuration
TEST_SUPABASE_URL = os.getenv("TEST_SUPABASE_URL", "http://localhost:3001")
TEST_SUPABASE_ANON_KEY = os.getenv("TEST_SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0")
TEST_SUPABASE_SERVICE_KEY = os.getenv("TEST_SUPABASE_SERVICE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU")


async def setup_test_schema():
    """Create required tables in Supabase test instance."""
    adapter = SupabaseAdapter(
        url=TEST_SUPABASE_URL,
        anon_key=TEST_SUPABASE_ANON_KEY,
        service_key=TEST_SUPABASE_SERVICE_KEY
    )
    
    # Read migration script
    migration_file = project_root / "scripts" / "migrations" / "001_create_insights_lineage_tables.sql"
    
    if not migration_file.exists():
        print(f"⚠️  Migration file not found: {migration_file}")
        print("   Skipping schema setup. Tables may need to be created manually.")
        return
    
    with open(migration_file, "r") as f:
        migration_sql = f.read()
    
    # Execute migration
    try:
        print("📝 Creating Supabase test schema...")
        result = await adapter.execute_sql(migration_sql)
        print("✅ Supabase test schema created successfully!")
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        print("   This may be expected if tables already exist.")


if __name__ == "__main__":
    asyncio.run(setup_test_schema())
