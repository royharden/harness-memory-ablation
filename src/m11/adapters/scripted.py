"""Explicit builder-authored synthetic patches returned as inert controller data."""
from __future__ import annotations

from pathlib import PurePosixPath

from pydantic import BaseModel, ConfigDict, model_validator

from harnessrun import AttemptSpec, ContractError, LaunchSpec

from .base import PreparationContext
from .null import NullAdapter


class ScriptedPatch(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    path: str
    expected_before_sha256: str
    replacement_utf8: str

    @model_validator(mode="after")
    def safe_patch(self) -> ScriptedPatch:
        path = PurePosixPath(self.path)
        if (not self.path or path.is_absolute() or ".." in path.parts
                or "\\" in self.path or ":" in self.path or "\x00" in self.path
                or str(path) != self.path):
            raise ValueError("scripted patch path must be a canonical relative POSIX path")
        if (len(self.expected_before_sha256) != 64 or
                any(c not in "0123456789abcdef" for c in self.expected_before_sha256)):
            raise ValueError("scripted patch requires exact before hash")
        return self


class ScriptedScenario(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    scenario_id: str
    mode: str = "SIMULATED"
    authorship: str = "builder-authored synthetic; not independent admission evidence"
    patches: tuple[ScriptedPatch, ...]
    trace_jsonl: bytes

    @model_validator(mode="after")
    def simulated_only(self) -> ScriptedScenario:
        if self.mode != "SIMULATED" or self.authorship != "builder-authored synthetic; not independent admission evidence":
            raise ValueError("scripted scenario must retain synthetic authorship and mode")
        if not self.scenario_id or len({p.path for p in self.patches}) != len(self.patches):
            raise ValueError("scenario ID required and patch paths unique")
        return self


class ScriptedAdapter(NullAdapter):
    harness_id = "scripted"

    def __init__(self, context: PreparationContext, settings_sha256: str,
                 scenario: ScriptedScenario):
        super().__init__(context, settings_sha256)
        self.scenario = scenario

    def prepare(self, spec: AttemptSpec) -> LaunchSpec:
        return self._launch(spec, ("m11-simulated-scripted", self.scenario.scenario_id))

    def planned_patches(self, spec: AttemptSpec) -> tuple[ScriptedPatch, ...]:
        self._validate(spec)
        records = self.parse(self.scenario.trace_jsonl)
        if any(record.attempt_id != spec.attempt_id for record in records):
            raise ContractError("scripted trace attempt binding mismatch")
        if any(getattr(record, "strength", None) == "verified" for record in records):
            raise ContractError("synthetic trace cannot verify native model identity")
        return self.scenario.patches
