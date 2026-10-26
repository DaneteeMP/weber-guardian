FROM python:3.12-slim
WORKDIR /code
# WeasyPrint renders HTML/CSS to PDF through system libraries (pango/cairo/
# gdk-pixbuf) that python:3.12-slim does not ship. shared-mime-info lets
# gdk-pixbuf resolve the PNG logo MIME type.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libgdk-pixbuf-2.0-0 \
        shared-mime-info \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# $PORT is injected by hosting platforms (Render, Railway). Locally it is
# unset, so the container keeps listening on 8000 as docker-compose expects.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
