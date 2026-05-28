# syntax=docker/dockerfile:1.6
# ---- builder ---------------------------------------------------------------
FROM python:3.14-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY services/agent/pyproject.toml services/agent/README.md ./
COPY services/agent/src ./src
COPY libs ./libs

RUN pip install --prefix=/install \
      "./libs/meridian_common" \
      "./libs/meridian_proto" \
      "." \
 && find /install -name __pycache__ -type d -exec rm -rf {} +

# ---- runtime ---------------------------------------------------------------
FROM gcr.io/distroless/python3-debian12:nonroot AS runtime

LABEL org.opencontainers.image.title="meridian-agent" \
      org.opencontainers.image.description="Per-host telemetry & probe agent" \
      org.opencontainers.image.source="https://github.com/your-org/meridian" \
      org.opencontainers.image.licenses="Apache-2.0"

ENV PYTHONPATH=/app/lib/python3.12/site-packages \
    PYTHONUNBUFFERED=1
COPY --from=builder /install /app

USER nonroot:nonroot
EXPOSE 9101
ENTRYPOINT ["python", "-m", "meridian_agent"]
