#!/usr/bin/env bash
# Render generated docs from source-of-truth config.
# Currently: SLO catalog YAML -> docs/slo-catalog.md table.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python3 - <<'PY'
import yaml, pathlib
cat = yaml.safe_load(pathlib.Path("config/slo/slo-catalog.yaml").read_text())
lines = [
    "# SLO Catalog (rendered)",
    "",
    "> Generated from config/slo/slo-catalog.yaml by tools/docs-build.sh. Do not edit.",
    "",
    "| SLO | Service | Objective | Window |",
    "|---|---|---|---|",
]
for o in cat.get("objectives", []):
    lines.append(f"| {o['name']} | {o['service']} | {o['objective_pct']}% | {o['window_days']}d |")
out = pathlib.Path("docs/slo-catalog.generated.md")
out.write_text("\n".join(lines) + "\n")
print(f"wrote {out}")
PY
