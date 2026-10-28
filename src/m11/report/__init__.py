"""Pure, offline presentations of analysis records; runtime-unverified source.

Analysis owns eligibility and calculations. These renderers never fetch artifacts,
resolve references, run graders, grant admission, or manufacture missing results.
"""

from __future__ import annotations

import html
import json
import math
from collections.abc import Mapping
from typing import Any

__all__ = ["render_html", "render_markdown", "render_json"]

_NOTICE = (
    "Source-phase disposition: accepted for construction, independence PENDING - Roy, "
    "runtime-unverified. This labels construction only, never validation of supplied observations. "
    "A delegated stand-in is not human-independent; this renderer appoints no reviewer or verifier. "
    "P0 and K/L execution acceptance "
    "remain deferred. Gate records do not authorize execution or publication. "
    "Missing values remain unknown; list-price estimates are not actual charges."
)
_ORDER = (
    "schema_version", "campaign_id", "mode", "experiment_kind", "status",
    "construction_status", "construction_context", "unavailable_reasons", "limitations", "provenance",
    "groups", "comparisons", "trajectories", "claims", "planned_cells", "attempts",
)
_INFERENCE_KEYS = frozenset({
    "p_value", "pvalue", "confidence_interval", "bootstrap_interval",
    "wilson_interval", "mcnemar", "inferential", "inference",
    "inferential_claim", "interval", "ci", "bootstrap", "wilson",
    "primary_effect", "task_weighted_effect", "mcnemar_p_value",
})


def _validate(value: Any) -> None:
    """Accept only finite JSON-like data, without lossy fallback conversion."""
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Non-finite numbers must have an explicit unavailable reason")
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("Report keys must be strings")
            _validate(item)
        return
    if isinstance(value, list):
        for item in value:
            _validate(item)
        return
    raise TypeError("Reports require JSON-like data; serialize typed records first")


def _prepare(result: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(result, Mapping):
        raise TypeError("Analysis result must be a mapping")
    _validate(result)
    if result.get("schema_version") != "m11-analysis/1":
        raise ValueError("Unsupported analysis schema_version")
    if result.get("mode") not in {"SIMULATED", "MEASURED"}:
        raise ValueError("Analysis mode must be explicit SIMULATED or MEASURED")
    mode = result["mode"]

    def inspect(value: Any) -> None:
        if isinstance(value, Mapping):
            if "mode" in value and value["mode"] != mode:
                raise ValueError("Mixed or unresolved provenance mode in report")
            for key, item in value.items():
                if mode == "SIMULATED" and key.lower() in _INFERENCE_KEYS and item not in (None, [], {}):
                    raise ValueError("SIMULATED reports cannot contain inferential results")
                inspect(item)
        elif isinstance(value, list):
            for item in value:
                inspect(item)

    inspect(result)
    return dict(result)


def _items(value: Mapping[str, Any]) -> list[tuple[str, Any]]:
    """Keep schedule/list order; deterministically order mapping keys."""
    rank = {key: index for index, key in enumerate(_ORDER)}
    return sorted(value.items(), key=lambda pair: (rank.get(pair[0], len(rank)), pair[0]))


def _scalar(value: Any) -> str:
    if value is None:
        return "null (unknown / unavailable; see supplied reason)"
    return json.dumps(value, ensure_ascii=False, allow_nan=False)


def _html_value(value: Any) -> str:
    if isinstance(value, Mapping):
        if not value:
            return "<p>Empty object (no supplied records).</p>"
        return "<dl>" + "".join(
            "<dt>" + html.escape(key, quote=True) + "</dt><dd>" + _html_value(item) + "</dd>"
            for key, item in _items(value)
        ) + "</dl>"
    if isinstance(value, list):
        if not value:
            return "<p>Empty list (no supplied records).</p>"
        return "<ol>" + "".join("<li>" + _html_value(item) + "</li>" for item in value) + "</ol>"
    return "<span class=\"value\">" + html.escape(_scalar(value), quote=True) + "</span>"


def _number(value: Any) -> bool:
    return (isinstance(value, int) and not isinstance(value, bool)) or (
        isinstance(value, float) and math.isfinite(value)
    )


def _trajectory_svg(trajectory: Any, index: int) -> str:
    """Plot explicit point values only; gaps are never imputed or connected."""
    title = f"Trajectory {index + 1}: supplied checkpoint values"
    points = trajectory.get("points") if isinstance(trajectory, Mapping) else None
    if not isinstance(points, list):
        return "<p>Trajectory chart unavailable: no explicit points array; full record follows.</p>"
    known = [point for point in points if isinstance(point, Mapping) and _number(point.get("value"))]
    if not known:
        return "<p>Trajectory chart unavailable: all supplied point values are unknown.</p>"
    values = [point["value"] for point in known]
    lower, upper = min(values), max(values)
    # Rescale to avoid subtraction overflow while preserving supplied finite values.
    scale = max(abs(lower), abs(upper), 1)
    lo, hi = lower / scale, upper / scale
    span = hi - lo
    marks = []
    previous: tuple[float, float] | None = None
    for position, point in enumerate(points):
        if not isinstance(point, Mapping) or not _number(point.get("value")):
            previous = None
            continue
        x = 48 + 540 * (position / max(len(points) - 1, 1))
        y = 100 if span == 0 else 164 - 128 * ((point["value"] / scale - lo) / span)
        if previous is not None:
            marks.append(f'<line x1="{previous[0]:.3f}" y1="{previous[1]:.3f}" x2="{x:.3f}" y2="{y:.3f}" stroke="currentColor"/>')
        label = html.escape(_scalar(point), quote=True)
        marks.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="4"><title>{label}</title></circle>')
        previous = (x, y)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 220" role="img" '
        f'aria-label="{html.escape(title, quote=True)}"><title>{html.escape(title)}</title>'
        '<path d="M48 24V180H600" fill="none" stroke="currentColor"/>'
        f'<text x="4" y="24">{html.escape(str(upper))}</text>'
        f'<text x="4" y="180">{html.escape(str(lower))}</text>'
        '<text x="48" y="208">Supplied point order; gaps remain unknown</text>'
        + "".join(marks) + "</svg>"
    )


