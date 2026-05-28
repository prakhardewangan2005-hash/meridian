"""Probe class registry — supports both built-in and entry_point plugins."""
from __future__ import annotations

from importlib.metadata import entry_points

from meridian_agent.probes.base import Probe
from meridian_agent.probes.dns import DNSProbe
from meridian_agent.probes.http import HTTPProbe
from meridian_agent.probes.icmp import ICMPProbe
from meridian_agent.probes.tcp import TCPProbe
from meridian_agent.probes.traceroute import TracerouteProbe

BUILTINS: dict[str, type[Probe]] = {
    "dns": DNSProbe,
    "http": HTTPProbe,
    "icmp": ICMPProbe,
    "tcp": TCPProbe,
    "traceroute": TracerouteProbe,
}


def discover() -> dict[str, type[Probe]]:
    """Return built-ins merged with third-party probes registered under
    the 'meridian_agent.probes' entry point group."""
    registry = dict(BUILTINS)
    try:
        eps = entry_points(group="meridian_agent.probes")
    except TypeError:  # python <3.10 compat path
        return registry
    for ep in eps:
        try:
            cls = ep.load()
            if not (isinstance(cls, type) and issubclass(cls, Probe)):
                continue
            registry[ep.name] = cls
        except Exception:
            continue
    return registry
