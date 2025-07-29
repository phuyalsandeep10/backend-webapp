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


