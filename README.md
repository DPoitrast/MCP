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
