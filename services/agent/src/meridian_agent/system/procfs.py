"""Foundation /proc and /sys helpers. Synchronous — these are kernel pseudo-files."""
from __future__ import annotations

from pathlib import Path

PROC = Path("/proc")
SYS = Path("/sys")


def read_text(path: Path) -> str:
    with path.open("r", encoding="utf-8") as f:
        return f.read()


def read_lines(path: Path) -> list[str]:
    return read_text(path).splitlines()


def read_kv(path: Path, sep: str = ":") -> dict[str, str]:
    """Parse meminfo / status-style key:value files."""
    out: dict[str, str] = {}
    for line in read_lines(path):
        if sep not in line:
            continue
        k, v = line.split(sep, 1)
        out[k.strip()] = v.strip()
    return out


def first_int(s: str) -> int:
    """Extract the leading integer (e.g. '12345 kB' -> 12345)."""
    return int(s.split()[0])
