# Adding an SLO

SLOs are version-controlled in
[config/slo/slo-catalog.yaml](../../config/slo/slo-catalog.yaml). Adding one is a
reviewed PR.

## 1. Add the objective

See [new-slo.yaml](new-slo.yaml) for the shape. The `sli_query` must return the
**good-event ratio** in [0,1].

## 2. Render docs + rules

```bash
./tools/docs-build.sh    # regenerates the catalog table
```

CI generates the multi-window burn-rate recording/alert rules from the catalog.

## 3. Verify compliance

```bash
python scripts/check-slo-compliance.py --prometheus http://localhost:9090
```
