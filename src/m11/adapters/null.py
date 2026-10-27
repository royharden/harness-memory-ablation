"""SIMULATED no-op control; never edits a candidate or grades it."""
from harnessrun import AttemptSpec, ContractError, LaunchSpec, parse_jsonl

from .base import AdapterBase


class NullAdapter(AdapterBase):
    harness_id = "null"
    simulated = True

    def prepare(self, spec: AttemptSpec) -> LaunchSpec:
        return self._launch(spec, ("m11-simulated-null",))

    def parse(self, data: bytes) -> tuple:
        records = parse_jsonl(data)
        if any(getattr(record, "record_type", None) not in
               {"HarnessEvent", "UsageObservation", "ModelEvidence"} for record in records):
            raise ContractError("adapter streams contain parsed observations only")
        if any(getattr(record, "record_type", None) == "ModelEvidence" and
               (record.strength != "unsupported" or record.provider_returned_model_id is not None)
               for record in records):
            raise ContractError("synthetic controls cannot supply native model proof")
        return records

    def planned_patches(self, spec: AttemptSpec) -> tuple:
        self._validate(spec)
        return ()
