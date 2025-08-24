run:
		@echo "Starting fastapi"
		fastapi dev src/main.py --host 0.0.0.0
celery:
		@echo "Starting celery"
		celery -A src.config.celery worker --beat --loglevel=INFO
arq:
		@echo "Starting arq"
		arq src.config.arq.WorkerSettings

dramatiq:
		@echo "Starting dramatiq"
		dramatiq src.tasks
test:
	@echo "Starting testing"
	pytest -v
seed:
	PYTHONPATH=./src python -m  src.seed.script
migration:
	@echo "Creating migration"
	MIGRATION_NAME=$(name) alembic revision -m "$(msg)" --rev-id $(shell date -u +%Y%m%d_%H%M%S)
migrate:
	@echo "Migrating the migrations to the database"
	alembic upgrade head
downgrade:
	@echo "Migrating the migrations to the database"
	alembic downgrade -1
