# National Dairy Farm MCP Server

A **Model Context Protocol (MCP) Server** for the National Dairy FARM Program API. This server provides a standardized interface to interact with dairy farm management data, evaluations, and analytics through the National Dairy FARM Program's API.

## 🐄 Features

### **Core API Operations**
- **Cooperative Management**: Create, read, update, and list dairy cooperatives
- **Farm Management**: Complete CRUD operations for farm data and profiles
- **Facility Management**: Manage farm facilities and infrastructure
- **User Management**: Handle user accounts, roles, and permissions
- **Evaluation Workflow**: Create, manage, and submit farm evaluations
- **Life Cycle Analysis (LCA)**: Generate and manage environmental impact reports
- **Attachment Management**: Handle document uploads and management
- **Search & Analytics**: Advanced search and reporting capabilities

### **MCP Server Features**
- **OAuth2 Authentication**: Secure authentication with the Dairy Farm API
- **RESTful Interface**: Standard HTTP endpoints for MCP operations
- **Error Handling**: Comprehensive error handling and logging
- **Health Monitoring**: Built-in health checks and status monitoring
- **Configurable**: Environment-based configuration management

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- National Dairy Farm API credentials (client ID and secret)
- FastAPI and dependencies

### Installation

1. **Install dependencies:**
   ```bash
   cd dairy_farm_mcp
   pip install -r requirements.txt
   ```

2. **Configure credentials:**
   ```bash
   cp .env.example .env
   # Edit .env with your API credentials
   ```

3. **Start the MCP server:**
   ```bash
   python server.py --host localhost --port 8001
   ```

4. **Test the server:**
   ```bash
   python client.py --info
   ```

## 📋 Configuration

### Environment Variables

Create a `.env` file with your configuration:

```bash
# Required: Dairy Farm API Credentials
DAIRY_FARM_CLIENT_ID=your_client_id_here
DAIRY_FARM_CLIENT_SECRET=your_client_secret_here

# Optional: Server Configuration
DAIRY_FARM_MCP_SERVER_HOST=localhost
DAIRY_FARM_MCP_SERVER_PORT=8001
DAIRY_FARM_API_URL=https://eval.nationaldairyfarm.com/dfdm/api

# Optional: API Settings
DAIRY_FARM_API_TIMEOUT=30
DAIRY_FARM_API_VERSION=3.2
DAIRY_FARM_LOG_LEVEL=INFO
```

### Command Line Options

```bash
python server.py --help

options:
  --host HOST              Host to bind to (default: localhost)
  --port PORT              Port to bind to (default: 8001)
  --dairy-farm-url URL     Dairy Farm API base URL
  --client-id ID           Dairy Farm API client ID
  --client-secret SECRET   Dairy Farm API client secret
```

## 🔧 Usage

### Server Operations

**Start the server:**
```bash
python server.py --host 0.0.0.0 --port 8001
```

**Health check:**
```bash
curl http://localhost:8001/health
```

**List operations:**
```bash
curl http://localhost:8001/operations
```

### Client Usage

**Interactive mode:**
```bash
python client.py --interactive
```

**Show server info:**
```bash
python client.py --info
```

**Execute operation:**
```bash
python client.py --operation list_farms --parameters '{"page": 0, "size": 10}'
```

**Run demos:**
```bash
python demo.py --scenario all
```

## 📊 Available Operations

### **Cooperative Management**
- `list_coops` - List all cooperatives
- `get_coop` - Get specific cooperative details
- `create_coop` - Create new cooperative
- `update_coop` - Update cooperative information

### **Farm Management**
- `list_farms` - List all farms with filtering and pagination
- `get_farm` - Get specific farm details
- `create_farm` - Create new farm
- `update_farm` - Update farm information
- `delete_farm` - Delete farm

### **Evaluation Workflow**
- `list_evaluations` - List farm evaluations with filters
- `get_evaluation` - Get evaluation details
- `create_evaluation` - Create new evaluation
- `update_evaluation` - Update evaluation status and results
- `submit_evaluation` - Submit completed evaluation

### **Analytics & Reporting**
- `get_farm_analytics` - Get farm performance analytics
- `get_coop_analytics` - Get cooperative analytics
- `get_evaluation_trends` - Get evaluation trend analysis
- `search_farms` - Search farms using Solr
- `search_evaluations` - Search evaluations

### **Life Cycle Analysis**
- `list_lca_reports` - List LCA reports
- `get_lca_report` - Get LCA report details
- `create_lca_report` - Create new LCA report
- `update_lca_report` - Update LCA report

### **User & Facility Management**
- `list_users` - List system users
- `create_user` - Create new user
- `list_facilities` - List farm facilities
- `create_facility` - Create new facility

### **Attachments**
- `list_attachments` - List document attachments
- `upload_attachment` - Upload new attachment
- `delete_attachment` - Delete attachment

## 🎯 Example Operations

