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
    curl -sSL -O https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    rm packages-microsoft-prod.deb && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=deps /app/.venv /app/.venv
COPY . .
RUN uv sync --frozen --no-dev
ENV PATH="/app/.venv/bin:$PATH"
CMD ["streamlit", "run", "frontend_main.py", "--server.address", "0.0.0.0"]