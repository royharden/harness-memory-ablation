"""Reference coherence for a complete public record bundle, without grading/running."""

from .codec import ContractError, canonical_json, sha256_bytes
from .models import (
    AttemptRecord, AttemptSpec, GradeResult, HarnessEvent, LaunchSpec,
    Limitation, ModelEvidence, ProviderConfig, UsageObservation, WireRecord,
)


def validate_bundle(records: tuple[WireRecord, ...]) -> None:
    """Check references in a complete bundle; partial streams use parse_record instead."""
    specs = _index(records, AttemptSpec, "attempt_id")
    attempts = _index(records, AttemptRecord, "attempt_id")
    launches = _index(records, LaunchSpec, "launch_id")
    usages = _index(records, UsageObservation, "observation_id")
    models = _index(records, ModelEvidence, "model_evidence_id")
    events = _index(records, HarnessEvent, "event_id")
    _index(records, GradeResult, "attempt_id")
    modes = {r.mode for r in records if isinstance(r, (AttemptSpec, AttemptRecord))}
    if len(modes) > 1:
        raise ContractError("mixed SIMULATED/MEASURED bundle")
    configs = {sha256_bytes(canonical_json(r)): r for r in records if isinstance(r, ProviderConfig)}
    for spec in specs.values():
        if spec.provider_config_sha256 not in configs:
            raise ContractError("unresolved provider config")
        for parent in (spec.parent_attempt_id, spec.retry_of):
            if parent is not None and parent not in specs:
                raise ContractError("unresolved attempt lineage")
    _acyclic(specs)
    for launch in launches.values():
        spec = specs.get(launch.attempt_id)
        if spec is None or sha256_bytes(canonical_json(spec)) != launch.attempt_spec_sha256:
            raise ContractError("launch spec binding mismatch")
        if launch.output_cap_bytes != spec.output_cap_bytes or launch.environment_names != spec.environment_names:
            raise ContractError("launch caps/environment drift")
    for attempt in attempts.values():
        spec = specs.get(attempt.attempt_id)
        if spec is None or sha256_bytes(canonical_json(spec)) != attempt.attempt_spec_sha256:
            raise ContractError("attempt spec binding mismatch")
        if (attempt.cell_id, attempt.campaign_id, attempt.mode, attempt.parent_attempt_id, attempt.retry_of) != (
            spec.cell_id, spec.campaign_id, spec.mode, spec.parent_attempt_id, spec.retry_of
        ):
            raise ContractError("attempt identity/lineage mismatch")
        if attempt.launch_id is not None:
            launch = launches.get(attempt.launch_id)
            if launch is None or launch.attempt_id != attempt.attempt_id:
                raise ContractError("unresolved attempt launch")
            if sha256_bytes(canonical_json(launch)) != attempt.launch_spec_sha256:
                raise ContractError("launch hash mismatch")
        elif attempt.launch_spec_sha256 is not None:
            raise ContractError("launch hash without launch")
        for identities, registry in ((attempt.usage_observation_ids, usages), (attempt.model_evidence_ids, models)):
            for identity in identities:
                if identity not in registry or registry[identity].attempt_id != attempt.attempt_id:
                    raise ContractError("unresolved/cross-attempt observation")
        if attempt.usage_coverage == "complete" and (
            not attempt.usage_observation_ids or any(usages[i].coverage != "complete" for i in attempt.usage_observation_ids)
        ):
            raise ContractError("unsupported complete usage claim")
        if attempt.model_coverage == "complete" and not attempt.model_evidence_ids:
            raise ContractError("unsupported complete model coverage")
    sequences: dict[str, set[int]] = {}
    for record in records:
        if isinstance(record, (UsageObservation, ModelEvidence, HarnessEvent, GradeResult, Limitation)):
            if record.attempt_id not in specs:
                raise ContractError("record references absent attempt spec")
        if isinstance(record, HarnessEvent):
            seq = sequences.setdefault(record.attempt_id, set())
            if record.sequence in seq:
                raise ContractError("duplicate event sequence")
            seq.add(record.sequence)
            if record.kind == "started" and (record.payload.launch_id not in launches or
                launches[record.payload.launch_id].attempt_id != record.attempt_id):
                raise ContractError("started event has unresolved launch")
        if isinstance(record, ModelEvidence):
            config = configs[specs[record.attempt_id].provider_config_sha256]
            if config.requested_model_id != record.requested_model_id:
                raise ContractError("requested model drift")
        if isinstance(record, GradeResult):
            attempt = attempts.get(record.attempt_id)
            if attempt is None or attempt.artifact_sha256 != record.artifact_sha256:
                raise ContractError("grade does not bind retained immutable artifact")
    # Capture byte ranges, signatures, source custody and grader evidence require
    # external resolvers/gates; this structural check never claims those passed.


def _index(records, record_class, attribute):
    result = {}
    for record in records:
        if isinstance(record, record_class):
            identity = getattr(record, attribute)
            if identity in result:
                raise ContractError("duplicate record identity")
            result[identity] = record
    return result


def _acyclic(specs):
    active, done = set(), set()

    def visit(identity):
        if identity in active:
            raise ContractError("cyclic attempt lineage")
        if identity in done:
            return
        active.add(identity)
        for parent in (specs[identity].parent_attempt_id, specs[identity].retry_of):
            if parent is not None:
                visit(parent)
        active.remove(identity)
        done.add(identity)

    for identity in specs:
        visit(identity)
