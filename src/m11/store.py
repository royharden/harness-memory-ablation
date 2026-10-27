"""Explicit SQLite metadata persistence; never a dispatch or monetary authority.

Construction checkpoint: runtime unverified. Instantiate with an absolute runtime
path outside OneDrive, then call initialize explicitly. No connection is opened at
import or construction. Immutable records reject conflicting replay; lifecycle is
separate so a crash after begin cannot be mistaken for an unstarted attempt.
"""

from __future__ import annotations

from contextlib import contextmanager
import hashlib
from pathlib import Path
import sqlite3
from typing import Iterator, Literal, TypeVar

from harnessrun import AttemptRecord
from pydantic import BaseModel, ConfigDict

from .campaign import PlannedCell, ScheduleManifest, TrajectoryCheckpoint, canonical_json
from .longitudinal import TrajectoryState

RecordT = TypeVar("RecordT", bound=BaseModel)


class StoreConflict(ValueError):
    """An immutable identity already has different content or lineage."""


class DispatchBlocked(StoreConflict):
    """Metadata cannot establish a new, unambiguous serial dispatch."""


class AttemptLifecycle(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    attempt_id: str
    cell_id: str
    state: Literal["claimed", "running", "cleanup_pending", "finished"]
    begin_sha256: str | None
    cleanup_receipt_sha256: str | None


def _hash(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _digest(value: str) -> None:
    if len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise ValueError("expected lowercase SHA256")


class MetadataStore:
    """Persist complete schedules/results, with explicit connections/transactions.

    get_* returns None for an absent record; list_* always returns a tuple and
    never synthesizes missing results. Each write uses BEGIN IMMEDIATE. The
    single unresolved lifecycle guard is global within this database, including
    campaigns, to preserve live concurrency one. A claim is not permission to run.
    """

    def __init__(self, path: str | Path) -> None:
        supplied_path = Path(path)
        if not supplied_path.is_absolute():
            raise ValueError("metadata path must be absolute")
        self.path = supplied_path.resolve(strict=False)
        if any(part.casefold().startswith("onedrive") for part in self.path.parts):
            raise ValueError("active metadata must reside outside OneDrive")

    @contextmanager
    def _connection(self, *, create: bool = False) -> Iterator[sqlite3.Connection]:
        # mode=rw prevents a read or ordinary write from creating an empty DB.
        uri = self.path.as_uri() + ("?mode=rwc" if create else "?mode=rw")
        connection = sqlite3.connect(uri, uri=True, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
        finally:
            connection.close()

    @contextmanager
    def _transaction(self, *, create: bool = False) -> Iterator[sqlite3.Connection]:
        with self._connection(create=create) as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                yield connection
                connection.commit()
            except BaseException:
                connection.rollback()
                raise

    def initialize(self) -> None:
        """Create schema explicitly; parent directory must already exist."""
        statements = (
            "CREATE TABLE IF NOT EXISTS metadata_schema (version INTEGER PRIMARY KEY CHECK(version=1))",
            "CREATE TABLE IF NOT EXISTS schedules (registration_id TEXT PRIMARY KEY, campaign_id TEXT NOT NULL, payload TEXT NOT NULL, sha256 TEXT NOT NULL)",
            "CREATE TABLE IF NOT EXISTS cells (cell_id TEXT PRIMARY KEY, registration_id TEXT NOT NULL REFERENCES schedules(registration_id), campaign_id TEXT NOT NULL, ordinal INTEGER NOT NULL, payload TEXT NOT NULL, sha256 TEXT NOT NULL, UNIQUE(registration_id, ordinal))",
            "CREATE TABLE IF NOT EXISTS attempts (attempt_id TEXT PRIMARY KEY, cell_id TEXT NOT NULL UNIQUE REFERENCES cells(cell_id), payload TEXT NOT NULL, sha256 TEXT NOT NULL)",
            "CREATE TABLE IF NOT EXISTS lifecycle (attempt_id TEXT PRIMARY KEY, cell_id TEXT NOT NULL UNIQUE REFERENCES cells(cell_id), state TEXT NOT NULL CHECK(state IN ('claimed','running','cleanup_pending','finished')), begin_sha256 TEXT, cleanup_receipt_sha256 TEXT)",
            "CREATE TABLE IF NOT EXISTS checkpoints (trajectory_id TEXT NOT NULL, checkpoint INTEGER NOT NULL CHECK(checkpoint BETWEEN 1 AND 12), cell_id TEXT NOT NULL REFERENCES cells(cell_id), payload TEXT NOT NULL, sha256 TEXT NOT NULL, PRIMARY KEY(trajectory_id, checkpoint))",
            "CREATE TABLE IF NOT EXISTS trajectory_states (trajectory_id TEXT NOT NULL, revision INTEGER NOT NULL, previous_sha256 TEXT, payload TEXT NOT NULL, sha256 TEXT NOT NULL, PRIMARY KEY(trajectory_id, revision), UNIQUE(trajectory_id, sha256))",
        )
        with self._transaction(create=True) as connection:
            for statement in statements:
                connection.execute(statement)
            versions = connection.execute("SELECT version FROM metadata_schema").fetchall()
            if versions and [row["version"] for row in versions] != [1]:
                raise StoreConflict("unsupported metadata schema")
            connection.execute("INSERT OR IGNORE INTO metadata_schema(version) VALUES (?)", (1,))

    @staticmethod
    def _same(row: sqlite3.Row | None, payload: str) -> bool:
        if row is None:
            return False
        if row["sha256"] != _hash(row["payload"]):
            raise StoreConflict("stored metadata hash mismatch")
        if row["payload"] != payload:
            raise StoreConflict("conflicting immutable record")
        return True

    def record_schedule(self, schedule: ScheduleManifest) -> None:
        """Atomically insert the manifest and every planned cell, idempotently."""
        payload = canonical_json(schedule)
        with self._transaction() as connection:
            row = connection.execute("SELECT payload, sha256 FROM schedules WHERE registration_id=?", (schedule.registration_id,)).fetchone()
            if self._same(row, payload):
                # Verify population as well; a partial/tampered DB is not repaired.
                stored = connection.execute("SELECT cell_id, payload, sha256 FROM cells WHERE registration_id=? ORDER BY ordinal", (schedule.registration_id,)).fetchall()
                if len(stored) != len(schedule.cells):
                    raise StoreConflict("stored schedule population differs")
                for old, cell in zip(stored, sorted(schedule.cells, key=lambda item: item.ordinal), strict=True):
                    if old["cell_id"] != cell.cell_id or not self._same(old, canonical_json(cell)):
                        raise StoreConflict("stored schedule cell differs")
                return
            connection.execute("INSERT INTO schedules VALUES (?,?,?,?)", (schedule.registration_id, schedule.campaign_id, payload, _hash(payload)))
            for cell in schedule.cells:
                if cell.registration_id != schedule.registration_id or cell.campaign_id != schedule.campaign_id:
                    raise StoreConflict("cell schedule lineage differs")
                cell_payload = canonical_json(cell)
                connection.execute("INSERT INTO cells VALUES (?,?,?,?,?,?)", (cell.cell_id, schedule.registration_id, cell.campaign_id, cell.ordinal, cell_payload, _hash(cell_payload)))

    def record_attempt(self, attempt: AttemptRecord) -> None:
        """Store a final immutable snapshot; retain refusal and failure records."""
        if attempt.status in ("pending", "running") or attempt.process_state == "running":
            raise StoreConflict("record_attempt requires a result snapshot, not live progress")
        payload = canonical_json(attempt)
        with self._transaction() as connection:
            row = connection.execute("SELECT payload, sha256 FROM attempts WHERE attempt_id=?", (attempt.attempt_id,)).fetchone()
            if self._same(row, payload):
                return
            cell = self._cell(connection, attempt.cell_id)
            if cell.campaign_id != attempt.campaign_id or (cell.attempt_id is not None and cell.attempt_id != attempt.attempt_id):
                raise StoreConflict("attempt does not match its frozen planned cell")
            lifecycle = connection.execute("SELECT attempt_id FROM lifecycle WHERE cell_id=?", (attempt.cell_id,)).fetchone()
            if lifecycle is not None and lifecycle["attempt_id"] != attempt.attempt_id:
                raise StoreConflict("attempt differs from durable claim")
            if lifecycle is None and attempt.process_state != "not_started":
                raise StoreConflict("a dispatched result requires durable dispatch lineage")
            connection.execute("INSERT INTO attempts VALUES (?,?,?,?)", (attempt.attempt_id, attempt.cell_id, payload, _hash(payload)))
            if lifecycle is None:
                if attempt.status != "refused":
                    raise StoreConflict("a zero-work result without dispatch lineage must be refused")
                # Keep zero-work attempted cells visible to resume, too. A
                # refusal is not a successful dispatch or a replacement grant.
                connection.execute("INSERT INTO lifecycle VALUES (?,?,'finished',NULL,NULL)", (attempt.attempt_id, attempt.cell_id))

    @staticmethod
    def _cell(connection: sqlite3.Connection, cell_id: str) -> PlannedCell:
        row = connection.execute("SELECT payload, sha256 FROM cells WHERE cell_id=?", (cell_id,)).fetchone()
        if row is None:
            raise StoreConflict("unknown planned cell")
        if _hash(row["payload"]) != row["sha256"]:
            raise StoreConflict("stored cell hash mismatch")
        return PlannedCell.model_validate_json(row["payload"])

    def claim_attempt(self, cell_id: str, attempt_id: str) -> AttemptLifecycle:
        """Claim once; replay is refused even with the same IDs. No auto retries."""
        if not attempt_id:
            raise ValueError("attempt_id must be nonempty")
        with self._transaction() as connection:
            cell = self._cell(connection, cell_id)
            if cell.attempt_id is not None and cell.attempt_id != attempt_id:
                raise DispatchBlocked("attempt ID differs from frozen schedule")
            if connection.execute("SELECT 1 FROM lifecycle WHERE state != 'finished' LIMIT 1").fetchone():
                raise DispatchBlocked("an unresolved claim, begin or cleanup blocks scheduling")
            if connection.execute("SELECT 1 FROM lifecycle WHERE cell_id=? OR attempt_id=?", (cell_id, attempt_id)).fetchone() or connection.execute("SELECT 1 FROM attempts WHERE cell_id=? OR attempt_id=?", (cell_id, attempt_id)).fetchone():
                raise DispatchBlocked("cell or attempt already exists; no replacement/re-dispatch")
            connection.execute("INSERT INTO lifecycle VALUES (?,?,'claimed',NULL,NULL)", (attempt_id, cell_id))
        return AttemptLifecycle(attempt_id=attempt_id, cell_id=cell_id, state="claimed", begin_sha256=None, cleanup_receipt_sha256=None)

    def begin_attempt(self, attempt_id: str, begin_sha256: str) -> None:
        """Durable pre-dispatch marker; repeating begin always refuses."""
        _digest(begin_sha256)
        with self._transaction() as connection:
            changed = connection.execute("UPDATE lifecycle SET state='running', begin_sha256=? WHERE attempt_id=? AND state='claimed' AND begin_sha256 IS NULL", (begin_sha256, attempt_id)).rowcount
            if changed != 1:
                raise DispatchBlocked("begin absent/already durable; ambiguous dispatch must not replay")

    def finish_attempt(self, attempt_id: str) -> None:
        """Finish only with a stored result; cleanup_pending keeps the serial lock."""
        with self._transaction() as connection:
            row = connection.execute("SELECT payload, sha256 FROM attempts WHERE attempt_id=?", (attempt_id,)).fetchone()
            if row is None or row["sha256"] != _hash(row["payload"]):
                raise StoreConflict("a hash-valid immutable attempt is required")
            result = AttemptRecord.model_validate_json(row["payload"])
            if result.process_state == "running":
                raise DispatchBlocked("owned processes still running")
            lifecycle = connection.execute("SELECT state FROM lifecycle WHERE attempt_id=?", (attempt_id,)).fetchone()
            if lifecycle is not None and lifecycle["state"] == "claimed" and (result.status != "refused" or result.process_state != "not_started"):
                raise DispatchBlocked("a claimed attempt cannot finish as dispatched without durable begin")
            state = "cleanup_pending" if result.process_state == "cleanup_pending" or result.status == "cleanup_pending" else "finished"
            changed = connection.execute("UPDATE lifecycle SET state=? WHERE attempt_id=? AND state IN ('claimed','running')", (state, attempt_id)).rowcount
            if changed != 1:
                raise StoreConflict("attempt is not an unresolved claim/begin")

    def resolve_cleanup(self, attempt_id: str, receipt_sha256: str) -> None:
        """Attach cleanup proof without rewriting the original attempt outcome."""
        _digest(receipt_sha256)
        with self._transaction() as connection:
            changed = connection.execute("UPDATE lifecycle SET state='finished', cleanup_receipt_sha256=? WHERE attempt_id=? AND state='cleanup_pending'", (receipt_sha256, attempt_id)).rowcount
            if changed != 1:
                raise StoreConflict("no pending cleanup for attempt")

    def record_checkpoint(self, checkpoint: TrajectoryCheckpoint) -> None:
        """Append an immutable terminal checkpoint snapshot, including unknowns."""
        if checkpoint.status in ("planned", "paused"):
            raise StoreConflict("only final checkpoint snapshots are immutable")
        payload = canonical_json(checkpoint)
        with self._transaction() as connection:
            cell = self._cell(connection, checkpoint.cell_id)
            if (cell.campaign_id, cell.seed_id, cell.checkpoint, cell.treatment_id, cell.harness_id) != (checkpoint.campaign_id, checkpoint.seed_id, checkpoint.checkpoint, checkpoint.treatment_id, checkpoint.harness_id):
                raise StoreConflict("checkpoint differs from frozen cell")
            row = connection.execute("SELECT payload, sha256 FROM checkpoints WHERE trajectory_id=? AND checkpoint=?", (checkpoint.trajectory_id, checkpoint.checkpoint)).fetchone()
            if self._same(row, payload):
                return
            if checkpoint.attempt_id is not None:
                attempt = connection.execute("SELECT cell_id FROM attempts WHERE attempt_id=?", (checkpoint.attempt_id,)).fetchone()
                if attempt is None or attempt["cell_id"] != checkpoint.cell_id:
                    raise StoreConflict("checkpoint attempt reference is unresolved")
            connection.execute("INSERT INTO checkpoints VALUES (?,?,?,?,?)", (checkpoint.trajectory_id, checkpoint.checkpoint, checkpoint.cell_id, payload, _hash(payload)))

    def record_trajectory_state(self, state: TrajectoryState, *, expected_previous_sha256: str | None) -> str:
        """Append full state (including pauses/archives) with compare-and-swap lineage.

        Returns its canonical SHA256 for the next append. Prior snapshots are never
        updated, so a paused observation survives later regrading/cleanup resolution.
        Caller uses longitudinal's pure transitions; this does not clear dispatch locks.
        """
        state = TrajectoryState.model_validate_json(canonical_json(state))
        if expected_previous_sha256 is not None:
            _digest(expected_previous_sha256)
        trajectory_id = state.checkpoints[0].trajectory_id
        payload = canonical_json(state)
        digest = _hash(payload)
        with self._transaction() as connection:
            for checkpoint in state.checkpoints:
                cell = self._cell(connection, checkpoint.cell_id)
                if (cell.campaign_id, cell.seed_id, cell.checkpoint, cell.treatment_id, cell.harness_id) != (checkpoint.campaign_id, checkpoint.seed_id, checkpoint.checkpoint, checkpoint.treatment_id, checkpoint.harness_id):
                    raise StoreConflict("trajectory state differs from its frozen cells")
            latest = connection.execute("SELECT revision,payload,sha256 FROM trajectory_states WHERE trajectory_id=? ORDER BY revision DESC LIMIT 1", (trajectory_id,)).fetchone()
            if latest is not None:
                if latest["sha256"] != _hash(latest["payload"]):
                    raise StoreConflict("stored trajectory state hash mismatch")
                if latest["sha256"] == digest:
                    if latest["payload"] != payload:
                        raise StoreConflict("trajectory hash/content conflict")
                    return digest
            actual_previous = latest["sha256"] if latest else None
            if actual_previous != expected_previous_sha256:
                raise StoreConflict("trajectory state changed since the expected revision")
            revision = latest["revision"] + 1 if latest else 0
            connection.execute("INSERT INTO trajectory_states VALUES (?,?,?,?,?)", (trajectory_id, revision, actual_previous, payload, digest))
        return digest

    def list_trajectory_states(self, trajectory_id: str) -> tuple[TrajectoryState, ...]:
        """Read the complete immutable state history; reject broken hash lineage."""
        with self._connection() as connection:
            rows = connection.execute("SELECT revision,previous_sha256,payload,sha256 FROM trajectory_states WHERE trajectory_id=? ORDER BY revision", (trajectory_id,)).fetchall()
        previous: str | None = None
        states = []
        for revision, row in enumerate(rows):
            if row["revision"] != revision or row["previous_sha256"] != previous or row["sha256"] != _hash(row["payload"]):
                raise StoreConflict("trajectory state history hash/lineage mismatch")
            states.append(TrajectoryState.model_validate_json(row["payload"]))
            previous = row["sha256"]
        return tuple(states)

    def get_trajectory_state(self, trajectory_id: str) -> TrajectoryState | None:
        states = self.list_trajectory_states(trajectory_id)
        return states[-1] if states else None

    def _read(self, query: str, parameters: tuple[object, ...], model: type[RecordT]) -> tuple[RecordT, ...]:
        with self._connection() as connection:
            rows = connection.execute(query, parameters).fetchall()
        records = []
        for row in rows:
            if row["sha256"] != _hash(row["payload"]):
                raise StoreConflict("stored metadata hash mismatch")
            records.append(model.model_validate_json(row["payload"]))
        return tuple(records)

    def get_schedule(self, registration_id: str) -> ScheduleManifest | None:
        records = self._read("SELECT payload,sha256 FROM schedules WHERE registration_id=?", (registration_id,), ScheduleManifest)
        return records[0] if records else None

    def get_cell(self, cell_id: str) -> PlannedCell | None:
        records = self._read("SELECT payload,sha256 FROM cells WHERE cell_id=?", (cell_id,), PlannedCell)
        return records[0] if records else None

    def list_cells(self, registration_id: str) -> tuple[PlannedCell, ...]:
        return self._read("SELECT payload,sha256 FROM cells WHERE registration_id=? ORDER BY ordinal", (registration_id,), PlannedCell)

    def get_attempt(self, attempt_id: str) -> AttemptRecord | None:
        records = self._read("SELECT payload,sha256 FROM attempts WHERE attempt_id=?", (attempt_id,), AttemptRecord)
        return records[0] if records else None

    def list_attempts(self, registration_id: str) -> tuple[AttemptRecord, ...]:
        return self._read("SELECT a.payload,a.sha256 FROM attempts a JOIN cells c ON a.cell_id=c.cell_id WHERE c.registration_id=? ORDER BY c.ordinal", (registration_id,), AttemptRecord)

    def list_checkpoints(self, trajectory_id: str) -> tuple[TrajectoryCheckpoint, ...]:
        return self._read("SELECT payload,sha256 FROM checkpoints WHERE trajectory_id=? ORDER BY checkpoint", (trajectory_id,), TrajectoryCheckpoint)

    def get_lifecycle(self, attempt_id: str) -> AttemptLifecycle | None:
        with self._connection() as connection:
            row = connection.execute("SELECT * FROM lifecycle WHERE attempt_id=?", (attempt_id,)).fetchone()
        return AttemptLifecycle.model_validate(dict(row)) if row else None

    def list_dispatches(self, registration_id: str | None = None) -> tuple[dict[str, str], ...]:
        """Resume view; includes every claim, including unresolved durable begins."""
        query = "SELECT l.cell_id,l.attempt_id,l.state,c.campaign_id FROM lifecycle l JOIN cells c ON l.cell_id=c.cell_id"
        parameters: tuple[object, ...] = ()
        if registration_id is not None:
            query += " WHERE c.registration_id=?"
            parameters = (registration_id,)
        query += " ORDER BY c.registration_id,c.ordinal"
        with self._connection() as connection:
            rows = connection.execute(query, parameters).fetchall()
        return tuple(dict(row) for row in rows)
