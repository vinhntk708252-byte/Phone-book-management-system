# Dockerfile - Packaging & Deployment for Phone Book Management System (Group 03)
FROM debian:bookworm-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-tk python3-pytest && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

CMD ["python3", "main.py"]
