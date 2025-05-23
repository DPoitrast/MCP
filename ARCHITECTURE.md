# MCP Server Architecture

## Overview
This project has been restructured into a clean, production-ready architecture following industry best practices. The codebase now follows a layered architecture pattern with clear separation of concerns.

## Project Structure

```
app/
├── __init__.py
├── main.py                     # FastAPI application factory
├── models.py                   # Domain models (dataclasses)
├── schemas.py                  # Pydantic models for API validation
├── seed.py                     # Database seeding script
├── api/                        # API layer
│   ├── dependencies.py         # Common API dependencies
│   └── v1/
│       ├── api.py             # API router configuration
│       └── endpoints/
│           ├── health.py       # Health check endpoints
│           └── herd.py         # Herd CRUD endpoints
├── core/                       # Core functionality
│   ├── config.py              # Application configuration
│   ├── database.py            # Database connection management
│   └── security.py            # Authentication & authorization
├── exceptions/                 # Custom exception classes
│   └── exceptions.py          # Business logic exceptions
├── repositories/               # Data access layer
│   ├── base.py                # Base repository class
│   └── herd.py                # Herd data access operations
└── services/                   # Business logic layer
    └── herd.py                # Herd business logic
```

## Architecture Layers

### 1. API Layer (`app/api/`)
- **Responsibility**: HTTP request/response handling, input validation, serialization
- **Components**: FastAPI routers, endpoint handlers, dependency injection
- **Key Features**:
  - Proper HTTP status codes
  - Comprehensive error handling
  - Request/response validation with Pydantic
  - Authentication integration

### 2. Service Layer (`app/services/`)
- **Responsibility**: Business logic, domain rules, workflow orchestration
- **Components**: Service classes with business methods
- **Key Features**:
  - Input validation and business rules
  - Transaction coordination
  - Logging and audit trails
  - Exception handling with custom exceptions

### 3. Repository Layer (`app/repositories/`)
- **Responsibility**: Data access and persistence
- **Components**: Repository classes for database operations
- **Key Features**:
  - CRUD operations
  - Query optimization
  - Transaction management
  - Database-specific error handling

### 4. Core Layer (`app/core/`)
- **Responsibility**: Cross-cutting concerns and infrastructure
- **Components**: Configuration, database connections, security
- **Key Features**:
  - Centralized configuration management
  - Database connection pooling
  - Authentication and authorization
  - Environment-specific settings

## Key Improvements

### 1. **Separation of Concerns**
- API layer only handles HTTP concerns
- Business logic isolated in service layer
- Data access encapsulated in repositories
- Infrastructure concerns in core layer

### 2. **Dependency Injection**
- Services injected into API endpoints
- Repositories injected into services
- Database connections managed as dependencies
- Easy testing with mock dependencies

### 3. **Error Handling**
- Custom exception hierarchy
- Global exception handlers
- Proper HTTP status codes
- Structured error responses

### 4. **Configuration Management**
- Environment-based configuration
- Type-safe settings with Pydantic
- Default values with overrides
- Centralized configuration access

### 5. **Security Enhancements**
- JWT token support (backwards compatible with dev token)
- Proper authentication flow
- Authorization on all endpoints
- Security middleware ready

### 6. **Database Improvements**
- Enhanced schema with timestamps
- Proper indexing for performance
- Transaction safety
- Connection pooling ready
- Database health checks

### 7. **API Enhancements**
- Paginated responses with metadata
- Search functionality
- CRUD operations with proper status codes
- Statistics endpoint
- Comprehensive documentation

## API Endpoints

### Health Endpoints
- `GET /api/v1/health` - Service health check
- `GET /api/v1/health/database` - Database health check

### Herd Endpoints
- `GET /api/v1/herd` - List herds (paginated)
- `GET /api/v1/herd/{id}` - Get herd by ID
- `POST /api/v1/herd` - Create new herd
- `PUT /api/v1/herd/{id}` - Update herd
- `DELETE /api/v1/herd/{id}` - Delete herd
- `GET /api/v1/herd/stats` - Get herd statistics
- `GET /api/v1/herd/search/name?name=X` - Search by name
- `GET /api/v1/herd/search/location?location=X` - Search by location

## Configuration

The application uses environment-based configuration with sensible defaults:

```env
# Database
DATABASE_URL=sqlite:///mcp.db
DATABASE_PATH=mcp.db

# Security
SECRET_KEY=your-secret-key
ALGORITHM=HS256

# API
API_V1_PREFIX=/api/v1
MAX_QUERY_LIMIT=1000
DEFAULT_QUERY_LIMIT=100

# Logging
LOG_LEVEL=INFO

# Environment
ENVIRONMENT=development
DEBUG=false
```

## Testing

The codebase maintains full test compatibility while adding new functionality:

- All existing tests pass
- New API structure tested
- Error handling verified
- Authentication flows tested

## Future Enhancements

This architecture supports easy extension:

1. **Additional Resources**: Add new entities following the same pattern
2. **Authentication**: Full JWT implementation ready
3. **Caching**: Service layer ready for caching integration
4. **Async Database**: Easy migration to async SQL drivers
5. **Message Queues**: Service layer can integrate with event systems
6. **Monitoring**: Structured logging and metrics ready

## Migration Notes

- Old `crud.py` functionality moved to repositories and services
- Old `database.py` enhanced and moved to `core/database.py`
- API responses now include pagination metadata
- Authentication enhanced but backwards compatible
- All existing functionality preserved with improvements