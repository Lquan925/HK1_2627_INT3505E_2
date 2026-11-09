FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir ".[postgres,server]"
COPY migrations ./migrations
COPY alembic.ini wsgi.py ./
RUN useradd --create-home appuser && mkdir -p /app/instance && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "wsgi:app"]
