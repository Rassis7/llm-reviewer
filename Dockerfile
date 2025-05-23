FROM python:3.12.4-slim

WORKDIR /app

ENV PYTHONPATH=/app
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VENV_IN_PROJECT=1
ENV POETRY_CACHE_DIR=/tmp/poetry_cache

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false && \
    poetry install --only=main --no-root && \
    rm -rf $POETRY_CACHE_DIR

COPY . .

EXPOSE 8501

CMD ["poetry", "run", "streamlit", "run", "llm_reviewer/streamlit/app.py", "--server.port=8501", "--server.address=0.0.0.0"]