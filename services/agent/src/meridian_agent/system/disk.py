"""Disk metrics from /proc/diskstats and statvfs on mounted filesystems."""
from __future__ import annotations

import os
import shutil

from meridian_agent.system.procfs import PROC, read_lines

# Mount points we care about by default. Override in config.
DEFAULT_MOUNTS = ("/", "/var", "/var/lib/meridian")


def _diskstats() -> dict[str, dict[str, int]]:
    """Per-device counters from /proc/diskstats. Field order:
       major minor name reads_completed reads_merged sectors_read ms_reading
       writes_completed writes_merged sectors_written ms_writing
       ios_in_progress ms_doing_io weighted_ms_doing_io
    """
    out: dict[str, dict[str, int]] = {}
    for line in read_lines(PROC / "diskstats"):
        f = line.split()
        if len(f) < 14:
            continue
        name = f[2]
        # Skip loop / ram / partition leaves we typically don't care about
        if name.startswith(("loop", "ram", "dm-")):
            continue
        try:
            out[name] = {
                "reads_completed": int(f[3]),
                "sectors_read": int(f[5]),
                "ms_reading": int(f[6]),
                "writes_completed": int(f[7]),
                "sectors_written": int(f[9]),
                "ms_writing": int(f[10]),
                "ios_in_progress": int(f[11]),
                "ms_doing_io": int(f[12]),
            }
        except ValueError:
            continue
    return out


def collect(mounts: tuple[str, ...] = DEFAULT_MOUNTS) -> dict[str, float]:
    out: dict[str, float] = {}
    for mount in mounts:
        if not os.path.ismount(mount) and mount != "/":
            continue
        try:
            usage = shutil.disk_usage(mount)
        except OSError:
            continue
        safe = mount.replace("/", "_") or "root"
        out[f"disk_total_bytes{safe}"] = float(usage.total)
        out[f"disk_used_bytes{safe}"] = float(usage.used)
        out[f"disk_free_bytes{safe}"] = float(usage.free)
        out[f"disk_used_pct{safe}"] = 100.0 * usage.used / usage.total if usage.total else 0.0

    # inode usage on /
    try:
        st = os.statvfs("/")
        if st.f_files:
            out["inode_used_pct_root"] = 100.0 * (st.f_files - st.f_ffree) / st.f_files
    except OSError:
        pass

    # Roll up per-device IO counters
    devs = _diskstats()
    for dev, counters in devs.items():
        for k, v in counters.items():
            out[f"disk_dev_{dev}_{k}"] = float(v)
    return out
