FROM ghcr.io/astral-sh/uv:python3.13-alpine@sha256:6bef08ad40f8062d86a6be6b853e85563d6db8885eb2ba853308b4bb07b1270b

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
