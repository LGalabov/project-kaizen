FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project

COPY src/ ./src/

# Install project in production mode
RUN uv sync --frozen

# Use system Python since container is already isolated
ENV UV_PROJECT_ENVIRONMENT=/usr/local

ENV MCP_TRANSPORT=http
ENV MCP_HTTP_HOST=0.0.0.0

EXPOSE 5453
CMD ["uv", "run", "kaizen-mcp"]
