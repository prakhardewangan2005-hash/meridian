# Custom Probe Plugin

Meridian discovers probes via the `meridian_agent.probes` entry-point group, so
you can ship a probe in your own package without touching the agent.

## 1. Implement the Probe ABC

See [my_probe.py](my_probe.py). Subclass `Probe`, set `probe_type`, implement
`async def execute() -> ProbeResult`.

## 2. Register the entry point

In your package's `pyproject.toml`:

```toml
[project.entry-points."meridian_agent.probes"]
tls_expiry = "my_package.my_probe:TLSExpiryProbe"
```

## 3. Install it alongside the agent

```bash
pip install my-package
```

The agent's registry picks it up automatically; reference it by type in your
probe YAML:

```yaml
probes:
  - type: tls_expiry
    name: cert-check
    target: example.com:443
    interval_s: 3600
```
