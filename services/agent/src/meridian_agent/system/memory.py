"""Memory + swap from /proc/meminfo."""
from __future__ import annotations

from meridian_agent.system.procfs import PROC, first_int, read_kv


def collect() -> dict[str, float]:
    mi = read_kv(PROC / "meminfo")
    total = first_int(mi["MemTotal"]) * 1024
    available = first_int(mi.get("MemAvailable", mi.get("MemFree", "0 kB"))) * 1024
    free = first_int(mi["MemFree"]) * 1024
    swap_total = first_int(mi.get("SwapTotal", "0 kB")) * 1024
    swap_free = first_int(mi.get("SwapFree", "0 kB")) * 1024
    used = total - available
    return {
        "mem_total_bytes": float(total),
        "mem_available_bytes": float(available),
        "mem_used_bytes": float(used),
        "mem_free_bytes": float(free),
        "mem_used_pct": 100 * used / total if total else 0.0,
        "swap_total_bytes": float(swap_total),
        "swap_used_bytes": float(swap_total - swap_free),
        "swap_used_pct": 100 * (swap_total - swap_free) / swap_total if swap_total else 0.0,
    }
