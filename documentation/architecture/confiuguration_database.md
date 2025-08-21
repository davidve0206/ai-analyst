# Configuration Database Schema

## Overview

The application uses Azure SQL Database to store report configurations, user data, and execution history.

## Key Models

### SalesReportRequest
Core entity representing a report generation request.

**Fields:**
- `id`: Primary key
- `name`: Report name/description
- `kpi_type`: Type of KPI to analyze
- `filter_criteria`: JSON field for filtering data
- `recipients`: List of email recipients
- `schedule`: Cron expression for automated execution
- `created_at`: Timestamp
- `updated_at`: Timestamp

### Recipient
Email recipient information linked to report requests.

**Fields:**
- `id`: Primary key
- `name`: Recipient name
- `email`: Email address
- `report_request_id`: Foreign key to SalesReportRequest

## Database Configuration

### Connection
- **Driver**: Azure SQL Database
- **Authentication**: Azure Identity (DefaultAzureCredential)
- **ORM**: SQLAlchemy with async support
- **Connection Pool**: Managed by SQLAlchemy

### Settings
Configuration managed through environment variables:
- `AZURE_DB_SERVER`: Database server URL
- `AZURE_DB_DATABASE`: Database name
- `AZURE_DB_CONNECTION_TIMEOUT`: Connection timeout (default: 30s)

## Database Service

### `db_service.py`
Provides database operations:
- Connection management
- CRUD operations for models
- Transaction handling
- Connection pooling

### Key Functions
- `get_session()`: Async database session
- `create_report_request()`: Create new report
- `get_report_requests()`: Retrieve reports
- `update_report_status()`: Update execution status

## Migration Strategy

- Database schema managed through SQLAlchemy models
- No formal migration system currently implemented
- Schema changes require manual database updates

## Local Development

For local development without Azure SQL:
- SQLite support can be added for testing
- Connection string modification in settings
- Mock data services for offline development
