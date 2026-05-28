# ADR-0001: Record architecture decisions

* Status: Accepted
* Date: 2025-07-01

## Context

A portfolio-grade system accumulates decisions whose rationale is easily lost.
Reviewers and future maintainers need to understand *why*, not just *what*.

## Decision

We use lightweight Architecture Decision Records (Michael Nygard format), one
file per decision, numbered, immutable once accepted. Superseding decisions
reference the records they replace.

## Consequences

* Decisions are reviewable in PRs alongside the code that implements them.
* The "why" survives staff turnover.
* Small overhead per decision; we only record significant, hard-to-reverse ones.
