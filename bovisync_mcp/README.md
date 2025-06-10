# Bovisync MCP Server

A Model Context Protocol (MCP) server for the Bovisync API, providing access to dairy farm animal management, events, and milk production data.

## Overview

This MCP server implements a complete interface to the Bovisync API, allowing you to:

- **Authentication**: OAuth2 token management
- **Session Management**: Set and manage active herds
- **Animal Management**: List animals, get animal data, bulk operations
- **Event Management**: Track breeding, health, and other farm events
- **Milk Data**: Access DHI test results and parlor production data
- **Reporting**: Generate animal reports and analytics

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables (optional):
```bash
export BOVISYNC_CLIENT_ID="your_client_id"
export BOVISYNC_CLIENT_SECRET="your_client_secret"
export BOVISYNC_API_URL="https://api.bovisync.com"
```

## Running the Server

### Quick Start
```bash
./start_server.sh
```

### Manual Start
```bash
python3 server.py --client-id YOUR_ID --client-secret YOUR_SECRET
```

### Command Line Options
- `--host`: Host to bind to (default: localhost)
- `--port`: Port to bind to (default: 8002)
- `--bovisync-url`: Bovisync API base URL
- `--client-id`: Bovisync API client ID
- `--client-secret`: Bovisync API client secret

## Using the Client

### Interactive Mode
```bash
python3 client.py --interactive
```

### Execute Single Operation
```bash
python3 client.py --operation list_animals --parameters '{"limit": 50}'
```

### Available Operations

#### Authentication & Session
- `get_token` - Get OAuth access token
- `get_active_herd` - Get current active herd
- `set_active_herd` - Set active herd for session
- `get_user_herds` - List accessible herds

#### Animal Management
- `list_animals` - List animals in herd
  - Parameters: `limit`, `offset`, `search`, `active_only`
- `get_animal_data` - Get animal report data
  - Parameters: `animal_id`, `report_items`, `date_from`, `date_to`
- `get_animal_bulk` - Bulk animal data export
  - Parameters: `limit`, `offset`, `modified_since`

#### Event Management
- `list_events` - List farm events
  - Parameters: `limit`, `offset`, `event_type`, `animal_id`, `date_from`, `date_to`
- `get_event_meta` - Get event type information
  - Parameters: `event_type_id`
- `get_event_bulk` - Bulk event data for month
  - Parameters: `year`, `month`, `event_type`

#### Milk Data
- `get_milk_test_data` - DHI milk test results
  - Parameters: `limit`, `offset`, `animal_id`, `test_date_from`, `test_date_to`
- `get_parlor_daily_data` - Daily parlor production
  - Parameters: `limit`, `offset`, `date_from`, `date_to`, `animal_id`

#### Reporting
- `get_report_animal_data` - Animal report data
  - Parameters: `animal_id`, `report_items`, `date_from`, `date_to`

## API Examples

### List Animals
```bash
curl -X POST http://localhost:8002/execute \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "list_animals",
    "parameters": {
      "limit": 50,
      "active_only": true
    }
  }'
```

### Get Animal Data
```bash
curl -X POST http://localhost:8002/execute \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "get_animal_data",
    "parameters": {
      "animal_id": "12345",
      "report_items": "milk,reproduction",
      "date_from": "2024-01-01",
      "date_to": "2024-12-31"
    }
  }'
```

### List Events
```bash
curl -X POST http://localhost:8002/execute \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "list_events",
    "parameters": {
      "event_type": "breeding",
      "date_from": "2024-01-01",
      "limit": 100
    }
  }'
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BOVISYNC_CLIENT_ID` | OAuth client ID | None |
| `BOVISYNC_CLIENT_SECRET` | OAuth client secret | None |
| `BOVISYNC_API_URL` | Bovisync API base URL | https://api.bovisync.com |
| `BOVISYNC_HOST` | Server host | localhost |
| `BOVISYNC_PORT` | Server port | 8002 |

### OAuth Scopes

The server requests the following OAuth scopes:
- `animal:read` - Access to animal data
- `event:read` - Access to event data  
- `milktest:read` - Access to milk test data
- `parlor:read` - Access to parlor data
- `data:read` - Access to report data

## Health Check

Check server status:
```bash
curl http://localhost:8002/health
```

Response includes:
- Server health status
- Bovisync API connection status
- Active herd information
- Timestamp

## Error Handling

The server provides detailed error messages for:
- Authentication failures
- API connection issues
- Invalid parameters
- Rate limiting
- Permission errors

## Development

### Project Structure
```
bovisync_mcp/
├── __init__.py          # Package initialization
├── server.py            # Main MCP server
├── client.py            # MCP client and CLI
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── start_server.sh      # Server startup script
└── README.md           # This file
```

### Adding New Operations

1. Add endpoint definition to `self.endpoints` in `BovisyncMCPServer.__init__()`
2. Include required parameters and OAuth scope
3. The server automatically handles request routing and authentication

### Testing

Test server connectivity:
```bash
python3 client.py --health
```

Test specific operations:
```bash
python3 client.py --operation get_user_herds
```

## License

Generated with Claude Code for Bovisync API integration.

## Support

For Bovisync API documentation and support, visit: https://bovisync.com/api-docs