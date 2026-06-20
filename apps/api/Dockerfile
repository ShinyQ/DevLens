FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN mkdir -p src && pip install --no-cache-dir -e ".[dev]"

COPY . .

RUN mkdir -p /app/data

CMD ["uvicorn", "devlens.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
