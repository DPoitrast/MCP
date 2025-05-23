FROM python:3.11-slim

# Install curl first for HEALTHCHECK (as root)
RUN apt-get update && apt-get install -y curl --no-install-recommends && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first to take advantage of Docker layer caching
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user and group
RUN groupadd -r appgroup && useradd -r -g appgroup -s /sbin/nologin appuser

# Copy the application code and context file, setting ownership to the new user/group
# This assumes the Docker version supports the --chown flag for COPY.
COPY --chown=appuser:appgroup . .

# Switch to the non-root user
USER appuser

# Add HEALTHCHECK instruction
# This assumes there will be a /healthz endpoint on port 80 in the application.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:80/healthz || exit 1

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "app.main:app", "--bind", "0.0.0.0:80"]
