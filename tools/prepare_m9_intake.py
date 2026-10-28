"""Source-only staged M9 inventory checker; never imports or enables the ledger.

Not executed during Dirty construction. Future authorized use is limited to an
explicit staged directory inside this checkout, never another app or worktree.
Matching a caller's hashes does not authenticate source origin/API/rights/tests.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re

PIN = "a0f2bd01b2dcadf9b778cab9cf7ff9a416fe6c30"
MAX_INVENTORY_BYTES = 1024 * 1024
MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_TOTAL_BYTES = 64 * 1024 * 1024
MAX_FILES = 512
_DIGEST = re.compile(r"[0-9a-f]{64}")
_OPAQUE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,255}")
_FORBIDDEN = {".git", ".ssh", "auth", "credentials", "credential", "tokens", "token", "secrets", "secret"}


class IntakeRefusal(ValueError):
    """An input cannot be inspected safely or does not match the staged contract."""


def _forbidden_component(name: str) -> bool:
    # Ordinary Win32 lookup can trim trailing dots/spaces; refuse that spelling
    # before any lookup rather than normalizing it into a credential directory.
    return (
        not name or name.endswith((" ", ".")) or ":" in name
        or any(ord(char) < 32 or ord(char) == 127 for char in name)
        or name.startswith(".") or name.casefold() in _FORBIDDEN
        or PurePosixPath(name).stem.casefold() in _FORBIDDEN
    )


def _no_links(path: Path) -> None:
    if path.is_symlink() or (os.name == "nt" and path.is_junction()):
        raise IntakeRefusal("symlink_or_junction_not_allowed")


def _exact_relative_parts(candidate: Path, root: Path) -> tuple[str, ...]:
    # WindowsPath containment folds case even when NTFS has distinct sensitive
    # sibling directories. Compare actual component strings conservatively;
    # relative caller paths already inherit the trusted canonical root casing.
    prefix = root.parts
    parts = candidate.parts
    if len(parts) < len(prefix) or parts[:len(prefix)] != prefix:
        raise IntakeRefusal("exact_checkout_root_components_required")
    return parts[len(prefix):]


def _bounded_path(candidate: Path, root: Path) -> Path:
    # Reject lexically before resolving, so an arbitrary path cannot be used to
    # explore another application's files. Check every allowed ancestor too.
    if ".." in candidate.parts or not candidate.is_absolute():
        raise IntakeRefusal("path_outside_explicit_checkout_boundary")
    relative_parts = _exact_relative_parts(candidate, root)
    current = root
    for part in relative_parts:
        if _forbidden_component(part):
            raise IntakeRefusal("hidden_or_credential_ancestor_forbidden")
        current /= part
        _no_links(current)
    resolved = candidate.resolve(strict=True)
    resolved_parts = _exact_relative_parts(resolved, root)
    # Canonical components must also pass; an alternate filesystem spelling is
    # not permission to read a forbidden root through a different visible name.
    if any(_forbidden_component(part) for part in resolved_parts):
        raise IntakeRefusal("resolved_hidden_or_credential_ancestor_forbidden")
    return resolved


def _read(path: Path, limit: int) -> bytes:
    if not path.is_file() or path.stat().st_size > limit:
        raise IntakeRefusal("required_regular_file_missing_or_over_limit")
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise IntakeRefusal("file_over_limit")
    return data


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise IntakeRefusal("duplicate_inventory_key")
        result[key] = value
    return result


def _file_entry(entry: object) -> tuple[str, str, str]:
    if not isinstance(entry, dict) or set(entry) != {"path", "sha256", "role"}:
        raise IntakeRefusal("invalid_closed_file_entry")
    name, digest, role = entry["path"], entry["sha256"], entry["role"]
    if not isinstance(name, str) or not isinstance(digest, str) or not _DIGEST.fullmatch(digest):
        raise IntakeRefusal("invalid_file_name_or_digest")
    relative = PurePosixPath(name)
    parts = name.split("/")
    if relative.is_absolute() or "\\" in name or ":" in name or any(p in ("", ".", "..") for p in parts):
        raise IntakeRefusal("noncanonical_inventory_path")
    if any(_forbidden_component(p) for p in parts):
        raise IntakeRefusal("credential_hidden_or_repository_path_forbidden")
    if relative.suffix.casefold() in {".pem", ".key", ".env", ".pfx", ".p12"}:
        raise IntakeRefusal("credential_file_forbidden")
    if role == "ledger_source":
        allowed = name.startswith("src/m9/ledger/") and relative.suffix == ".py"
    elif role == "copied_test":
        allowed = name.startswith("tests/") and relative.suffix == ".py"
    elif role == "attribution":
        allowed = name in {"NOTICE", "NOTICE.md", "ATTRIBUTION.md", "LICENSE", "COPYING"}
    else:
        allowed = False
    if not allowed:
        raise IntakeRefusal("path_not_in_declared_source_test_or_attribution_closure")
    return name, digest, role


def inspect_staged(staged_root: str, inventory_sha256: str) -> dict[str, object]:
    """Read bounded explicitly inventoried source bytes only; execute none.

    The trusted code root comes from this script, never from a caller flag.
    No output, copying, vendoring, money mutation or resource activation occurs.
    """
    if not _DIGEST.fullmatch(inventory_sha256):
        raise IntakeRefusal("real_inventory_digest_required")
    checkout = Path(__file__).resolve().parents[1]
    candidate = Path(staged_root)
    candidate = candidate if candidate.is_absolute() else checkout / candidate
    stage = _bounded_path(candidate, checkout)
    if stage == checkout or not stage.is_dir():
        raise IntakeRefusal("explicit_staged_subdirectory_required")
    manifest = _bounded_path(stage / "M9-INVENTORY.json", checkout)
    raw = _read(manifest, MAX_INVENTORY_BYTES)
    if hashlib.sha256(raw).hexdigest() != inventory_sha256:
        raise IntakeRefusal("inventory_digest_mismatch")
    inventory = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object)
    required = {"schema_version", "source_commit", "provenance_ref", "redistribution_status", "files"}
    if not isinstance(inventory, dict) or set(inventory) != required:
        raise IntakeRefusal("invalid_closed_inventory")
    if inventory["schema_version"] != "m11-m9-intake/1" or inventory["source_commit"] != PIN:
        raise IntakeRefusal("inventory_version_or_source_pin_mismatch")
    provenance = inventory["provenance_ref"]
    if not isinstance(provenance, str) or not _OPAQUE.fullmatch(provenance):
        raise IntakeRefusal("real_opaque_source_provenance_reference_required")
    if inventory["redistribution_status"] != "private_only_unresolved_public_rights":
        raise IntakeRefusal("no_public_rights_assertion_permitted")
    records = inventory["files"]
    if not isinstance(records, list) or not 1 <= len(records) <= MAX_FILES:
        raise IntakeRefusal("bounded_nonempty_inventory_required")
    entries = [_file_entry(entry) for entry in records]
    names = {name for name, _, _ in entries}
    if len(names) != len(entries):
        raise IntakeRefusal("duplicate_inventory_path")
    roles = [role for _, _, role in entries]
    if any(role not in roles for role in ("ledger_source", "copied_test", "attribution")):
        raise IntakeRefusal("source_copied_test_and_attribution_inventory_required")
    observed: set[str] = set()
    expected_directories = {
        parent.as_posix()
        for name in names
        for parent in PurePosixPath(name).parents
        if parent.as_posix() != "."
    }
    # Inspect names only for omitted entries; unlisted file contents are never read.
    for directory, subdirs, files in os.walk(stage, followlinks=False):
        for name in subdirs:
            child = Path(directory) / name
            _no_links(child)
            if _forbidden_component(name):
                raise IntakeRefusal("forbidden_staged_directory")
            if child.relative_to(stage).as_posix() not in expected_directories:
                raise IntakeRefusal("directory_outside_inventory_closure")
        for name in files:
            child = Path(directory) / name
            _no_links(child)
            if child != manifest:
                observed.add(child.relative_to(stage).as_posix())
            if len(observed) > MAX_FILES:
                raise IntakeRefusal("staged_file_count_exceeds_bound")
    if names != observed:
        raise IntakeRefusal("staged_tree_and_inventory_names_differ")
    total = 0
    for name, expected, _ in entries:
        path = _bounded_path(stage.joinpath(*PurePosixPath(name).parts), checkout)
        data = _read(path, min(MAX_FILE_BYTES, MAX_TOTAL_BYTES - total))
        total += len(data)
        if total > MAX_TOTAL_BYTES:
            raise IntakeRefusal("total_staged_bytes_exceed_bound")
        if hashlib.sha256(data).hexdigest() != expected:
            raise IntakeRefusal("staged_file_digest_mismatch")
    return {
        "schema_version": "m11-m9-intake-report/1",
        "disposition": "caller_inventory_hashes_match_source_origin_unverified",
        "source_commit_claim": PIN,
        "inventory_sha256": inventory_sha256,
        "source_file_count": roles.count("ledger_source"),
        "copied_test_file_count": roles.count("copied_test"),
        "total_bytes_hashed": total,
        "operational": False,
        "ledger_available": False,
        "executed": False,
        "unavailable": ["independent_source_origin_authentication", "exact_M9_API_mapping", "copied_test_execution", "public_redistribution_rights", "atomic_M9_claim_runtime_authority"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Future staged M9 hash inventory inspection; never imports/enables M9")
    parser.add_argument("--staged-root", required=True)
    parser.add_argument("--inventory-sha256", required=True)
    args = parser.parse_args()
    try:
        report = inspect_staged(args.staged_root, args.inventory_sha256)
    except (IntakeRefusal, OSError, UnicodeError, json.JSONDecodeError) as exc:
        # Do not echo file contents, arbitrary paths or exception payloads.
        reason = str(exc) if isinstance(exc, IntakeRefusal) else "staged_inventory_unavailable_or_malformed"
        print(json.dumps({"operational": False, "ledger_available": False, "disposition": "refused", "reason": reason}))
        return 2
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
