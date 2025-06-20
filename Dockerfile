# Stage 1: deps only
FROM ghcr.io/astral-sh/uv:0.7.13-python3.13-bookworm AS deps
WORKDIR /app
COPY uv.lock pyproject.toml ./
RUN uv sync --frozen --no-install-project --no-dev

# Stage 2: app with cached deps
FROM ghcr.io/astral-sh/uv:0.7.13-python3.13-bookworm
# Install cron and ODBC Driver 18 for SQL Server
RUN apt-get update && \
    apt-get install -y curl gnupg apt-transport-https ca-certificates unixodbc-dev && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=deps /app/.venv /app/.venv
COPY . .
RUN uv sync --frozen --no-dev
ENV PATH="/app/.venv/bin:$PATH"
CMD ["gradio", "frontend_main.py"]