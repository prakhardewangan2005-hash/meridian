"""Network counters from /proc/net.

Surfaces:
  * /proc/net/dev      — per-interface byte/packet/error/drop
  * /proc/net/netstat  — TCP retransmits, listen drops, fast retrans
  * /proc/net/snmp     — IP/TCP/UDP aggregate
  * /proc/net/sockstat — socket allocation
"""
from __future__ import annotations

from pathlib import Path

from meridian_agent.system.procfs import PROC, read_lines

TCP_KEYS_OF_INTEREST = (
    "TcpExt_TCPLostRetransmit",
    "TcpExt_TCPSynRetrans",
    "TcpExt_TCPFastRetrans",
    "TcpExt_ListenDrops",
    "TcpExt_ListenOverflows",
    "Tcp_RetransSegs",
    "Tcp_InSegs",
    "Tcp_OutSegs",
    "Tcp_CurrEstab",
)


def _read_dev() -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    for line in read_lines(PROC / "net/dev")[2:]:
        if ":" not in line:
            continue
        iface, rest = line.split(":", 1)
        iface = iface.strip()
        if iface == "lo":
            continue
        f = rest.split()
        if len(f) < 16:
            continue
        out[iface] = {
            "rx_bytes": int(f[0]),
            "rx_packets": int(f[1]),
            "rx_errors": int(f[2]),
            "rx_dropped": int(f[3]),
            "tx_bytes": int(f[8]),
            "tx_packets": int(f[9]),
            "tx_errors": int(f[10]),
            "tx_dropped": int(f[11]),
        }
    return out


def _read_paired(path: Path) -> dict[str, int]:
    """Parse /proc/net/{netstat,snmp}: alternating header/value lines."""
    out: dict[str, int] = {}
    lines = read_lines(path)
    it = iter(lines)
    for header in it:
        try:
            values = next(it)
        except StopIteration:
            break
        if ":" not in header:
            continue
        category, keys = header.split(":", 1)
        _, vals = values.split(":", 1)
        for k, v in zip(keys.split(), vals.split(), strict=False):
            try:
                out[f"{category.strip()}_{k}"] = int(v)
            except ValueError:
                continue
    return out


def collect() -> dict[str, dict]:
    per_iface = _read_dev()
    tcp: dict[str, int] = {}
    try:
        merged = {
            **_read_paired(PROC / "net/netstat"),
            **_read_paired(PROC / "net/snmp"),
        }
        for k in TCP_KEYS_OF_INTEREST:
            if k in merged:
                tcp[k] = merged[k]
    except OSError:
        pass
    try:
        for line in read_lines(PROC / "net/sockstat"):
            if line.startswith("TCP:"):
                parts = line.split()
                for i in range(1, len(parts) - 1, 2):
                    tcp[f"sockstat_{parts[i]}"] = int(parts[i + 1])
    except OSError:
        pass
    return {"per_interface": per_iface, "tcp": tcp}
