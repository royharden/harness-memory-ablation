"""Declarative Linux workspace checks, without filesystem or container effects.

Source checks are not isolation evidence. Actual image/config/nonce and mount
verification remains unavailable until independent P0 and runtime activation.
"""

from __future__ import annotations

from pathlib import PurePosixPath
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from harnessrun import AttemptSpec, ContractError, LaunchSpec, Mount, canonical_json, sha256_bytes


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
