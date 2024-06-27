FROM python:3.12-slim

EXPOSE 8010

ENV CONFIG production

COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade -r requirements.txt

WORKDIR /app

COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

CMD ["fastapi", "run", "--host", "0.0.0.0", "--port", "8010", "--workers", "4"]
