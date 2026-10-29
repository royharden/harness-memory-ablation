"""Declarative Linux workspace checks, without filesystem or container effects.

Source checks are not isolation evidence. Actual image/config/nonce and mount
verification remains unavailable until independent P0 and runtime activation.
"""

from __future__ import annotations

from pathlib import PurePosixPath
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from harnessrun import AttemptSpec, CapabilityRecord, ContractError, LaunchSpec, Mount, canonical_json, sha256_bytes
from harnessrun.models import Identifier, SHA256
from .configuration import require_no_placeholders


def _absolute(path: str) -> str:
    if not path.startswith("/") or path.startswith("//") or "\\" in path or ":" in path or "\x00" in path:
        raise ValueError("only canonical container-absolute POSIX paths permitted")
    if any(part in ("", ".", "..") for part in path.split("/")[1:]):
        raise ValueError("ambiguous container path")
    return path


def _under(path: str, root: str) -> bool:
    return PurePosixPath(path).is_relative_to(PurePosixPath(root))


class WorkspacePolicy(BaseModel):
    """Frozen declaration, never a substitute for observed isolation evidence."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    schema_version: Literal["m11-workspace/1"] = "m11-workspace/1"
    workspace_ref: str
    image_sha256: str
    binary_sha256: str
    workspace_root: str
    fresh_home: str
    config_roots: tuple[str, ...]
    session_roots: tuple[str, ...]
    allowed_mounts: tuple[Mount, ...]
    environment_names: tuple[str, ...]
    allowed_argv: tuple[str, ...]
    forbidden_roots: tuple[str, ...]
    disabled_features: tuple[Literal["auto_updates", "global_skills", "plugins", "mcp", "external_retrieval", "auto_memory", "background_agents", "subagents", "prior_sessions"], ...]
    network_policy: Literal["offline", "provider_only"]
    clean_home_manifest_sha256: str
    clean_config_manifest_sha256: str

    @field_validator("image_sha256", "binary_sha256", "clean_home_manifest_sha256", "clean_config_manifest_sha256")
    @classmethod
    def digest(cls, value: str) -> str:
        if len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
            raise ValueError("expected lowercase SHA256")
        return value

    _paths = field_validator("workspace_root", "fresh_home")(_absolute)

    @model_validator(mode="after")
    def closed_roots(self) -> WorkspacePolicy:
        roots = (self.workspace_root, self.fresh_home, *self.config_roots, *self.session_roots)
        for root in (*roots, *self.forbidden_roots):
            _absolute(root)
        if not self.workspace_ref or not self.allowed_argv:
            raise ValueError("workspace reference and exact argv required")
        if any(not arg or "\x00" in arg or "\n" in arg or "\r" in arg for arg in self.allowed_argv):
            raise ValueError("argv entries must be nonempty, NUL/newline-free arguments")
        if PurePosixPath(self.allowed_argv[0]).name in ("sh", "bash", "dash", "zsh", "cmd", "cmd.exe", "powershell", "pwsh"):
            raise ValueError("shell launch/interpolation is forbidden")
        if any(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name) is None for name in self.environment_names):
            raise ValueError("environment allowlist contains a value or invalid name")
        if _under(self.fresh_home, self.workspace_root) or _under(self.workspace_root, self.fresh_home):
            raise ValueError("home and workspace must be disjoint")
        if not self.config_roots or not self.session_roots:
            raise ValueError("explicit fresh config/session roots required")
        if any(not _under(root, self.fresh_home) for root in (*self.config_roots, *self.session_roots)):
            raise ValueError("config/session search roots must lie in fresh home")
        required = {"auto_updates", "global_skills", "plugins", "mcp", "external_retrieval", "auto_memory", "background_agents", "subagents", "prior_sessions"}
        if set(self.disabled_features) != required or len(self.disabled_features) != len(required):
            raise ValueError("all global/background context features must be explicitly disabled")
        for values in (self.environment_names, self.config_roots, self.session_roots, self.forbidden_roots):
            if len(set(values)) != len(values):
                raise ValueError("duplicate workspace allowlist entries")
        if len(self.allowed_mounts) != 1:
            raise ValueError("agent receives only its task-workspace mount")
        mount = self.allowed_mounts[0]
        if mount.source_ref != self.workspace_ref or mount.target_path != self.workspace_root or mount.access != "read_write":
            raise ValueError("only the opaque admitted workspace reference may be mounted")
        # Source references are opaque; never interpret one as a host path.
        if any(c in self.workspace_ref for c in ("/", "\\", ":", "\x00")):
            raise ValueError("workspace source reference must not encode a host path")
        for forbidden in self.forbidden_roots:
            if any(_under(root, forbidden) or _under(forbidden, root) for root in roots):
                raise ValueError("allowed root overlaps forbidden home/sibling/hidden/socket root")
        return self


class WorkspaceCheck(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    schema_version: Literal["m11-workspace-check/1"] = "m11-workspace-check/1"
    disposition: Literal["source_consistent_runtime_unverified"] = "source_consistent_runtime_unverified"
    policy_sha256: str
    limitations: tuple[str, ...] = ("P0 pending", "image/home/config/mount isolation not executed", "forbidden-context nonce not executed")


def validate_workspace(attempt: AttemptSpec, launch: LaunchSpec, policy: WorkspacePolicy) -> WorkspaceCheck:
    """Refuse drift against an exact declaration; do not inspect host paths."""
    if launch.attempt_id != attempt.attempt_id:
        raise ContractError("launch/attempt identity mismatch")
    if launch.attempt_spec_sha256 != sha256_bytes(canonical_json(attempt.model_dump(mode="json"))):
        raise ContractError("launch attempt digest mismatch")
    if attempt.workspace_ref != policy.workspace_ref:
        raise ContractError("workspace source reference mismatch")
    if launch.image_sha256 is None or launch.image_sha256 != policy.image_sha256 or launch.binary_sha256 != policy.binary_sha256:
        raise ContractError("pinned image/binary required; host fallback forbidden")
    _absolute(launch.cwd)
    if not _under(launch.cwd, policy.workspace_root):
        raise ContractError("cwd escapes admitted workspace")
    if launch.allowed_mounts != policy.allowed_mounts:
        raise ContractError("mount allowlist mismatch")
    if launch.environment_names != policy.environment_names or attempt.environment_names != policy.environment_names:
        raise ContractError("environment-name allowlist mismatch")
    if launch.argv != policy.allowed_argv:
        raise ContractError("argv differs from frozen exact allowlist")
    if launch.output_cap_bytes != attempt.output_cap_bytes:
        raise ContractError("launch output cap differs from attempt")
    for entry in attempt.treatment_files:
        path = entry.path
        if path.startswith("/"):
            _absolute(path)
            if not _under(path, policy.workspace_root):
                raise ContractError("treatment path escapes workspace")
        elif not path or "\\" in path or ":" in path or any(p in ("", ".", "..") for p in path.split("/")):
            raise ContractError("noncanonical relative treatment path")
    return WorkspaceCheck(policy_sha256=sha256_bytes(canonical_json(policy.model_dump(mode="json"))))


class RuntimeVerificationUnavailable(ContractError):
    """No trusted runtime/admission/isolation integration can verify this request."""


class TaskDelivery(BaseModel):
    """Private controller input, separate from the closed public LaunchSpec.

    task_sha256 binds the suite execution item; payload_sha256 binds exact visible
    instruction bytes. A future trusted verifier must establish their relationship.
    No input content is placed in argv, wire events, or verification error messages.
    """

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    task_id: Identifier
    task_sha256: SHA256
    transport: Literal["utf8_stdin"] = "utf8_stdin"
    payload: bytes
    payload_sha256: SHA256

    @model_validator(mode="after")
    def input_binding(self) -> TaskDelivery:
        if not self.payload or len(self.payload) > 1024 * 1024 or b"\x00" in self.payload:
            raise ValueError("visible task input must be nonempty bounded NUL-free UTF8")
        self.payload.decode("utf-8", errors="strict")
        if sha256_bytes(self.payload) != self.payload_sha256:
            raise ValueError("task input hash mismatch")
        return self


class RuntimePermit(BaseModel):
    """Untrusted permit artifact until a future trusted verifier authenticates it.

    Hashes and this type do not grant execution. Current source has no issuer,
    signer, receipt verifier or operator activation that can authorize runtime.
    """

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    schema_version: Literal["m11-runtime-permit/1"] = "m11-runtime-permit/1"
    permit_id: Identifier
    attempt_id: Identifier
    launch_id: Identifier
    attempt_spec_sha256: SHA256
    launch_spec_sha256: SHA256
    policy_sha256: SHA256
    delivery_sha256: SHA256
    capabilities_sha256: SHA256
    isolation_context_id: Identifier
    ledger_run_id: Identifier
    expires_at: str
    admission_receipt_sha256: SHA256
    activation_receipt_sha256: SHA256
    capability_receipt_sha256: SHA256
    isolation_receipt_sha256: SHA256
    finite_liability_receipt_sha256: SHA256
    ledger_begin_receipt_sha256: SHA256
    task_delivery_receipt_sha256: SHA256


class RuntimeAttestation(BaseModel):
    """Return contract of trusted verification, not a caller-owned admission flag."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    permit_sha256: SHA256
    isolation_context_id: Identifier
    verified_platform: Literal["linux"]
    checked_at: str
    verification_receipt_sha256: SHA256


