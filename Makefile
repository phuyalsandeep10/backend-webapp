run:
		@echo "Starting fastapi"
		fastapi dev src/main.py
celery:
		@echo "Starting celery"
		celery -A src.config.celery worker --loglevel=INFO
test:
	@echo "Starting testing"
	pytest -v
seed:
	PYTHONPATH=./src python src/seed.py
migration:
	@echo "Creating migration"
	MIGRATION_NAME=$(name) alembic revision -m "$(msg)" --rev-id $(shell date -u +%Y%m%d_%H%M%S)
migrate:
	@echo "Migrating the migrations to the database"
	alembic upgrade head
downgrade:
	@echo "Migrating the migrations to the database"
	alembic downgrade -1
