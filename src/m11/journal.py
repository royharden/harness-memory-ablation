"""Private recovery metadata adapter; no supplied M9 or ownership authority.

Source construction only, runtime unverified. Neither an archived receipt nor a
SQLite transaction can supply the missing cross-ledger atomic claim or live
namespace lease. Dispatch always refuses; group ownership always stays unknown.
No database connection, process or authority call occurs at construction/import.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Literal, Protocol

from harnessrun import AttemptSpec, LaunchSpec, canonical_json, sha256_bytes
from harnessrun.codec import strict_json

from .process import ControllerOutcome, ControllerRefusal, LaunchClaim, StopReason
from .store import MetadataStore, StoreConflict
from .workspace import RuntimeAttestation, RuntimePermit

EventKind = Literal["spawn_intent", "started", "cleanup_pending", "finished"]


class JournalUnavailable(ControllerRefusal):
    """An exact authentic integration is absent; retain consumed IDs/liability."""


class ExistingReceiptAuthority(Protocol):
    """Operator-injected authenticator of EXISTING external evidence only.

    No implementation is supplied. Callbacks must authenticate issuer/signature,
    revocation and the exact claim/request/observation binding with bounded IO.
    They must reject unknown, stale, conflicting or unauthenticated receipts.
    They grant no new runtime, monetary, lease or independent-data authority.
    A digest/boolean supplied by a caller is never sufficient evidence.
    """

    def authenticate_claim(self, claim: LaunchClaim, attempt: AttemptSpec,
                           launch: LaunchSpec, permit: RuntimePermit,
                           attestation: RuntimeAttestation, receipt: bytes) -> None:
        """Authenticate actual consumed claim/M9 begin and exact receipt pins."""
        ...

    def authenticated_existing_event(self, claim: LaunchClaim, kind: EventKind,
                                     observation: bytes) -> bytes:
        """Return authenticated original external receipt for exact observation.

        started must bind actual PID/PGID acknowledgement; finished must bind
        the exact outcome and any claimed all-descendant cleanup evidence.
        Never mint evidence merely because a controller reported a value.
        """
        ...


def _receipt(value: bytes) -> str:
    if not isinstance(value, bytes) or not value or len(value) > 1024 * 1024:
        raise JournalUnavailable("bounded original authenticated receipt bytes required")
    # Private archival bytes, not public export and not proof by themselves.
    return value.hex()


class MetadataLaunchJournal:
    """Concrete DurableLaunchJournal surface with explicit unavailable seams.

    store is metadata only. receipt_authority must be a trusted injected
    integration; no default authenticates anything. Recovery writes consume
    unique identities and keep scheduling blocked, including after terminal
    archival. An external lease/M9 reconciliation contract remains necessary
    before this adapter could safely permit dispatch or release that lock.
    """

    def __init__(self, store: MetadataStore, *,
                 receipt_authority: ExistingReceiptAuthority | None = None) -> None:
        self._store = store
        self._authority = receipt_authority

    def claim(self, attempt: AttemptSpec, launch: LaunchSpec,
              permit: RuntimePermit, attestation: RuntimeAttestation) -> LaunchClaim:
        # In particular do not compose store.claim_attempt + an M9 callback:
        # separate commits cannot meet DurableLaunchJournal's atomic contract.
        raise JournalUnavailable(
            "exact atomic M9 begin/local single-use claim contract unavailable; no new claim issued"
        )

    def record_authenticated_claim(self, claim: LaunchClaim, attempt: AttemptSpec,
                                   launch: LaunchSpec, permit: RuntimePermit,
                                   attestation: RuntimeAttestation, *, receipt: bytes) -> None:
        """Archive an actual externally consumed claim; never return a grant.

        This recovery method is deliberately separate from claim(). Replaying
        it with exactly the same bytes is an archival no-op, never a retry.
        """
        authority = self._require_authority()
        receipt_hex = _receipt(receipt)
        cell = self._store.get_cell(attempt.cell_id)
        if cell is None or (
            attempt.campaign_id, attempt.task_id, attempt.task_sha256,
            attempt.treatment_id, attempt.harness_id, attempt.repeat, attempt.checkpoint,
        ) != (
            cell.campaign_id, cell.task_id, cell.task_sha256,
            cell.treatment_id, cell.harness_id, cell.repeat, cell.checkpoint,
        ):
            raise JournalUnavailable("external consumed claim differs from frozen cell mapping")
        schedule = self._store.get_schedule(cell.registration_id)
        if schedule is None or schedule.suite_sha256 != attempt.suite_sha256:
            raise JournalUnavailable("external consumed claim differs from frozen suite binding")
        expected = (attempt.attempt_id, launch.launch_id,
                    sha256_bytes(canonical_json(attempt)),
                    sha256_bytes(canonical_json(launch)),
                    sha256_bytes(canonical_json(permit)), permit.ledger_run_id)
        actual = (claim.attempt_id, claim.launch_id, claim.attempt_spec_sha256,
                  claim.launch_spec_sha256, claim.permit_sha256, claim.ledger_run_id)
        if not claim.claim_id or actual != expected or launch.attempt_id != attempt.attempt_id or launch.attempt_spec_sha256 != claim.attempt_spec_sha256:
            raise JournalUnavailable("external claim does not bind immutable attempt/launch/permit")
        if (permit.attempt_id, permit.launch_id, permit.attempt_spec_sha256,
            permit.launch_spec_sha256, attestation.permit_sha256,
            attestation.isolation_context_id) != (
            attempt.attempt_id, launch.launch_id, claim.attempt_spec_sha256,
            claim.launch_spec_sha256, claim.permit_sha256, permit.isolation_context_id
        ):
            raise JournalUnavailable("external permit/attestation scope mismatch")
        authority.authenticate_claim(claim, attempt, launch, permit, attestation, receipt)
        payload = canonical_json({
            "schema_version": "m11-private-launch-claim/1", "claim": asdict(claim),
            "cell_id": attempt.cell_id,
            "attestation_sha256": sha256_bytes(canonical_json(attestation)),
            "isolation_context_id": permit.isolation_context_id,
            "ledger_begin_receipt_sha256": permit.ledger_begin_receipt_sha256,
            "receipt_hex": receipt_hex,
        }).decode("utf-8")
        self._store.record_launch_claim(claim_id=claim.claim_id,
            attempt_id=claim.attempt_id, launch_id=claim.launch_id,
            cell_id=attempt.cell_id, payload=payload)

    def _require_authority(self) -> ExistingReceiptAuthority:
        if self._authority is None:
            raise JournalUnavailable("trusted existing external receipt authenticator unavailable")
        return self._authority

    def _binding(self, claim: LaunchClaim) -> str:
        payload = self._store.get_launch_claim(claim.claim_id)
        if payload is None:
            raise JournalUnavailable("authenticated consumed claim archive unavailable")
        stored = strict_json(payload.encode("utf-8"))
        if not isinstance(stored, dict) or stored.get("schema_version") != "m11-private-launch-claim/1" or stored.get("claim") != asdict(claim):
            raise StoreConflict("launch event immutable claim binding differs")
        return payload

    def _record(self, claim: LaunchClaim, kind: EventKind,
                observation: dict[str, object]) -> None:
        authority = self._require_authority()
        binding = self._binding(claim)
        exact_observation = canonical_json({"claim": asdict(claim), "kind": kind,
                                           "observation": observation})
        receipt = authority.authenticated_existing_event(claim, kind, exact_observation)
        payload = canonical_json({"schema_version": "m11-private-launch-event/1",
            "observation_hex": exact_observation.hex(),
            "receipt_hex": _receipt(receipt), "liability": "retained"}).decode("utf-8")
        self._store.record_launch_event(claim.claim_id, binding, kind, payload)

    def record_spawn_intent(self, claim: LaunchClaim) -> None:
        """Durably archive existing intent as ambiguous before any future spawn."""
        self._record(claim, "spawn_intent", {"begin_state": "ambiguous"})

    def record_started(self, claim: LaunchClaim, pid: int, pgid: int) -> None:
        if type(pid) is not int or type(pgid) is not int or pid <= 0 or pgid != pid:
            raise JournalUnavailable("fresh-session positive PID/PGID acknowledgement required")
        self._record(claim, "started", {"pid": pid, "pgid": pgid})

    def record_cleanup_pending(self, claim: LaunchClaim, reason: StopReason) -> None:
        if reason not in ("finished", "timeout", "output_cap", "crash", "cancelled"):
            raise JournalUnavailable("unsupported cleanup reason")
        self._record(claim, "cleanup_pending", {"reason": reason})

    def group_state(self, claim: LaunchClaim, pid: int,
                    pgid: int) -> Literal["owned", "empty", "unknown"]:
        # Neither a DB record nor a PID probe can keep an exclusive namespace
        # lease valid through the controller's subsequent signal operation.
        return "unknown"

    def record_finished(self, claim: LaunchClaim, outcome: ControllerOutcome) -> None:
        lifecycle = outcome.lifecycle
        if (lifecycle.attempt_id, lifecycle.launch_id) != (claim.attempt_id, claim.launch_id):
            raise JournalUnavailable("terminal observation differs from consumed launch")
        if lifecycle.process_state not in ("exited", "cleanup_pending") or outcome.liability != "retained":
            raise JournalUnavailable("terminal observation must retain unresolved monetary liability")
        self._record(claim, "finished", {
            "lifecycle": lifecycle.model_dump(mode="json"),
            "output_sha256": sha256_bytes(outcome.output),
            "output_bytes": len(outcome.output),
            "output_truncated": outcome.output_truncated,
            "stdin_bytes_written": outcome.stdin_bytes_written,
            "exit_code": outcome.exit_code, "wall_seconds": outcome.wall_seconds,
            "liability": outcome.liability,
            "journal_confirmed": outcome.journal_confirmed,
            # Local source has no admitted cleanup reconciliation/lease seam.
            "metadata_cleanup_state": "cleanup_pending",
        })