class RuntimeVerifier(Protocol):
    """Future operator-owned authority, never loaded from a public request object.

    Must authenticate signatures, revocation, P0/activation/source access, exact
    capability/task-input/model/usage/finite-liability evidence, actual M9 begin,
    pinned image/binary and *current* Linux isolation namespaces/mounts/home/config/
    network in the executing context. Source declaration checks prove none of it.
    """

    def verify(self, permit: RuntimePermit, attempt: AttemptSpec, launch: LaunchSpec,
               policy: WorkspacePolicy, delivery: TaskDelivery) -> RuntimeAttestation: ...


class UnavailableRuntimeVerifier:
    def verify(self, permit: RuntimePermit, attempt: AttemptSpec, launch: LaunchSpec,
               policy: WorkspacePolicy, delivery: TaskDelivery) -> RuntimeAttestation:
        raise RuntimeVerificationUnavailable(
            "P0/runtime activation, authentic permit/isolation/capability/task-delivery verification and M9 begin integration unavailable"
        )


def _runtime_utc(value: str) -> datetime:
    if not value.endswith(("Z", "+00:00")) or "T" not in value:
        raise RuntimeVerificationUnavailable("runtime timestamp must be RFC3339 UTC")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RuntimeVerificationUnavailable("malformed runtime timestamp") from exc


