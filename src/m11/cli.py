"""Argparse entrypoint. Execution gates remain closed during source construction."""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

from harnessrun import ContractError, strict_json


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="m11", description="Runtime-unverified M11 source checkpoint")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("status")
    demo = commands.add_parser("demo")
    demo.add_argument("--offline", action="store_true", required=True)
    analyze = commands.add_parser("analyze")
    analyze.add_argument("input", type=Path)
    report = commands.add_parser("report")
    report.add_argument("input", type=Path)
    report.add_argument("--format", choices=("html", "markdown", "json"), default="html")
    for name in ("admit", "intake", "treat", "probe", "run"):
        commands.add_parser(name)
    for name, operations in (("suite", ("validate",)), ("long", ("run",)),
                             ("prereg", ("freeze", "amend", "verify")),
                             ("ledger", ("reconcile",)), ("authorize", ("check",))):
        group = commands.add_parser(name)
        operations_parser = group.add_subparsers(dest="operation", required=True)
        for operation in operations:
            operations_parser.add_parser(operation)
    return parser


def _read_export(path: Path) -> dict:
    if path.suffix.lower() != ".json" or any(part.lower() in {".env", ".ssh", ".aws", "auth", "credentials"} for part in path.parts):
        raise ContractError("only an explicit public JSON result export is accepted")
    with path.open("rb") as stream:
        raw = stream.read(10 * 1024 * 1024 + 1)
    payload = strict_json(raw)
    if not isinstance(payload, dict):
        raise ContractError("public result export must be a JSON object")
    return payload


def _refusal(command: str, reason: str) -> int:
    print(json.dumps({"status": "refused", "command": command,
        "reason": reason, "runtime_verified": False, "p0": "PENDING"}), file=sys.stderr)
    return 3


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "status":
        print(json.dumps({"status": "source construction; runtime-unverified",
            "p0": "PENDING", "native_dispatch": "refused", "spend_authorized_usd": "0"}))
        return 0
    # Source permission is never confused with permission to execute the instrument.
    if args.command not in {"demo", "analyze", "report"}:
        return _refusal(args.command, "P0/runtime activation unavailable; consumer command integration pending")
    try:
        if args.command == "demo":
            from .demo import build_demo
            print(json.dumps(build_demo(), ensure_ascii=False, sort_keys=True, allow_nan=False))
            return 0
        analysis = importlib.import_module("m11.analysis")
        result = analysis.analyze_export(_read_export(args.input))
        if args.command == "analyze":
            print(json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False))
        else:
            report = importlib.import_module("m11.report")
            renderer = {"html": report.render_html, "markdown": report.render_markdown,
                        "json": report.render_json}[args.format]
            print(renderer(result))
        return 0
    except ModuleNotFoundError:
        return _refusal(args.command, "declared consumer or dependency unavailable; source integration pending")
    except (ContractError, ValueError, TypeError, OSError, AttributeError):
        return _refusal(args.command, "input/consumer contract failed; no result claimed")


if __name__ == "__main__":
    raise SystemExit(main())
