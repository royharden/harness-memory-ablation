"""Pure treatment construction checks; no files, admission, or execution effects.

These source-only formats are not independent leak/admission evidence. Token
counts remain unknown unless supplied by a separately pinned tokenizer receipt.
"""

from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, StrictInt, field_validator, model_validator

from harnessrun import ContractError, canonical_json, sha256_bytes


class ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


def _digest(value: str) -> str:
    if len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise ValueError("expected lowercase SHA256")
    return value


def _relative(path: str) -> str:
    if not path or "\\" in path or ":" in path or path.startswith("/"):
        raise ValueError("treatment path must be POSIX workspace-relative")
    if any(p in ("", ".", "..") for p in path.split("/")):
        raise ValueError("ambiguous or escaping treatment path")
    return path


class Fact(ClosedModel):
    id: str
    type: Literal["decision", "convention", "gotcha"]
    status: Literal["current", "stale", "decoy"]
    provenance: str
    date: str
    value: str

    @field_validator("id", "provenance", "date", "value")
    @classmethod
    def nonempty(cls, value: str) -> str:
        if not value or "\x00" in value:
            raise ValueError("fact fields must be nonempty and NUL-free")
        return value


class TreatmentFile(ClosedModel):
    path: str
    sha256: str
    access: Literal["read_only", "read_write"]

    _path = field_validator("path")(_relative)
    _hash = field_validator("sha256")(_digest)


class TreatmentManifest(ClosedModel):
    version: Literal["treatment/1"] = "treatment/1"
    experiment_kind: Literal["task", "longitudinal"]
    arm_id: Literal["M0", "M1", "M2", "L0", "L1", "L2"]
    fact_set_sha256: str | None
    files: tuple[TreatmentFile, ...]
    byte_length: StrictInt
    native_token_count: StrictInt | None
    tokenizer_pin: str | None
    equality_receipt_sha256: str | None
    update_permission: Literal["none", "typed_memory_only"]
    discipline_sha256: str | None

    @field_validator("fact_set_sha256", "equality_receipt_sha256", "discipline_sha256")
    @classmethod
    def hashes(cls, value: str | None) -> str | None:
        return None if value is None else _digest(value)

    @model_validator(mode="after")
    def arm_rules(self) -> TreatmentManifest:
        if self.byte_length < 0 or (self.native_token_count is not None and self.native_token_count < 0):
            raise ValueError("negative treatment count")
        if self.arm_id not in ("M0", "L0") and (self.native_token_count is None) != (self.tokenizer_pin is None):
            raise ValueError("token count and tokenizer pin must be known together")
        if self.tokenizer_pin == "":
            raise ValueError("empty tokenizer pin")
        expected = ("M0", "M1", "M2") if self.experiment_kind == "task" else ("L0", "L1", "L2")
        if self.arm_id not in expected:
            raise ValueError("arm does not belong to experiment")
        if len({f.path for f in self.files}) != len(self.files):
            raise ValueError("duplicate treatment path")
        absent = self.arm_id in ("M0", "L0")
        if absent:
            if self.files or self.byte_length or self.fact_set_sha256 is not None or self.equality_receipt_sha256 is not None or self.discipline_sha256 is not None:
                raise ValueError("baseline memory must be absent")
            if self.native_token_count != 0 or self.tokenizer_pin is not None or self.update_permission != "none":
                raise ValueError("baseline injects zero tokens and cannot update memory")
        else:
            if not self.files or self.byte_length == 0 or self.fact_set_sha256 is None:
                raise ValueError("memory arm needs nonempty hash-bound content")
            if self.arm_id in ("M2", "L2") and self.discipline_sha256 is None:
                raise ValueError("structured arm needs pinned discipline")
            permission = "typed_memory_only" if self.arm_id == "L2" else "none"
            if self.update_permission != permission:
                raise ValueError("only L2 permits typed memory updates")
            if self.arm_id != "L2" and any(f.access != "read_only" for f in self.files):
                raise ValueError("treatment access conflicts with arm permission")
            if self.arm_id == "L2" and sum(f.access == "read_write" for f in self.files) != 1:
                raise ValueError("L2 permits exactly one typed-memory writable file")
        return self


