# Basic Deployment (local)

Bring up the entire Meridian stack on your laptop.

```bash
# from the repo root
./scripts/bootstrap-dev.sh
# or manually:
./scripts/generate-certs.sh ./pki
docker compose up -d
./scripts/healthcheck.sh
```

Then:
* Grafana — http://localhost:3000 (admin/admin), "Meridian" dashboard folder
* Prometheus — http://localhost:9090
* Alertmanager — http://localhost:9093

Seed some inventory:
```bash
python scripts/seed-inventory.py
meridianctl probes list
meridianctl slo list
```

Tear down:
```bash
docker compose down -v
```
