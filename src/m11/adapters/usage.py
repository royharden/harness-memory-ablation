"""Conservative per-attempt/scope usage deltas; no prices or monetary authority."""
from __future__ import annotations

from dataclasses import dataclass, field

from harnessrun import ContractError, UsageObservation, canonical_json, sha256_bytes

BUCKETS = ("ordinary_input", "cached_input", "cache_write_5m", "cache_write_1h", "output")


@dataclass(frozen=True)
class UsageContribution:
    observation: UsageObservation
    buckets: tuple[tuple[str, int | None], ...]
    coverage: str
    reasons: tuple[str, ...]
    replay: bool


@dataclass
class _Scope:
    totals: dict[str, int | None] = field(default_factory=lambda: {k: 0 for k in BUCKETS})
    capture_sha256: str | None = None
    finalized: bool = False
    blocked: bool = False


class UsageNormalizer:
    """Keep every original observation, including zero-contribution exact replays.

    No cross-capture freshness can be established from UsageObservation alone.
    A changed capture for a used scope is therefore unknown, even if its counters
    look plausible. This conservative behavior cannot release M9 liabilities.
    """
    def __init__(self):
        self.observations: list[UsageObservation] = []
        self.contributions: list[UsageContribution] = []
        self._raw: dict[tuple[str, str, str], str] = {}
        self._ids: dict[tuple[str, str], tuple[str, str, str]] = {}
        self._scopes: dict[tuple[str, str], _Scope] = {}

    def add(self, observation: UsageObservation) -> UsageContribution:
        if not isinstance(observation, UsageObservation):
            raise ContractError("usage normalizer requires a validated UsageObservation")
        self.observations.append(observation)
        raw_key = (observation.attempt_id, observation.evidence_sha256, observation.source_locator)
        id_key = (observation.attempt_id, observation.observation_id)
        # observation_id may differ on re-encoding; it does not define new usage.
        semantic = observation.model_dump(mode="json", exclude={"observation_id"})
        fingerprint = sha256_bytes(canonical_json(semantic))
        previous = self._raw.get(raw_key)
        scope_key = (observation.attempt_id, observation.scope_id)
        state = self._scopes.setdefault(scope_key, _Scope())
        if previous is not None:
            if previous == fingerprint:
                return self._result(observation, {k: 0 for k in BUCKETS},
                                    observation.coverage, ("exact raw observation replay",), True)
            state.blocked = True
            return self._unknown(observation, "conflicting interpretations of identical raw provenance")
        if id_key in self._ids and self._ids[id_key] != raw_key:
            state.blocked = True
            return self._unknown(observation, "observation ID reused with different raw provenance")
        self._raw[raw_key] = fingerprint
        self._ids[id_key] = raw_key
        if state.capture_sha256 is not None and state.capture_sha256 != observation.evidence_sha256:
            state.blocked = True
            return self._unknown(observation, "cross-capture scope replay/freshness ambiguous without pinned provider identity")
        state.capture_sha256 = observation.evidence_sha256
        if state.blocked:
            return self._unknown(observation, "scope remains blocked after ambiguous counters")
        if state.finalized and observation.counter_basis == "incremental":
            state.blocked = True
            return self._unknown(observation, "incremental usage after final reconciliation")
        values = observation.buckets.model_dump()
        contribution: dict[str, int | None] = {}
        reasons = []
        if observation.unknown_reason is not None:
            reasons.append(observation.unknown_reason)
        for bucket in BUCKETS:
            value = values[bucket]
            previous_total = state.totals[bucket]
            if value is None or previous_total is None:
                contribution[bucket] = None
                state.totals[bucket] = None
                reasons.append(f"{bucket}: missing counter or earlier unknown contribution")
            elif observation.counter_basis == "incremental":
                contribution[bucket] = value
                state.totals[bucket] = previous_total + value
            elif value < previous_total:
                contribution[bucket] = None
                state.totals[bucket] = None
                reasons.append(f"{bucket}: counter reset, out of order or incompatible overlapping source")
            else:
                contribution[bucket] = value - previous_total
                state.totals[bucket] = value
        if observation.counter_basis == "final":
            state.finalized = True
        coverage = observation.coverage
        if any(value is None for value in contribution.values()):
            coverage = "unknown"
        return self._result(observation, contribution, coverage, tuple(dict.fromkeys(reasons)), False)

    def _result(self, observation, buckets, coverage, reasons, replay):
        result = UsageContribution(observation, tuple((k, buckets[k]) for k in BUCKETS),
                                   coverage, reasons, replay)
        self.contributions.append(result)
        return result

    def _unknown(self, observation: UsageObservation, reason: str) -> UsageContribution:
        return self._result(observation, {k: None for k in BUCKETS}, "unknown", (reason,), False)

    def totals(self, attempt_id: str) -> dict[str, int | None]:
        states = [state for (attempt, _), state in self._scopes.items() if attempt == attempt_id]
        if not states:
            return {k: None for k in BUCKETS}
        return {k: (None if any(s.blocked or s.totals[k] is None for s in states)
                    else sum(s.totals[k] for s in states)) for k in BUCKETS}
