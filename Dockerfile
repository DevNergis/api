FROM ghcr.io/astral-sh/uv:alpine

WORKDIR /app

COPY . .

RUN uv sync --frozen --no-cache

EXPOSE 8000
CMD ["uv", "run", "fastapi", "run"]
