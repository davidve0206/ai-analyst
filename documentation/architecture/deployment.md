# Deployment Guide

## Production Deployment

### Docker Deployment (Recommended)

**Prerequisites:**
- Docker and Docker Compose
- AI API keys (Gemini/Azure OpenAI)
- SMTP server for email delivery

**Steps:**

1. **Environment Setup**
   Create `.env` file with production values:
   ```bash
   # Copy from .env.example and update
   cp .env.example .env
   ```

2. **Build and Deploy**
   ```bash
   docker-compose up -d
   ```

3. **Verify Deployment**
   ```bash
   # Check container status
   docker-compose ps
   
   # View logs
   docker-compose logs -f
   ```

### Manual Deployment

**For non-Docker environments:**

1. **Install Python 3.13+**
2. **Install uv package manager**
3. **Setup application**
   ```bash
   uv sync --no-dev
   source .venv/bin/activate
   ```

4. **Run application**
   ```bash
   # Frontend
   uv run fastapi run frontend_main.py --host 0.0.0.0 --port 8000
   
   # Background agent (separate process)
   uv run python agent_main.py
   ```

## Configuration

### Environment Variables

**Required in production:**

- AI model API keys
- Email server configuration
- Azure authentication

**Optional:**

- `LANGSMITH_TRACING=true` (for observability)
- Custom port settings
- Logging levels
- Database connection details

## Monitoring

### Logging

- Application logs: `logs/app.log`
- Structured logging with timestamps
- Error tracking and debugging info

### Health Checks - TODO

- Database connectivity
- AI model availability