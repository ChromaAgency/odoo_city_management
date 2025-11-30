# City Management FastAPI API

This module provides a modern REST API for the City Management system using FastAPI.

## Features

- **Reports API**: Get report information by name or phone number
- **Categories API**: Retrieve categories and subcategories by code
- **Chatbot Options API**: Get formatted category lists for chatbot integration
- **Citizen Intentions API**: Create citizen intentions
- **Webhooks API**: Handle external webhook integrations

## Installation

### Requirements

1. Install the `fastapi` addon from OCA/rest-framework:
   ```bash
   pip install odoo-addon-fastapi
   ```

2. Update your Odoo addons and install the `fastapi` module in your database.

3. Restart Odoo server.

## Configuration

### Create FastAPI Endpoint

1. Go to **Settings > Technical > FastAPI > Endpoints**
2. Create a new endpoint:
   - **Name**: City Management API
   - **App**: City Management API
   - **Root Path**: `/api/city_management`
   - **User**: Select a user with appropriate permissions
   - **Authentication**: Choose your preferred method

3. Save the endpoint.

### Access the API

- **API Documentation**: `http://your-odoo-server/api/city_management/docs`
- **OpenAPI Schema**: `http://your-odoo-server/api/city_management/openapi.json`

## API Endpoints

### Reports

#### Get Report by Name
```
GET /api/city_management/report/name/{name}
```
Returns report information including status, notes, and last update.

**Example Response:**
```json
{
  "result": {
    "name": "123ABC",
    "state": "En progreso",
    "note": "Trabajo en progreso",
    "last_change_date": "29/11/2025",
    "last_change_time": "10:30"
  }
}
```

#### Get Reports by Phone
```
GET /api/city_management/report/phone/{phone}
```
Returns all reports associated with a phone number as formatted messages.

### Categories

#### Get Category by Code
```
GET /api/city_management/categories/code/{code}
```
Returns category information by code.

#### Get Subcategory by Code
```
GET /api/city_management/categories/{category_id}/subcategories/code/{code}
```
Returns subcategory information within a parent category.

### Chatbot Options

#### Get Chatbot Categories
```
GET /api/city_management/chatbot_options/categories
```
Returns all parent categories formatted for chatbot display with navigation filters.

**Example Response:**
```json
{
  "result": "▶️ 1 - Water Services\n▶️ 2 - Street Maintenance\n▶️ 3 - Public Lighting",
  "filters": {
    "maxOption": 3,
    "minOption": 1
  }
}
```

#### Get Chatbot Subcategories
```
GET /api/city_management/chatbot_options/categories/{category_id}/subcategories
```
Returns subcategories for a parent category formatted for chatbot display with navigation filters.

**Example Response:**
```json
{
  "result": "▶️ 1 - Broken Pipe\n▶️ 2 - Low Pressure\n▶️ 3 - Water Quality",
  "filters": {
    "maxOption": 3,
    "minOption": 1
  }
}
```

### Citizen Intentions

#### Create Citizen Intention
```
POST /api/city_management/citizen_intention
```

**Request Body:**
```json
{
  "mobile": "+1234567890",
  "intention": "complaint",
  "detail": "Street light not working",
  "feeling": "frustrated"
}
```

### Webhooks

#### Process Webhook
```
POST /api/city_management/webhooks
```

**Supported Actions:**
- `CREATE_REPORT`: Create a new report
- `UPDATE_REPORT`: Update an existing report
- `LOG`: Log webhook data

**Request Body (CREATE_REPORT):**
```json
{
  "action": "CREATE_REPORT",
  "data": {
    "mobile": "+1234567890",
    "subcategory_id": 1,
    "note": "Report details",
    "neighbour": {
      "name": "John Doe",
      "email": "john@example.com"
    }
  }
}
```

**Request Body (UPDATE_REPORT):**
```json
{
  "action": "UPDATE_REPORT",
  "data": {
    "report_id": 123,
    "state": "in_progress",
    "note": "Updated status"
  }
}
```

## Architecture

The FastAPI integration follows this structure:

```
city_management/controller/fastapi/
├── __init__.py           # Module initialization
├── endpoints.py          # FastAPI endpoint model
├── schemas/              # Pydantic models
│   ├── __init__.py
│   ├── report.py
│   ├── category.py
│   ├── chatbot.py
│   ├── intention.py
│   └── webhook.py
└── routers/              # API route handlers
    ├── __init__.py
    ├── reports.py
    ├── categories.py
    ├── chatbot.py
    ├── intentions.py
    └── webhooks.py
```

## Development

### Adding New Endpoints

1. Create a new schema in `schemas/` if needed
2. Create a new router in `routers/`
3. Import and include the router in `routers/__init__.py`

### Testing

Use the interactive API documentation at `/docs` to test endpoints directly in your browser.

### Security

- All endpoints use the user configured in the FastAPI endpoint
- Consider creating a dedicated user with minimal required permissions
- Use appropriate authentication methods (API Key, HTTP Basic, etc.)

## Troubleshooting

### Import Errors

If you see import errors for `pydantic` or `fastapi`:
```bash
pip install fastapi pydantic
```

### Endpoint Not Found

Make sure:
1. The `fastapi` module is installed and activated
2. The FastAPI endpoint is created and configured
3. The server was restarted after installation

## References

- [FastAPI Odoo Documentation](https://github.com/OCA/rest-framework/tree/19.0/fastapi)
- [FastAPI Official Docs](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
