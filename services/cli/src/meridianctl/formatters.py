"""Output formatters: table / json / yaml."""
from __future__ import annotations

import json
from typing import Any

import yaml
from rich.console import Console
from rich.table import Table

_console = Console()


def render_table(rows: list[dict[str, Any]], columns: list[str], title: str = "") -> None:
    if not rows:
        _console.print(f"[dim]no {title or 'rows'}[/dim]")
        return
    t = Table(title=title, show_header=True, header_style="bold")
    for c in columns:
        t.add_column(c)
    for r in rows:
        t.add_row(*[str(r.get(c, "")) for c in columns])
    _console.print(t)


def render_json(data: Any) -> None:
    print(json.dumps(data, indent=2, default=str))


def render_yaml(data: Any) -> None:
    print(yaml.safe_dump(data, sort_keys=False, default_flow_style=False))


def render(data: Any, format_: str, columns: list[str] | None = None, title: str = "") -> None:
    if format_ == "json":
        render_json(data)
    elif format_ == "yaml":
        render_yaml(data)
    elif isinstance(data, list) and columns:
        render_table(data, columns, title)
    else:
        render_json(data)
