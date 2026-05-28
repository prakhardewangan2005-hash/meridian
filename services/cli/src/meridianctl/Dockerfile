# syntax=docker/dockerfile:1.6
FROM python:3.12-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build
COPY services/cli/pyproject.toml services/cli/README.md ./
COPY services/cli/src ./src
RUN pip install --prefix=/install "."

FROM python:3.12-slim-bookworm
ENV PYTHONPATH=/app/lib/python3.12/site-packages \
    PATH=/app/bin:$PATH
COPY --from=builder /install /app
ENTRYPOINT ["meridianctl"]
