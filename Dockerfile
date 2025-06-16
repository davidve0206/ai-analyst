# Stage 1: deps only
FROM ghcr.io/astral-sh/uv:0.7.13-python3.13-bookworm AS deps
WORKDIR /app
COPY uv.lock pyproject.toml ./
RUN uv sync --frozen --no-install-project --no-dev

# Stage 2: app with cached deps
FROM ghcr.io/astral-sh/uv:0.7.13-python3.13-bookworm
# Install cron to handle scheduled agent run
RUN apt-get update && \ 
    apt-get install -y cron \
    && apt-get clean
WORKDIR /app
COPY --from=deps /app/.venv /app/.venv
COPY . .
RUN uv sync --frozen --no-dev
ENV PATH="/app/.venv/bin:$PATH"
CMD ["gradio", "frontend_main.py"]