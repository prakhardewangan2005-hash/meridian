# Integration / E2E / Load / Chaos Tests

These tests exercise the system as a whole, beyond the per-service unit tests.

| Suite | Needs | Run |
|---|---|---|
| `e2e/` | full compose stack up | `make test-e2e` |
| `load/` | running controller | `locust -f tests/load/locustfile.py` |
| `chaos/` | chaos service (dry-run ok) | `make chaos-test` |

E2E tests are marked `@pytest.mark.e2e` and skipped by default unless the stack
is reachable, so a plain `make test` stays fast and hermetic.
