#!/usr/bin/env python3

import argparse
import subprocess
from datetime import datetime
import sys
import os
import re

def pascal_to_snake(name):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

def run_fastapi():
    print("Starting FastAPI with uvicorn")
    subprocess.run([
        "uvicorn",
        "src.main:socket_app",  # This is the module:app path
        "--host", "127.0.0.1",
        "--port", "8000",
        "--reload"
    ], check=True)

def run_celery():
    print("Starting celery")
    subprocess.run(["celery", "-A", "src.config.celery", "worker", "--loglevel=INFO"], check=True)

def run_tests():
    print("Starting testing")
    subprocess.run(["pytest", "-v"], check=True)

def run_seed():
    print("Running seed script")
    subprocess.run(["python", "src/seed.py"], env={**os.environ, "PYTHONPATH": "./src"}, check=True)


def sanitize_name(name):
    arr = name.split()
    names = []
    for name in arr:
        names.append(name.capitalize())
    print(names)        
    return "".join(names)
    

def make_migration(name, msg):
    print("Creating migration")
    os.environ.setdefault("MIGRATION_NAME", name.capitalize())
    rev_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    if not name:
        print("Please provide a migration name")
        sys.exit(1)

    # Convert to snake_case
    sanitizeName =  sanitize_name(name)
    snake_name = pascal_to_snake(name)

    # Set default message if not providedsss
    msg = msg or f"Add {sanitizeName} table"    
    # Export to env var (optional usage)s
    os.environ["MIGRATION_NAME"] = sanitizeName
    os.environ["MIGRATION_FILE_NAME"] = snake_name  

    rev_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    print(f"→ Migration class: {sanitizeName}")
    print(f"→ Filename: {snake_name}")
    print(f"→ Message: {msg}")      
    print(f"→ Revision ID: {rev_id}")

    command = [
        "alembic", "revision",
        "-m", msg,
        "--rev-id", rev_id
    ]
    subprocess.run(command, check=True)

def migrate():
    print("Migrating the migrations to the database")
    subprocess.run(["alembic", "upgrade", "head"], check=True)

def downgrade():    
    print("Downgrading the last migration")
    subprocess.run(["alembic", "downgrade", "-1"], check=True)

def main():
    parser = argparse.ArgumentParser(description="Manage.py replacement for Makefile")
    subparsers = parser.add_subparsers(dest="command", required=True)

    

    subparsers.add_parser("run", help="Start FastAPI server")
    subparsers.add_parser("celery", help="Start Celery worker")
    subparsers.add_parser("test", help="Run tests")
    subparsers.add_parser("seed", help="Run seeder script")
    subparsers.add_parser("migrate", help="Apply all migrations")
    subparsers.add_parser("downgrade", help="Revert last migration")

    migration_parser = subparsers.add_parser("migration", help="Create new migration")
    migration_parser.add_argument("--name", required=True, help="Migration name (not used)")
    migration_parser.add_argument("--msg", required=False, help="Migration message")

    args = parser.parse_args()

    match args.command:
        case "run":
            run_fastapi()
        case "celery":
            run_celery()
        case "test":
            run_tests()
        case "seed":
            run_seed()
        case "migration":
            make_migration(args.name, args.msg)
        case "migrate":
            migrate()
        case "downgrade":
            downgrade()

if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        sys.exit(1)
