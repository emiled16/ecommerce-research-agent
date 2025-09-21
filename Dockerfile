FROM python:3.13-slim as backend-builder

WORKDIR /app

COPY pyproject.toml poetry.lock poetry.toml ./

COPY src ./src

RUN pip install poetry && touch README.md && poetry install

EXPOSE 8000

CMD ["poetry", "run", "start-api"]