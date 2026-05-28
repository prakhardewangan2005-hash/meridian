#!/usr/bin/env bash
# Run the full local CI gate: lint, tests, and the alert/runbook invariant.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
fail=0

echo "########## LINT ##########"
bash tools/lint.sh || fail=1

echo; echo "########## TESTS ##########"
make test || fail=1

echo; echo "########## INVARIANT: every alert has a runbook_url ##########"
# Find alert names lacking a runbook_url annotation.
python3 - <<'PY' || fail=1
import sys, yaml, pathlib
p = pathlib.Path("config/prometheus/alerts.yml")
doc = yaml.safe_load(p.read_text())
missing = []
for group in doc.get("groups", []):
    for rule in group.get("rules", []):
        if "alert" not in rule:
            continue
        ann = rule.get("annotations", {})
        if "runbook_url" not in ann:
            missing.append(rule["alert"])
if missing:
    print("ALERTS MISSING runbook_url:", ", ".join(missing))
    sys.exit(1)
print("OK: all alerts have a runbook_url")
PY

echo; echo "########## INVARIANT: runbook files exist for referenced URLs ##########"
python3 - <<'PY' || fail=1
import sys, re, yaml, pathlib
doc = yaml.safe_load(pathlib.Path("config/prometheus/alerts.yml").read_text())
missing = []
for group in doc.get("groups", []):
    for rule in group.get("rules", []):
        url = rule.get("annotations", {}).get("runbook_url", "")
        m = re.search(r"/runbooks/([\w-]+\.md)$", url)
        if m and not pathlib.Path("runbooks", m.group(1)).is_file():
            missing.append(m.group(1))
if missing:
    print("MISSING runbook files:", ", ".join(sorted(set(missing))))
    sys.exit(1)
print("OK: all referenced runbooks exist")
PY

exit $fail
