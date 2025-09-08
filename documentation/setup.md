# Development Setup

## Prerequisites

- Python 3.13+
- uv (Python package manager)
- Azure account (for database and AI models)
- Docker (optional, for containerized deployment)

## Environment Configuration

### Required Environment Variables

Create a `.env` file in the project root with the following settings:

```bash
# Database
AZURE_DB_SERVER=your-server.database.windows.net
AZURE_DB_DATABASE=your-database

# AI Models (at least one required)
GEMINI_API_KEY=your-gemini-key
AZURE_OPENAI_API_KEY=your-openai-key
AZURE_OPENAI_ENDPOINT=your-openai-endpoint

# Email Service
EMAIL_HOST=smtp.your-provider.com
EMAIL_PORT=587
EMAIL_USE_SSL=true
EMAIL_USERNAME=your-username
EMAIL_PASSWORD=your-password

# Azure Authentication (optional - can use Azure CLI instead)
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret

# Observability (optional)
LANGSMITH_TRACING=false
LANGSMITH_API_KEY=your-langsmith-key
LANGSMITH_PROJECT=ai-analyst
```

## Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd ai-analyst
   ```

2. **Install dependencies**

   ```bash
   uv sync
   ```

3. **Setup database**
   - Create Azure SQL database
   - Run database migrations (if any)
   - Update connection string in `.env`

4. **Verify setup**

   ```bash
   uv run python -c "from src.configuration.settings import app_settings; print('Config loaded successfully')"
   ```

## Running the Application

### Development Mode

**Frontend (Web UI)**:

```bash
uv run fastapi dev frontend_main.py
```

Access at: <http://localhost:8000>

**Agent (Background Processing)**:

```bash
uv run python agent_main.py
```

### Production Mode

**Using Docker**:

```bash
docker-compose up
```

**Direct Python**:

```bash
uv run fastapi run frontend_main.py --host 0.0.0.0 --port 8000
```

## Testing

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/agents/test_report_graph.py

# Run with coverage
uv run pytest --cov=src
```

## Development Tips

- **Prompts**: Located in `src/agents/prompts/` - uses Jinja2 templates
- **Configuration Database Models**: Defined in `src/configuration/db_models.py`
- **Settings**: Managed via Pydantic Settings in `src/configuration/settings.py`
- **Logging**: Configured in `src/configuration/logger.py`
- **Authentication**: Azure Identity integration in `src/configuration/auth.py`
