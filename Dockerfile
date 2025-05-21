FROM python:3.11-slim

WORKDIR /app
COPY ./app ./app
COPY ./model_context.yaml ./model_context.yaml
RUN pip install fastapi uvicorn[standard] sqlalchemy pydantic

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
