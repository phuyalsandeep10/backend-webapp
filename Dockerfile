FROM python:3.13-slim

WORKDIR /code

COPY pyproject.toml .
COPY uv.lock .
COPY . .

RUN pip install uv
RUN uv pip install --system .

COPY ./src ./src


CMD ["/bin/sh", "./start.sh"]
