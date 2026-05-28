# ADR-0008: SLOs as version-controlled code

* Status: Accepted
* Date: 2025-07-08

## Context

SLOs defined in dashboards or someone's head drift and can't be reviewed. We
want objectives to be auditable, reviewable, and the single source for both docs
and alerting.

## Decision

`config/slo/slo-catalog.yaml` is the source of truth. CI renders it to
`docs/slo-catalog.md` and generates the multi-window burn-rate recording/alert
rules from it. Changing an objective is a reviewed pull request.

## Consequences

* SLO changes have history, review, and blame — like any other code.
* Docs and alert rules can't drift from the objectives; they're generated.
* Requires a small render/generate step in CI (`tools/docs-build.sh`).
