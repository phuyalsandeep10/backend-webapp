from invoke import task
import os
from datetime import datetime


@task
def run(ctx):
    print("Starting fastapi")
    ctx.run("fastapi dev src/main.py")


@task
def celery(ctx):
    print("Starting celery")
    ctx.run("celery -A src.config.celery worker --loglevel=INFO")


@task
def test(ctx):
    print("Starting testing")
    ctx.run("pytest -v")


@task
def seed(ctx):
    print("Running seed script")
    ctx.run("PYTHONPATH=./src python src/seed.py")


@task
def migration(ctx, name="", msg=""):
    if not name:
        print("Please provide --name and --msg arguments")
        return
    rev_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    os.environ.setdefault("MIGRATION_NAME", name.capitalize())

    print("Creating migration")
    alembicMessage = msg or name
    print(f"alembic Message {alembicMessage}")

    ctx.run(f'alembic revision -m "{alembicMessage}" --rev-id {rev_id}')


@task
def migrate(ctx):
    print("Migrating the migrations to the database")
    ctx.run("alembic upgrade head")


@task
def downgrade(ctx):
    print("Downgrading the last migration")
    ctx.run("alembic downgrade -1")
