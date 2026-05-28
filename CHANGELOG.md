# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2025-11-15
### Added
- Agent with five probe types (DNS, TCP, HTTP, ICMP, traceroute) on a uniform
  result schema.
- Disk-backed ring buffer with at-least-once drain/ack delivery.
- Linux system metrics from /proc and cgroup v2 (incl. PSI).
- Controller: node registry, probe distribution, SLO evaluator, incident
  lifecycle, chaos orchestration. FastAPI + async SQLAlchemy + Alembic.
- `meridianctl` operator CLI.
- Chaos service with six experiment types and watchdog auto-revert.
- SLO catalog as code; multi-window burn-rate recording/alert rules.
- Prometheus, Alertmanager, Loki, Grafana config + six dashboards.
- Deploy: docker-compose, Kubernetes (kustomize + Helm), Ansible, Terraform.
- 15 runbooks (linked from every alert) and 4 blameless postmortems.
- Benchmarks with a CI regression gate; chaos + e2e + load test suites.
- 8 ADRs, 6 architecture diagrams, full docs set.

[Unreleased]: https://github.com/your-org/meridian/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/your-org/meridian/releases/tag/v0.1.0
