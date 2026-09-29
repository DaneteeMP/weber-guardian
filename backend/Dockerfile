FROM python:3.12-slim
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# $PORT is injected by hosting platforms (Render, Railway). Locally it is
# unset, so the container keeps listening on 8000 as docker-compose expects.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
