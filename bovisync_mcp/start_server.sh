#!/bin/bash

# Bovisync MCP Server Startup Script

# Set default values
HOST=${BOVISYNC_HOST:-localhost}
PORT=${BOVISYNC_PORT:-8002}
CLIENT_ID=${BOVISYNC_CLIENT_ID}
CLIENT_SECRET=${BOVISYNC_CLIENT_SECRET}
API_URL=${BOVISYNC_API_URL:-https://api.bovisync.com}

echo "🐄 Starting Bovisync MCP Server"
echo "================================"
echo "Host: $HOST"
echo "Port: $PORT"
echo "API URL: $API_URL"
echo ""

# Check if client credentials are provided
if [ -z "$CLIENT_ID" ] || [ -z "$CLIENT_SECRET" ]; then
    echo "⚠️  Warning: BOVISYNC_CLIENT_ID and BOVISYNC_CLIENT_SECRET environment variables not set"
    echo "   You'll need to provide them as command line arguments or set them in your environment"
    echo ""
fi

# Start the server
python3 server.py \
    --host "$HOST" \
    --port "$PORT" \
    --bovisync-url "$API_URL" \
    --client-id "$CLIENT_ID" \
    --client-secret "$CLIENT_SECRET"