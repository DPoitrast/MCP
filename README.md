# MCP Proof of Concept

This repository contains a sophisticated Model Context Protocol (MCP) server
implemented with **FastAPI**. The project demonstrates advanced API design patterns
including OAuth2 authentication, dynamic API discovery, and comprehensive herd
management capabilities that can be deployed to AWS Fargate.

## Features

### 🔐 Authentication & Security
- **OAuth2 with JWT**: Bearer token authentication system
- **User Management**: Built-in user database with role-based access
- **Protected Endpoints**: Secure API operations requiring authentication
- **Development Mode**: Backwards compatibility with simple token authentication

### 🔍 Enhanced MCP Agent
- **Dynamic API Discovery**: Automatically discovers endpoints from OpenAPI metadata
- **Universal Operation Support**: Execute any discovered API operation
- **Fallback Compatibility**: Graceful degradation to static YAML configuration
- **10x More Operations**: Comprehensive endpoint coverage vs static configuration

### 📊 Comprehensive API
- **CRUD Operations**: Full herd management (Create, Read, Update, Delete)
- **Search & Filtering**: Search herds by name with flexible parameters
- **Pagination**: Efficient data retrieval with skip/limit controls
- **Statistics**: Real-time herd analytics and reporting
- **Health Monitoring**: System health checks and database status

### 🚀 Advanced Operations
- **MCP Execute**: Protected operation execution endpoint
- **Broadcast System**: Message broadcasting to connected clients
- **Model Listing**: Available MCP models and capabilities
- **Real-time Analytics**: Live system statistics and performance metrics

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Seed the database:**
   ```bash
   python -m app.seed
   ```

3. **Start the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Get an access token:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=johndoe&password=secret"
   ```

The database path can be configured via the `DATABASE_PATH` environment variable.
If not set, it defaults to `mcp.db` in the working directory.

## Authentication

### Available Users
- **johndoe** / **secret** - Active user account
- **alice** / **wonderland** - Active user account  
- **Development token**: `fake-super-secret-token` (development mode only)

### OAuth2 Flow
```bash
# Get access token
curl -X POST "http://localhost:8000/api/v1/auth/token" \
     -d "username=johndoe&password=secret"

# Use token in requests
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/v1/herd"
```

## Enhanced Agent Usage

### Dynamic Discovery Mode (Recommended)
```bash
# List all dynamically discovered operations
python -m agent http://localhost:8000 --list-tools

# Execute any operation with parameters
python -m agent http://localhost:8000 --execute health_check_api_v1_health_get --token YOUR_TOKEN

# Create new herd
python -m agent http://localhost:8000 --execute create_herd_api_v1_herd_post \
       --params '{"name": "New Farm", "location": "Colorado"}' --token YOUR_TOKEN
```

### Static Configuration Mode
```bash
# Traditional static configuration
python -m agent http://localhost:8000 --token YOUR_TOKEN
```

### Enhanced Agent Demo
Experience the full capabilities:
```bash
python demo_enhanced_agent.py
```

This demonstrates:
- Dynamic vs static discovery comparison
- All available operations execution
- Error handling and fallback mechanisms
- Real-time herd management operations

## API Operations

### Core Herd Management
- `GET /api/v1/herd` - List herds with pagination
- `POST /api/v1/herd` - Create new herd
- `GET /api/v1/herd/{id}` - Get specific herd
- `PUT /api/v1/herd/{id}` - Update herd
- `DELETE /api/v1/herd/{id}` - Delete herd

### Advanced Features
- `GET /api/v1/herd/search/name` - Search herds by name
- `GET /api/v1/herd/stats` - Get herd statistics
- `GET /api/v1/health` - System health check

### Protected MCP Operations
- `POST /api/v1/mcp/execute` - Execute MCP operations
- `POST /api/v1/mcp/broadcast` - Broadcast messages
- `GET /api/v1/mcp/models` - List available models

### Authentication Endpoints
- `POST /api/v1/auth/token` - OAuth2 token login
- `GET /api/v1/auth/users/me` - Current user info
- `GET /api/v1/auth/users/me/profile` - Detailed profile

## Testing

```bash
# Run all tests
pytest -q

# Run specific test files
pytest tests/test_agent.py -v
pytest tests/test_list_herd.py -v
```

## Container Deployment

```bash
# Build container
docker build -t mcp .

# Run container
docker run -p 8000:8000 mcp
```

## Infrastructure

The `terraform/` directory provides AWS deployment configuration:
- **ECR Repository**: Container image storage
- **Fargate Service**: Serverless container deployment
- **Load Balancer**: High availability and scaling

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

## Documentation

- **[Enhanced Agent Guide](ENHANCED_AGENT.md)** - Comprehensive agent capabilities and usage
- **[Architecture Overview](ARCHITECTURE.md)** - System design and patterns
- **OpenAPI Docs**: Available at `/docs` when server is running

## Project Structure

```
├── app/                    # FastAPI application
│   ├── api/v1/endpoints/   # API route handlers
│   ├── core/               # Configuration and security
│   ├── models.py           # Database models
│   ├── schemas.py          # Pydantic schemas
│   └── services/           # Business logic
├── agent/                  # Enhanced MCP agent
├── tests/                  # Test suite
├── terraform/              # AWS infrastructure
└── demo_enhanced_agent.py  # Full capabilities demo
```

The MCP discovery file is available at `model_context.yaml` for static configuration.
