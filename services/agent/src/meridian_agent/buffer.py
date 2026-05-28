"""Disk-backed ring buffer for probe results.

Format:
  * One file per segment (default 16 MiB), named segment-<ms_epoch>.log
  * Each record: <4-byte big-endian uint32 length><NDJSON bytes>
  * Oldest segments evicted when total size exceeds buffer.max_bytes
  * fsync every N writes (durability vs throughput tradeoff)
"""
from __future__ import annotations

import asyncio
import io
import json
import os
import struct
import time
from pathlib import Path

import structlog

from meridian_agent.config import BufferConfig
from meridian_agent.probes.base import ProbeResult

log = structlog.get_logger(__name__)

SEGMENT_SIZE_BYTES = 16 * 1024 * 1024
LEN_PREFIX = struct.Struct("!I")
FSYNC_EVERY_N = 64


class ResultBuffer:
    def __init__(self, cfg: BufferConfig) -> None:
        self._cfg = cfg
        self._lock = asyncio.Lock()
        self._current_path: Path | None = None
        self._current_file: io.BufferedWriter | None = None
        self._writes_since_fsync = 0

    async def open(self) -> None:
        self._cfg.path.mkdir(parents=True, exist_ok=True)
        self._rotate_if_needed(force=True)
        await self._enforce_size_cap()
        log.info("buffer.opened", path=str(self._cfg.path))

    async def close(self) -> None:
        async with self._lock:
            self._close_current()

    async def write(self, result: ProbeResult) -> None:
        payload = json.dumps(result.to_dict(), separators=(",", ":")).encode("utf-8")
        frame = LEN_PREFIX.pack(len(payload)) + payload
        async with self._lock:
            self._rotate_if_needed()
            assert self._current_file is not None
            self._current_file.write(frame)
            self._writes_since_fsync += 1
            if self._writes_since_fsync >= FSYNC_EVERY_N:
                self._current_file.flush()
                os.fsync(self._current_file.fileno())
                self._writes_since_fsync = 0

    async def drain(self, batch_size: int) -> list[dict]:
        """Read up to batch_size records from sealed segments (non-destructive)."""
        out: list[dict] = []
        async with self._lock:
            for seg in sorted(self._cfg.path.glob("segment-*.log")):
                if seg == self._current_path:
                    continue
                with seg.open("rb") as f:
                    while len(out) < batch_size:
                        lp = f.read(LEN_PREFIX.size)
                        if len(lp) < LEN_PREFIX.size:
                            break
                        (n,) = LEN_PREFIX.unpack(lp)
                        data = f.read(n)
                        if len(data) < n:
                            log.warning("buffer.partial_record", segment=str(seg))
                            break
                        try:
                            out.append(json.loads(data))
                        except json.JSONDecodeError:
                            log.warning("buffer.corrupt_record", segment=str(seg))
                if len(out) >= batch_size:
                    break
        return out

    async def ack(self) -> None:
        """Delete sealed segments after successful upstream delivery."""
        async with self._lock:
            for seg in sorted(self._cfg.path.glob("segment-*.log")):
                if seg == self._current_path:
                    break
                try:
                    seg.unlink()
                except FileNotFoundError:
                    pass

    def _close_current(self) -> None:
        if self._current_file is not None:
            self._current_file.flush()
            os.fsync(self._current_file.fileno())
            self._current_file.close()
            self._current_file = None

    def _rotate_if_needed(self, *, force: bool = False) -> None:
        if not force and self._current_file is not None:
            if self._current_file.tell() < SEGMENT_SIZE_BYTES:
                return
        self._close_current()
        ts = int(time.time() * 1000)
        self._current_path = self._cfg.path / f"segment-{ts:013d}.log"
        self._current_file = self._current_path.open("ab", buffering=0)

    async def _enforce_size_cap(self) -> None:
        async with self._lock:
            segs = sorted(self._cfg.path.glob("segment-*.log"))
            total = sum(s.stat().st_size for s in segs)
            for seg in segs:
                if total <= self._cfg.max_bytes:
                    break
                if seg == self._current_path:
                    continue
                size = seg.stat().st_size
                try:
                    seg.unlink()
                    total -= size
                    log.warning("buffer.evicted", segment=str(seg), size=size)
                except FileNotFoundError:
                    pass
