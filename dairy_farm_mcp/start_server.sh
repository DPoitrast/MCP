#!/bin/bash
# National Dairy Farm MCP Server Startup Script

echo "🐄 Starting National Dairy Farm MCP Server"
echo "=========================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env with your API credentials before running again."
    exit 1
fi

# Check if requirements are installed
if ! python3 -c "import fastapi, uvicorn, httpx, pydantic" 2>/dev/null; then
    echo "📦 Installing requirements..."
    pip install -r requirements.txt
fi

# Default configuration
HOST=${DAIRY_FARM_MCP_SERVER_HOST:-localhost}
PORT=${DAIRY_FARM_MCP_SERVER_PORT:-8001}
API_URL=${DAIRY_FARM_API_URL:-https://eval.nationaldairyfarm.com/dfdm/api}

echo "🔧 Configuration:"
echo "  Host: $HOST"
echo "  Port: $PORT"
echo "  Dairy Farm API: $API_URL"

# Check for credentials
if [ -z "$DAIRY_FARM_CLIENT_ID" ] && ! grep -q "DAIRY_FARM_CLIENT_ID=" .env; then
    echo "❌ DAIRY_FARM_CLIENT_ID not configured"
    echo "   Please set it in .env file or environment variable"
    exit 1
fi

if [ -z "$DAIRY_FARM_CLIENT_SECRET" ] && ! grep -q "DAIRY_FARM_CLIENT_SECRET=" .env; then
    echo "❌ DAIRY_FARM_CLIENT_SECRET not configured"
    echo "   Please set it in .env file or environment variable"
    exit 1
fi

echo "✅ Credentials configured"
echo ""
echo "🚀 Starting server..."
echo "   Server URL: http://$HOST:$PORT"
echo "   API Docs: http://$HOST:$PORT/docs"
echo "   Health Check: http://$HOST:$PORT/health"
echo ""
echo "📋 Available endpoints:"
echo "   GET  /                - Server information"
echo "   GET  /operations      - List available operations"
echo "   POST /execute         - Execute MCP operation"
echo "   GET  /health          - Health check"
echo ""
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start the server
python3 server.py --host "$HOST" --port "$PORT" --dairy-farm-url "$API_URL"