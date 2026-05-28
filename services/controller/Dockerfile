# syntax=docker/dockerfile:1.6
FROM python:3.12-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential libssl-dev libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY services/controller/pyproject.toml services/controller/README.md ./
COPY services/controller/src ./src
COPY services/controller/migrations ./migrations
COPY services/controller/alembic.ini ./alembic.ini
COPY libs ./libs

RUN pip install --prefix=/install \
      "./libs/meridian_common" \
      "./libs/meridian_proto" \
      "." \
 && find /install -name __pycache__ -type d -exec rm -rf {} +

FROM python:3.12-slim-bookworm AS runtime

# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
      libpq5 ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --system --no-create-home --uid 1100 meridian

ENV PATH=/app/bin:$PATH \
    PYTHONPATH=/app/lib/python3.12/site-packages \
    PYTHONUNBUFFERED=1

COPY --from=builder /install /app
COPY services/controller/migrations /opt/meridian/migrations
COPY services/controller/alembic.ini /opt/meridian/alembic.ini

WORKDIR /opt/meridian
USER meridian
EXPOSE 8443
ENTRYPOINT ["python", "-m", "meridian_controller"]
