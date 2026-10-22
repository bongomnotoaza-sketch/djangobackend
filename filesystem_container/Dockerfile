FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN useradd --create-home --shell /bin/bash appuser

RUN mkdir -p /workspace && chown -R appuser:appuser /workspace

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY api.py .
COPY file_server.py .
COPY file_system_service.py .

USER appuser

CMD ["python", "file_server.py"]