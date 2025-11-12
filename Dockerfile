FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

EXPOSE 8888

# Run FastAPI app via uvicorn, serving the MCP HTTP app mounted at /mcp
CMD ["uvicorn", "server:asgi_app", "--host", "0.0.0.0", "--port", "8888"]


