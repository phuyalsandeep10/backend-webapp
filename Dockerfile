FROM python:3.13-slim

WORKDIR /code

COPY pyproject.toml .
COPY uv.lock .

RUN pip install uv 
RUN uv pip install --system .

COPY ./src ./src
COPY ./src/main.py ./src/main.py

COPY start.sh /start.sh
RUN chmod +x /start.sh
CMD ["/bin/sh", "/start.sh"]
