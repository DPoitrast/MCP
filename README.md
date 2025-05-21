# MCP Proof of Concept

This repository contains a simple Model Context Protocol (MCP) server
implemented with **FastAPI**. The goal is to expose herd data through a
discoverable, versioned API that can be deployed to AWS Fargate.

## Running locally

1. Seed the SQLite database:

   ```bash
   python -m app.seed
   ```

2. Start the API server:

   ```bash
   uvicorn app.main:app --reload
   ```

3. Authenticate with the token `fake-super-secret-token` when calling the API.

The MCP discovery file is available at `model_context.yaml`.

## Using the agent

An `agent` package is provided to interact with the MCP server. After the
server is running you can list the herd data like so:

```bash
python -m agent http://localhost:8000 --token fake-super-secret-token
```

The agent reads `model_context.yaml` to discover the API path and returns the
JSON response from the server.

## Running tests

```bash
pytest -q
```

## Container

A `Dockerfile` is provided to run the server in a container. Build with:

```bash
docker build -t mcp .
```

## Terraform

The `terraform` directory contains a minimal configuration showing how the
container could be deployed to AWS (e.g. Fargate). It creates an ECR repository
for the image.
