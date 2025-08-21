# AI Analyst

AI Analyst is a financial analysis system that generates automated sales reports using AI agents. The system processes financial data, performs research, and produces PDF reports that can be scheduled and emailed to recipients.

## Quick Start

```bash
# Install dependencies
uv sync

# Run frontend
uv run fastapi dev frontend_main.py

# Run agent
uv run python agent_main.py
```

## Architecture

### Core Components

- **Agent System**: LangGraph-based AI agents that handle data analysis, research, and report generation
- **Frontend**: FastAPI web application for report configuration and scheduling
- **Email Service**: Automated delivery of generated reports

### Key Technologies

- **Framework**: LangGraph
- **Frontend**: FastAPI + Jinja Templates
- **Database**: Azure SQL (optional)
- **AI Models**: Support for Gemini, Azure OpenAI, and Azure Foundry
- **Authentication**: Azure Identity
- **Observability**: LangSmith (optional)

### Agent Workflow

Reports are generated through a multi-step AI agent process:
Research → Data Analysis → Report Generation (Inc. Visualizations) → Review

Execution can be scheduled via cron jobs.

### Data Sources

- Internal financial data (CSV files in `/data/`)
- Potentially - Database queries (Azure SQL); code exists but we don't have a database

### Output

- Markdown reports converted to PDF and stored locally
- Automated email delivery

## Project Structure

```text
src/
├── agents/           # AI agents and graph workflows
├── configuration/     # Settings, auth
└── frontend/         # Web UI and API routes for configuration

agent_main.py         # Main agent execution entry point
frontend_main.py      # FastAPI application entry point
data/                 # Provided datasets
outputs/              # Generated reports
```

## Configuration

Configuration is managed through environment variables in `.env` file:

### Essential Settings

- AI model keys (`GEMINI_API_KEY`, `AZURE_OPENAI_*`)
- Azure authentication (`AZURE_TENANT_ID`, etc.)
- Email configuration (`EMAIL_*`)

### Optional Settings

- Database connection (`AZURE_DB_*`) - currently not required
- Observability (`LANGSMITH_TRACING`, `LANGSMITH_API_KEY`)

## Documentation

For detailed documentation, see the `/documentation` folder:

- **[Development Setup](documentation/setup.md)** - Detailed installation and configuration
- **[Agent System](documentation/architecture/agents.md)** - Multi-agent AI system architecture
- **[Database Schema](documentation/architecture/database.md)** - Data models and database design
- **[API Reference](documentation/api.md)** - REST endpoints and usage examples
- **[Deployment Guide](documentation/deployment.md)** - Production deployment instructions

## Development Notes

### Testing

The `tests/` folder includes both unit tests and agent evaluations. Some evaluations are fully automated while others require human evaluation.

### Authentication

Azure Identity integration allows flexible authentication methods (environment variables, CLI, managed identity, etc.).
