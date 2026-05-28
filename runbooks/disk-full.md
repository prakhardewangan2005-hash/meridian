# Runbook: Disk Filling Up

**Alert:** `NodeDiskFillingUp` (root fs > 85%) · **Severity:** ticket

## Impact
Disk pressure threatens the agent buffer and any co-located service. At 100% the
agent can't write buffer segments (it will evict oldest, then drop).

## Check
1. `df -h` and `du -xh / | sort -h | tail` — what's growing?
2. Is it the Meridian buffer (`/var/lib/meridian/buffer`)? If so the collector
   isn't draining — check Prometheus scrape and exporter.
3. Logs not rotating? Container layer growth? Core dumps?

## Mitigate
* Buffer not draining → fix the consumer; the buffer self-caps and evicts oldest,
  so it won't fill the disk by itself if `buffer.max_bytes` is sane.
* Runaway logs → rotate/truncate; fix logrotate.
* Genuinely undersized → grow the volume.

## Verify
Root fs back under 85%; buffer size stable.

## Escalate
Repeated fills → capacity planning review.

## Related
[probe-storm](probe-storm.md)
