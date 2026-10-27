"""Private operator entry point; no permissive signature/admission CLI path."""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .admission import assess_gate
from .formats import Refusal, closed, parse_json
from .inventory import inspect_inventory


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="M11 private evaluation source tools")
    sub = parser.add_subparsers(dest="command", required=True)
    inspect = sub.add_parser("inspect", help="enumerated exact-byte hashes only, not admission")
    inspect.add_argument("--root", type=Path, required=True)
    inspect.add_argument("--manifest", type=Path, required=True)
    admit = sub.add_parser("admit", help="refuses absent external verifier/appointment context")
    admit.add_argument("--receipt", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "inspect":
            # Explicit input supplied by trusted operator; no recursive discovery.
            raw = args.manifest.read_bytes()
            manifest = closed(parse_json(raw), {"schema_version", "pack_id", "artifacts"},
                              "sealed manifest")
            if manifest["schema_version"] != "m11-sealed-pack/1":
                raise Refusal("unsupported sealed pack")
            result = inspect_inventory(args.root, manifest["artifacts"])
            status = 0
        else:
            result = asdict(assess_gate(None if args.receipt is None else args.receipt.read_bytes()))
            status = 2
        print(json.dumps(result, sort_keys=True))
        return status
    except (Refusal, OSError) as exc:
        print(json.dumps({"decision": "NO-GO", "reason": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