def render_html(result: Mapping[str, Any]) -> str:
    """Return a standalone static report without scripts, links or remote assets."""
    data = _prepare(result)
    sections = []
    for key, value in _items(data):
        charts = ""
        if key == "trajectories" and isinstance(value, list):
            charts = "".join(_trajectory_svg(item, index) for index, item in enumerate(value))
        sections.append("<section><h2>" + html.escape(key) + "</h2>" + charts + _html_value(value) + "</section>")
    mode = html.escape(data["mode"])
    claim = "Descriptive demonstration only; no inferential or live-performance claims." if data["mode"] == "SIMULATED" else "MEASURED is the supplied provenance label; rendering does not establish acceptance."
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>M11 analysis report</title><style>'
        'body{font:16px system-ui,sans-serif;max-width:76rem;margin:2rem auto;padding:0 1rem;line-height:1.5}'
        'dt{font-weight:700}dd{margin-bottom:1rem}li{margin-bottom:.7rem}'
        '.value{white-space:pre-wrap;overflow-wrap:anywhere}svg{width:100%;max-width:48rem;height:auto}'
        'section{border-top:1px solid #aaa;padding-top:1rem}aside{border:2px solid #555;padding:1rem}'
        '</style></head><body><h1>M11 analysis report — ' + mode + '</h1><aside><p>'
        + html.escape(_NOTICE) + '</p><p>' + html.escape(claim)
        + '</p><p>Interpret class companions, missingness, usage/model coverage, costs and gate evidence together. '
        'Values, denominators and unavailable reasons below are supplied by analysis, not inferred by rendering.</p></aside>'
        + "".join(sections) + '</body></html>\n'
    )


def _markdown_text(text: str) -> str:
    # Encode imported angle brackets/entities first; escape all Markdown control
    # punctuation so imported links, fences, tables and raw HTML remain inert text.
    escaped = html.escape(text, quote=False)
    return "".join("\\" + char if char in "\\`*_{}[]()#+-.!|>~" else char for char in escaped).replace("\r", "&#13;").replace("\n", "&#10;")


def _markdown_value(value: Any, depth: int = 0) -> list[str]:
    indent = "  " * depth
    if isinstance(value, Mapping):
        if not value:
            return [indent + "- Empty object (no supplied records)."]
        lines = []
        for key, item in _items(value):
            lines.append(indent + "- **" + _markdown_text(key) + "**")
            lines.extend(_markdown_value(item, depth + 1))
        return lines
    if isinstance(value, list):
        if not value:
            return [indent + "- Empty list (no supplied records)."]
        lines = []
        for index, item in enumerate(value):
            lines.append(indent + f"- Record {index + 1}")
            lines.extend(_markdown_value(item, depth + 1))
        return lines
    return [indent + "- " + _markdown_text(_scalar(value))]


def render_markdown(result: Mapping[str, Any]) -> str:
    """Return escaped Markdown with every record retained in supplied list order."""
    data = _prepare(result)
    notice = "SIMULATED: descriptive demonstration only; no inference or live-performance claims." if data["mode"] == "SIMULATED" else "MEASURED is supplied provenance, not rendering-established acceptance."
    return "# M11 analysis report\n\n" + _NOTICE + "\n\n" + notice + "\n\n" + "\n".join(_markdown_value(data)) + "\n"


def render_json(result: Mapping[str, Any]) -> str:
    """Serialize a separate JSON artifact, preserving nulls and every input field."""
    return json.dumps(_prepare(result), ensure_ascii=False, allow_nan=False, sort_keys=True, indent=2) + "\n"
