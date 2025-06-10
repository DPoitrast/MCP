FROM python:3.11-slim

WORKDIR /app

# Create a non-root user and group first
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Install Python dependencies first to take advantage of Docker layer caching
# These can be owned by root as they are system-level packages
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and chown it to the appuser
# This ensures the application files are owned by the non-root user
COPY --chown=appuser:appgroup . .

# Switch to the non-root user
USER appuser

EXPOSE 80

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