### Create a Farm
```python
await client.execute_operation("create_farm", {
    "name": "Green Valley Farm",
    "location": {
        "address": "123 Farm Road",
        "city": "Dairy City",
        "state": "WI",
        "zip": "12345"
    },
    "contact_info": {
        "owner": "John Farmer",
        "email": "john@greenvalley.com",
        "phone": "555-0123"
    },
    "coop_id": "coop_123"
})
```

### List Evaluations
```python
await client.execute_operation("list_evaluations", {
    "farm_id": "farm_456",
    "status": "completed",
    "date_from": "2024-01-01",
    "date_to": "2024-12-31",
    "page": 0,
    "size": 20
})
```

### Search Farms
```python
await client.execute_operation("search_farms", {
    "q": "organic",
    "filters": {"state": "WI", "certification": "organic"},
    "facets": ["state", "certification"],
    "page": 0,
    "size": 10
})
```

### Get Analytics
```python
await client.execute_operation("get_farm_analytics", {
    "farm_id": "farm_789",
    "metrics": ["milk_production", "animal_welfare", "environmental_impact"],
    "period": "last_year",
    "aggregation": "monthly"
})
```

## 🏗️ API Architecture

### Server Structure
```
dairy_farm_mcp/
├── server.py          # Main MCP server implementation
├── client.py          # MCP client and CLI tool
├── demo.py            # Demo scenarios and examples
├── config.py          # Configuration management
├── requirements.txt   # Python dependencies
├── .env.example       # Environment configuration template
└── README.md          # This documentation
```

### Authentication Flow
1. Server authenticates with Dairy Farm API using OAuth2 client credentials
2. Access token is cached and automatically refreshed
3. All API requests include the Bearer token
4. MCP clients authenticate with the server (optional)

### Error Handling
- Automatic token refresh on expiration
- Comprehensive HTTP error handling
- Detailed error messages and logging
- Graceful degradation for network issues

## 🔐 Security

### API Security
- OAuth2 client credentials flow
- Secure token storage and refresh
- HTTPS communication with Dairy Farm API
- Input validation and sanitization

### MCP Server Security
- Optional client authentication
- Rate limiting capabilities
- Comprehensive logging
- Error message sanitization

## 📈 Monitoring & Health

### Health Endpoints
- `GET /health` - Server health and API connectivity
- `GET /` - Server information and metrics
- `GET /operations` - Available operations list

### Logging
- Structured logging with timestamps
- Configurable log levels
- Request/response logging
- Error tracking and debugging

## 🧪 Testing

### Run Tests
```bash
# Test server connectivity
python client.py --health

# Run demo scenarios
python demo.py --scenario health
python demo.py --scenario farms
python demo.py --scenario all

# Interactive testing
python client.py --interactive
```

### Example Test Session
```bash
# Start server
python server.py

# In another terminal
python client.py --interactive

Dairy Farm MCP> help
Dairy Farm MCP> info
Dairy Farm MCP> list
Dairy Farm MCP> exec list_farms page=0 size=5
Dairy Farm MCP> health
Dairy Farm MCP> quit
```

## 🤝 Integration

### With Existing MCP Agent
```python
# Add to your MCP agent's context
{
    "api": {
        "tools": [
            {
                "name": "dairy_farm_list_farms",
                "method": "POST",
                "path": "/execute",
                "description": "List dairy farms",
                "parameters": {
                    "operation": "list_farms",
                    "parameters": {"page": 0, "size": 10}
                }
            }
        ]
    }
}
```

### With OpenAI Agent
The server can be integrated with the existing OpenAI-powered MCP agent for natural language queries about dairy farm data.

## 📚 Resources

### National Dairy FARM Program
- **Website**: https://nationaldairyfarm.com/
- **API Documentation**: https://eval.nationaldairyfarm.com/dfdm/api
- **Support**: farmtechsupport@nmpf.org

### Technical Documentation
- **OpenAPI Specification**: Available at the API base URL
- **OAuth2 Documentation**: Standard OAuth2 client credentials flow
- **MCP Protocol**: Model Context Protocol specification

## 🐛 Troubleshooting

### Common Issues

**Authentication Failed**
```bash
Error: Failed to authenticate with Dairy Farm API
```
- Verify client ID and secret in `.env`
- Check API credentials with Dairy Farm support
- Ensure network connectivity

**Connection Refused**
```bash
Error: Failed to connect to MCP server
```
- Ensure server is running: `python server.py`
- Check host and port configuration
- Verify firewall settings

**Operation Failed**
```bash
Error: HTTP 400: Bad Request
```
- Check operation parameters
- Review API documentation for required fields
- Validate data types and formats

### Getting Help
1. Check server logs for detailed error messages
2. Use `--health` to verify connectivity
3. Review API documentation for parameter requirements
4. Contact farmtechsupport@nmpf.org for API issues

## 📄 License

This MCP server implementation is provided as-is for integration with the National Dairy FARM Program API. Please refer to the National Dairy FARM Program's terms of service for API usage guidelines.