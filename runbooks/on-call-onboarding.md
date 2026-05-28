# Runbook: On-call Onboarding

Reference for new on-call engineers. Not tied to an alert.

## Before your first shift

* Confirm pager access and escalation path.
* Confirm `meridianctl` works against prod (mTLS certs in place):
  `meridianctl nodes list`.
* Read [incident-response.md](../docs/incident-response.md) and the four
  postmortems in [incident-reports/](../incident-reports/).
* Skim every runbook so you know what exists.

## During a page

1. Acknowledge within the SLA.
2. Open the runbook linked in the alert.
3. Open an incident if user-impacting:
   `meridianctl incident open --code INC-NNN --title "..." --severity SEVx`.
4. Mitigate first, root-cause later.
5. Keep a running timeline (you'll need it for the postmortem).

## Key dashboards

Overview, SLO burn, probe health, network telemetry, Linux fleet, incident
response (Grafana, "Meridian" folder).

## Golden signals to check first

* `up{job="meridian-agent"}` — are agents being scraped?
* `meridian:slo_burn_rate_1h` — what's burning?
* `meridian:probe_success_ratio_by_type:5m` — which probe type?
* Controller `/readyz` — is the control plane healthy?
