# Runbook: DNS Resolution Failure

**Alert:** `DNSResolutionFailing` (DNS probe success < 90%) · **Severity:** page

## Impact
DNS is failing fleet-wide or for a major zone. Because almost everything depends
on DNS, this is frequently the root cause of *other* alerts — triage DNS first
in any multi-alert situation.

## Check
1. Scope: all resolvers or one? `meridian:probe_success_ratio_by_type:5m{type="dns"}`
   broken down by target/resolver.
2. On a host: `scripts/dns-debug.sh <name>` (tries system resolver, then 1.1.1.1,
   8.8.8.8; shows `dig +trace` if needed).
3. Is it the resolver or upstream authoritative? Query the resolver directly vs a
   public resolver.

## Mitigate
* Resolver pod/box down → restart/replace it.
* Upstream authoritative outage → fail over to secondary resolver; update
  `resolv.conf`/agent probe resolver.
* Recently changed records / bad zone push → roll back the DNS change.

## Verify
DNS probe success ratio back above objective (99.5%); dependent alerts clear.

## Escalate
Authoritative/registrar issues → escalate to network/DNS owner.

## Related
[INC-001 cascading DNS failure](../incident-reports/INC-001-cascading-dns-failure.md),
[alert-storm](alert-storm.md)
