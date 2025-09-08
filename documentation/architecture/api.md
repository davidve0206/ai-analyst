# API Reference

## FastAPI Endpoints

The frontend provides a REST API for managing sales reports and scheduling.

### Base URL
- Development: `http://localhost:8000`
- Production: Configured via environment

## Endpoints

### Home
- **GET** `/` - Main dashboard page
- **Response**: HTML page with report configuration overview

### Sales Reports

#### Create Report Request
- **POST** `/sales_report/create`
- **Body**: Report configuration JSON
- **Response**: Created report ID

#### List Reports
- **GET** `/sales_report/list`
- **Response**: Array of report configurations

#### Get Report Status
- **GET** `/sales_report/{report_id}/status`
- **Response**: Execution status and last run details

#### Update Report
- **PUT** `/sales_report/{report_id}`
- **Body**: Updated configuration
- **Response**: Success confirmation

#### Delete Report
- **DELETE** `/sales_report/{report_id}`
- **Response**: Deletion confirmation

### Scheduling (Crontab)

#### List Scheduled Jobs
- **GET** `/crontab/jobs`
- **Response**: Array of active cron jobs

#### Create Scheduled Job
- **POST** `/crontab/create`
- **Body**: Cron expression and report ID
- **Response**: Job creation confirmation

#### Update Schedule
- **PUT** `/crontab/{job_id}`
- **Body**: Updated cron expression
- **Response**: Update confirmation

#### Delete Schedule
- **DELETE** `/crontab/{job_id}`
- **Response**: Deletion confirmation

## Request/Response Examples

### Create Report Request
```json
{
  "name": "Q4 Sales Analysis",
  "kpi_type": "sales_revenue",
  "filter_criteria": {
    "region": "North America",
    "time_period": "Q4_2024"
  },
  "recipients": [
    {
      "name": "John Smith",
      "email": "john@company.com"
    }
  ]
}
```

### Schedule Report
```json
{
  "report_id": 123,
  "cron_expression": "0 9 * * MON",
  "description": "Weekly Monday morning report"
}
```

## Authentication

Currently uses Azure Identity for backend services. Frontend authentication not implemented - planned for future releases.

## Error Handling

Standard HTTP status codes:
- `200`: Success
- `400`: Bad Request (validation errors)
- `404`: Not Found
- `500`: Internal Server Error

Error responses include descriptive messages for debugging.
