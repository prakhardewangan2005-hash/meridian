#!/usr/bin/env bash
# Install + run pre-commit hooks.
set -euo pipefail
if ! command -v pre-commit >/dev/null; then
  pip install pre-commit
fi
pre-commit install
pre-commit run --all-files