def confirm_execution_permission(attempt: AttemptSpec, launch: LaunchSpec, policy: WorkspacePolicy,
                                 delivery: TaskDelivery, permit: RuntimePermit,
                                 verifier: RuntimeVerifier) -> RuntimeAttestation:
    """Bind an exact request then ask the trusted authority; hashes alone never pass."""
    require_no_placeholders((attempt, launch, policy, permit))
    validate_workspace(attempt, launch, policy)
    if (delivery.task_id, delivery.task_sha256) != (attempt.task_id, attempt.task_sha256):
        raise RuntimeVerificationUnavailable("task delivery does not bind scheduled execution item")
    expected = (attempt.attempt_id, launch.launch_id, sha256_bytes(canonical_json(attempt)),
                sha256_bytes(canonical_json(launch)), sha256_bytes(canonical_json(policy)),
                sha256_bytes(canonical_json(delivery)))
    actual = (permit.attempt_id, permit.launch_id, permit.attempt_spec_sha256,
              permit.launch_spec_sha256, permit.policy_sha256, permit.delivery_sha256)
    if expected != actual:
        raise RuntimeVerificationUnavailable("permit scope differs from immutable execution request")
    now = datetime.now(timezone.utc)
    if _runtime_utc(permit.expires_at) <= now:
        raise RuntimeVerificationUnavailable("runtime permit expired")
    attestation = verifier.verify(permit, attempt, launch, policy, delivery)
    if not isinstance(attestation, RuntimeAttestation):
        raise RuntimeVerificationUnavailable("trusted verifier did not supply its attestation contract")
    if (attestation.permit_sha256, attestation.isolation_context_id) != (
        sha256_bytes(canonical_json(permit)), permit.isolation_context_id
    ):
        raise RuntimeVerificationUnavailable("runtime verification does not bind this permit/context")
    finished = datetime.now(timezone.utc)
    age = (finished - _runtime_utc(attestation.checked_at)).total_seconds()
    if age < -1 or age > 30 or _runtime_utc(permit.expires_at) <= finished:
        raise RuntimeVerificationUnavailable("runtime verification is stale or permit expired during verification")
    return attestation


@dataclass(frozen=True)
class PreparationAuthorization:
    """Trusted controller integration only; not a public JSON switch or issuer."""

    policy: WorkspacePolicy
    delivery: TaskDelivery
    permit: RuntimePermit
    capabilities: CapabilityRecord
    verifier: RuntimeVerifier


def confirm_native_preparation(attempt: AttemptSpec, launch: LaunchSpec,
                               authorization: PreparationAuthorization,
                               cli_version: str) -> None:
    require_no_placeholders((authorization.capabilities, authorization.permit, authorization.policy))
    capability = authorization.capabilities
    if (capability.harness_id, capability.cli_version, capability.binary_sha256,
        capability.image_sha256, capability.provider_config_sha256, capability.settings_sha256) != (
        attempt.harness_id, cli_version, launch.binary_sha256, launch.image_sha256,
        attempt.provider_config_sha256, attempt.model_settings_sha256
    ):
        raise RuntimeVerificationUnavailable("capability pins do not match native launch")
    if any(item.status != "verified" for item in (
        capability.model_evidence, capability.native_memory, capability.usage_buckets, capability.spend_bound
    )):
        raise RuntimeVerificationUnavailable("native capabilities lack verified evidence")
    if sha256_bytes(canonical_json(capability)) != authorization.permit.capabilities_sha256:
        raise RuntimeVerificationUnavailable("permit capability record mismatch")
    confirm_execution_permission(attempt, launch, authorization.policy, authorization.delivery,
                                 authorization.permit, authorization.verifier)
