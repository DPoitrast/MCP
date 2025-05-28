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

### 🤖 OpenAI Integration
- **GPT-4o-mini Model**: Fast, cost-effective AI powered by OpenAI's latest mini model
- **Intelligent Conversations**: Natural language interface with advanced reasoning
- **Smart MCP Operations**: AI understands user intent and executes appropriate MCP operations
- **Conversational Context**: Maintains conversation history for better interactions
- **Model Flexibility**: Switch between GPT-4o-mini, GPT-4o, and other models
- **API Endpoints**: RESTful endpoints for chat and intelligent query capabilities

### 💬 Interactive Interfaces
- **Interactive CLI**: Full-featured command-line interface with streaming responses
- **Web Interface**: Modern web-based chat interface for browser interaction
- **Unified Database**: Both interfaces use the same MCP database and authentication
- **Session Management**: User-specific conversation saving and restoration
- **Real-time Streaming**: Live response streaming for immediate feedback
- **Tab Completion**: Smart completion for commands and tool names

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

2. **Configure OpenAI (Optional):**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```

3. **Seed the database:**
   ```bash
   python -m app.seed
   ```

4. **Start the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Get an access token:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=johndoe&password=secret"
   ```

6. **Try the interactive agents:**
   ```bash
   # Interactive CLI (uses MCP database authentication)
   python interactive_agent.py
   
   # Web interface (in separate terminal, same database)
   python web_interface.py
   # Visit http://localhost:8080 and login with johndoe/secret
   
   # Demo all features
   python demo_agent_usage.py
   
   # Test unified database access
   python test_unified_database.py
   ```

The database path can be configured via the `DATABASE_PATH` environment variable.
If not set, it defaults to `mcp.db` in the working directory.

## AI Model Configuration

The system now uses **GPT-4o-mini** as the default model for optimal performance and cost:

### 🤖 **Current Model**: GPT-4o-mini
- **Performance**: ~2x faster than GPT-4 for most tasks
- **Cost**: Significantly lower cost per token
- **Quality**: High-quality responses for interactive chat and MCP operations
- **Availability**: Latest OpenAI model with improved efficiency

### 🔄 **Model Switching**
- **CLI**: Use `/model <name>` to switch models
- **Available models**: gpt-4o-mini, gpt-4o, gpt-4-turbo, gpt-3.5-turbo
- **Session persistent**: Model choice saves across CLI sessions
- **Web interface**: Uses gpt-4o-mini by default

### 💡 **Model Recommendations**
- **gpt-4o-mini**: Best for interactive chat and general tasks (default)
- **gpt-4o**: Use for complex reasoning tasks
- **gpt-3.5-turbo**: Fallback for basic interactions

## Unified Database System

Both the CLI and web interfaces now use the **same MCP database** for authentication and operations:

### 🔑 **Shared Authentication**
- Both interfaces authenticate against the same user database
- Same JWT token system for both CLI and web
- Consistent user management across interfaces

### 💾 **Database Consistency** 
- **User accounts**: Shared between CLI and web interface
- **MCP operations**: Both use identical API endpoints
- **Tool discovery**: Same tool set available in both interfaces
- **Conversation history**: Interface-specific but user-isolated

### 🔄 **Cross-Interface Benefits**
- Login with `johndoe/secret` or `alice/wonderland` in both interfaces
- MCP operations executed through web interface affect same database as CLI
- Consistent tool availability and functionality
- Unified session management per user

## Authentication

### Available Users
- **johndoe** / **secret** - Active user account
- **alice** / **wonderland** - Active user account  
- **Development token**: `fake-super-secret-token` (development mode only)

### OAuth2 Flow
```bash
# Get access token
curl -X POST "http://localhost:8000/api/v1/token" \
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

### Interactive Agent Demos
Experience the AI-powered interactive agents:

**CLI Interface:**
```bash
python interactive_agent.py
# Default: GPT-4o-mini model
# Use /model gpt-4o to switch models
```
Features: Real-time chat, streaming responses, command system, tab completion

**Web Interface:**
```bash
python web_interface.py
# Visit http://localhost:8080
# Login with johndoe/secret or alice/wonderland
# Uses GPT-4o-mini by default
```
Features: Modern web UI, MCP database authentication, real-time messaging

**Feature Demo:**
```bash
python demo_agent_usage.py
```
This demonstrates:
- OpenAI integration and chat capabilities
- Intelligent MCP operation execution
- Natural language query processing
- API endpoint usage examples

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

### OpenAI Agent Endpoints
- `POST /api/v1/agent/chat` - Direct chat with OpenAI agent
- `POST /api/v1/agent/query` - Intelligent MCP queries with natural language
- `GET /api/v1/agent/capabilities` - Agent capabilities and configuration
- `GET /api/v1/agent/tools` - Available MCP tools
- `GET /api/v1/agent/status` - Agent operational status

### Authentication Endpoints
- `POST /api/v1/token` - OAuth2 token login
- `GET /api/v1/users/me` - Current user info
- `GET /api/v1/users/me/profile` - Detailed profile

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