def canonical_facts(facts: tuple[Fact, ...]) -> bytes:
    if len({f.id for f in facts}) != len(facts):
        raise ContractError("duplicate fact ID")
    return canonical_json([f.model_dump(mode="json") for f in sorted(facts, key=lambda f: f.id)])


def render_fact_set(facts: tuple[Fact, ...], representation: Literal["prose", "typed"], *, ballast: bytes = b"") -> bytes:
    """Render six fields exactly; ballast can contain ASCII whitespace only."""
    canonical_facts(facts)
    if any(byte not in b" \t\n\r" for byte in ballast):
        raise ContractError("neutral ballast must be whitespace, never instructions or facts")
    ordered = sorted(facts, key=lambda f: f.id)
    if representation == "typed":
        rendered = canonical_json([f.model_dump(mode="json") for f in ordered]) + b"\n"
    elif representation == "prose":
        # JSON string quoting makes embedded newlines/delimiters unambiguous.
        blocks = []
        for fact in ordered:
            fields = fact.model_dump(mode="json")
            blocks.append("Fact\n" + "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in fields.items()))
        rendered = ("\n\n".join(blocks) + "\n").encode("utf-8")
    else:
        raise ContractError("unsupported fact representation")
    return rendered + ballast


class TreatmentContent(ClosedModel):
    """A single generated fact representation, without discipline bytes."""

    representation: Literal["prose", "typed"]
    facts: tuple[Fact, ...]
    rendered: bytes
    ballast: bytes

    @model_validator(mode="after")
    def exact_render(self) -> TreatmentContent:
        if self.rendered != render_fact_set(self.facts, self.representation, ballast=self.ballast):
            raise ValueError("rendered bytes differ from declared six-field facts/ballast")
        return self


class EqualityReceipt(ClosedModel):
    version: Literal["treatment-equality/1"] = "treatment-equality/1"
    left_manifest_sha256: str
    right_manifest_sha256: str
    fact_set_sha256: str
    fact_ids: tuple[str, ...]
    verdict: Literal["equal"] = "equal"
    left_byte_count: StrictInt
    right_byte_count: StrictInt
    relative_byte_difference: float
    left_ballast_sha256: str
    right_ballast_sha256: str
    leak_check_receipt_sha256: str
    left_token_count: StrictInt | None
    right_token_count: StrictInt | None
    left_tokenizer_pin: str | None
    right_tokenizer_pin: str | None
    token_unknown_reason: str | None

    _hashes = field_validator("left_manifest_sha256", "right_manifest_sha256", "fact_set_sha256", "left_ballast_sha256", "right_ballast_sha256", "leak_check_receipt_sha256")(_digest)

    @model_validator(mode="after")
    def consistency(self) -> EqualityReceipt:
        if len(set(self.fact_ids)) != len(self.fact_ids) or any(not key for key in self.fact_ids):
            raise ValueError("fact IDs must be unique and nonempty")
        low, high = sorted((self.left_byte_count, self.right_byte_count))
        if low <= 0 or high * 10 > low * 11:
            raise ValueError("invalid equality byte tolerance")
        if self.relative_byte_difference != (high - low) / low:
            raise ValueError("inconsistent relative byte difference")
        unknown = self.left_token_count is None or self.right_token_count is None
        if unknown != (self.token_unknown_reason is not None):
            raise ValueError("unknown token count requires explicit reason")
        for count, pin in ((self.left_token_count, self.left_tokenizer_pin), (self.right_token_count, self.right_tokenizer_pin)):
            if (count is None) != (pin is None) or (count is not None and count < 0) or pin == "":
                raise ValueError("token count/pin mismatch")
        return self


def treatment_manifest_hash(manifest: TreatmentManifest) -> str:
    """Hash the manifest with its receipt slot null, avoiding a circular hash."""
    data = manifest.model_dump(mode="json")
    data["equality_receipt_sha256"] = None
    return sha256_bytes(canonical_json(data))


def validate_treatment(manifest: TreatmentManifest, files: dict[str, bytes], *, require_equality_receipt: bool = True) -> None:
    if set(files) != {f.path for f in manifest.files}:
        raise ContractError("memory file inventory differs from manifest (M0/L0 requires absence)")
    if sum(len(blob) for blob in files.values()) != manifest.byte_length:
        raise ContractError("treatment byte length mismatch")
    for entry in manifest.files:
        if sha256_bytes(files[entry.path]) != entry.sha256:
            raise ContractError("treatment file hash mismatch")
    if require_equality_receipt and manifest.arm_id in ("M1", "M2") and manifest.equality_receipt_sha256 is None:
        raise ContractError("paired task arm needs equality receipt")


def validate_equality_receipt(left: TreatmentManifest, right: TreatmentManifest, receipt: EqualityReceipt) -> None:
    """Bind the finalized pair to its exact closed receipt, not just any hash."""
    if (left.arm_id, right.arm_id) != ("M1", "M2"):
        raise ContractError("equality receipt requires ordered M1/M2")
    receipt_hash = sha256_bytes(canonical_json(receipt.model_dump(mode="json")))
    if left.equality_receipt_sha256 != receipt_hash or right.equality_receipt_sha256 != receipt_hash:
        raise ContractError("treatment equality receipt digest mismatch")
    if (treatment_manifest_hash(left), treatment_manifest_hash(right)) != (receipt.left_manifest_sha256, receipt.right_manifest_sha256):
        raise ContractError("equality receipt binds different manifest bytes")
    if left.fact_set_sha256 != right.fact_set_sha256 or left.fact_set_sha256 != receipt.fact_set_sha256:
        raise ContractError("equality receipt fact hash mismatch")
    if (left.byte_length, right.byte_length) != (receipt.left_byte_count, receipt.right_byte_count):
        raise ContractError("equality receipt length mismatch")
    if (left.native_token_count, right.native_token_count, left.tokenizer_pin, right.tokenizer_pin) != (
        receipt.left_token_count, receipt.right_token_count, receipt.left_tokenizer_pin, receipt.right_tokenizer_pin
    ):
        raise ContractError("equality receipt tokenizer evidence mismatch")


def compare_treatments(left: TreatmentManifest, right: TreatmentManifest, left_content: TreatmentContent, right_content: TreatmentContent, *, left_files: dict[str, bytes], right_files: dict[str, bytes], leak_check_receipt_sha256: str) -> EqualityReceipt:
    """Check paired task treatments. A supplied leak hash is a reference, not proof."""
    _digest(leak_check_receipt_sha256)
    if (left.arm_id, right.arm_id) != ("M1", "M2"):
        raise ContractError("task equality requires ordered M1/M2 pair")
    if (left_content.representation, right_content.representation) != ("prose", "typed"):
        raise ContractError("M1 is prose and M2 is typed")
    validate_treatment(left, left_files, require_equality_receipt=False)
    validate_treatment(right, right_files, require_equality_receipt=False)
    for manifest, content, files in ((left, left_content, left_files), (right, right_content, right_files)):
        if content.rendered not in files.values():
            raise ContractError("fact representation is not an exact treatment file")
        if sha256_bytes(canonical_facts(content.facts)) != manifest.fact_set_sha256:
            raise ContractError("declared fact-set hash mismatch")
        for entry in manifest.files:
            if files[entry.path] != content.rendered and entry.sha256 != manifest.discipline_sha256:
                raise ContractError("unaccounted treatment content beyond facts/discipline")
        if manifest.discipline_sha256 is not None and not any(f.sha256 == manifest.discipline_sha256 for f in manifest.files):
            raise ContractError("pinned discipline bytes absent from treatment")
    if canonical_facts(left_content.facts) != canonical_facts(right_content.facts):
        raise ContractError("six-field fact mismatch, including stale/decoy status")
    low, high = sorted((left.byte_length, right.byte_length))
    if low <= 0 or high * 10 > low * 11:
        raise ContractError("paired treatment bytes exceed symmetric ten percent tolerance")
    return EqualityReceipt(
        left_manifest_sha256=treatment_manifest_hash(left), right_manifest_sha256=treatment_manifest_hash(right),
        fact_set_sha256=left.fact_set_sha256, fact_ids=tuple(sorted(f.id for f in left_content.facts)),
        left_byte_count=left.byte_length, right_byte_count=right.byte_length,
        relative_byte_difference=(high - low) / low,
        left_ballast_sha256=sha256_bytes(left_content.ballast), right_ballast_sha256=sha256_bytes(right_content.ballast),
        leak_check_receipt_sha256=leak_check_receipt_sha256,
        left_token_count=left.native_token_count, right_token_count=right.native_token_count,
        left_tokenizer_pin=left.tokenizer_pin, right_tokenizer_pin=right.tokenizer_pin,
        token_unknown_reason="native token counts unavailable" if left.native_token_count is None or right.native_token_count is None else None,
    )


class MemoryTransition(ClosedModel):
    before_sha256: str
    after_sha256: str
    changed: bool
    disposition: Literal["unchanged", "permitted_update", "memory_write_invalid"]
    reason: str

    _hashes = field_validator("before_sha256", "after_sha256")(_digest)


class LeakCheckReceipt(ClosedModel):
    """Builder source check over explicitly supplied visible bytes only."""

    version: Literal["m11-visible-leak-check/1"] = "m11-visible-leak-check/1"
    token_sha256: str
    visible_manifest_sha256: str
    verdict: Literal["absent", "leak"]
    matching_paths: tuple[str, ...]
    lineage: Literal["builder_source_check_not_independent_admission"] = "builder_source_check_not_independent_admission"


def check_decision_token_leak(token: bytes, visible_material: dict[str, bytes]) -> LeakCheckReceipt:
    """No traversal or hidden inputs: caller supplies admitted task/fixture bytes.

    This literal-byte check cannot prove semantic absence, custody, or admission.
    The token is never included in the receipt.
    """
    if not token:
        raise ContractError("decision token must be nonempty")
    for path in visible_material:
        _relative(path)
    matches = tuple(sorted(path for path, blob in visible_material.items() if token in blob))
    inventory = [{"path": path, "sha256": sha256_bytes(blob)} for path, blob in sorted(visible_material.items())]
    return LeakCheckReceipt(token_sha256=sha256_bytes(token), visible_manifest_sha256=sha256_bytes(canonical_json(inventory)),
                            verdict="leak" if matches else "absent", matching_paths=matches)


def check_memory_transition(manifest: TreatmentManifest, before: dict[str, bytes], after: dict[str, bytes], *, typed_after: TreatmentContent | None = None) -> MemoryTransition:
    """Archive hashes even on invalid writes; never repair, roll back or grade."""
    validate_treatment(manifest, before)
    def tree_hash(files: dict[str, bytes]) -> str:
        return sha256_bytes(canonical_json([{ "path": path, "sha256": sha256_bytes(blob)} for path, blob in sorted(files.items())]))
    before_hash, after_hash = tree_hash(before), tree_hash(after)
    changed = before != after
    disposition: Literal["unchanged", "permitted_update", "memory_write_invalid"] = "unchanged"
    reason = "memory bytes unchanged"
    if changed:
        disposition, reason = "memory_write_invalid", "memory is absent or immutable for assigned arm"
        if manifest.arm_id == "L2":
            writable = next(f.path for f in manifest.files if f.access == "read_write")
            readonly_unchanged = all(after.get(f.path) == before[f.path] for f in manifest.files if f.access == "read_only")
            if set(after) == set(before) and readonly_unchanged and typed_after is not None and typed_after.representation == "typed" and typed_after.rendered == after[writable]:
                disposition, reason = "permitted_update", "L2 typed update; archive exact bytes without correctness feedback"
            else:
                reason = "L2 update lacks valid typed content or changes allowed file inventory"
    return MemoryTransition(before_sha256=before_hash, after_sha256=after_hash, changed=changed, disposition=disposition, reason=reason)
