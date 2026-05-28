# Load Tests

Locust-based load test for the controller API.

```bash
pip install locust
locust -f tests/load/locustfile.py --host https://localhost:8443
# headless:
locust -f tests/load/locustfile.py --host https://localhost:8443 \
  --headless -u 100 -r 10 -t 1m
```

Targets the read-heavy endpoints (node/probe/SLO listing) plus heartbeat writes,
which mirror real fleet traffic.
