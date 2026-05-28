# syntax=docker/dockerfile:1.6
FROM python:3.12-slim-bookworm

# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
      iproute2 iptables stress-ng util-linux \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY services/chaos/pyproject.toml services/chaos/README.md ./
COPY services/chaos/src ./src
RUN pip install --no-cache-dir .

EXPOSE 8080
ENTRYPOINT ["meridian-chaos"]
