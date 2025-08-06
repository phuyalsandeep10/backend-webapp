uvicorn src.main:socket_app --host 127.0.0.1 --port 8000 --reload
celery -A your_project worker -l DEBUG -P solo



celery -A src.config.celery worker -l DEBUG -P solo


alembic revision --autogenerate -m "create users table"



alembic revision -m "create table"
make migration name=add_users_table msg="Add users table migration"


alembic upgrade head

alembic downgrade -1

#ahh
#deploy