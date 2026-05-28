#!/usr/bin/env bash
# Run all linters. Mirrors what CI does.
set -uo pipefail
fail=0
run() { echo "==> $1"; shift; "$@" || fail=1; }

run "ruff"      ruff check .
run "ruff-fmt"  ruff format --check .
run "mypy"      mypy services libs || true   # type errors are advisory locally
run "yamllint"  yamllint -c .yamllint.yml config deploy
command -v shellcheck >/dev/null && run "shellcheck" shellcheck scripts/*.sh tools/*.sh

exit $fail
