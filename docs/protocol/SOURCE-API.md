# Source interface checkpoint — runtime unverified

Private delegated Dirty construction only. P0 and runtime/instrument acceptance
remain pending; no module has been imported or executed for this checkpoint.
The source models replace previously unavailable layouts for construction purposes,
not scientific admission or demonstrated runtime compatibility.

`m11.campaign` owns strict frozen `extra=forbid` Pydantic 2 models:
`Registration`, `SuiteManifest`, `SuiteTask`, `SuiteSeed`, `SeedCheckpoint`,
`PlannedCell`, `ScheduleManifest`, `TrajectoryCheckpoint`, `TripwireObservation`,
`AdmissionReference`, `CostObservation`, `PublicCheckpoint`, `ResultEligibility`,
`PublicExport`. Helper functions
`canonical_json` is an explicit UTF-8 text view of shared
`harnessrun.canonical_json` bytes for SQLite/text files. `sha256_json` is the
shared helper reexported directly, not reimplemented. Source reconciliation uses
corrected DL1 `f0b82a4`; `parse_export` uses shared `strict_json` duplicate-key,
nonfinite and byte-cap checks before model validation.
`parse_export(str | bytes | dict) -> PublicExport` rejects duplicate keys,
mixed modes, unresolved IDs, population/hash drift and false grading linkage.
It imports the ten-record closure types from `harnessrun` directly, without a
private evaluation dependency or silent replacement model.

`PublicExport` is separate `m11-export/1`: the SOURCE-SEAMS keys are retained,
with required nested public `registration` and `suite` manifests so hashes and
explicit mappings can be resolved. Every result array is required, including
empty arrays. Class tokens are `independent`, `decision`, `misleading`;
registration stages are A/B/C/D0/D1/E. Cells bind task hash/class/opaque grading
ID, arm/system/repeat, optional paired seed/checkpoint, optional actual attempt
and disposition. No attempt/grade is fabricated for an unstarted slot.

`CostObservation` separates `list_price_estimate` (per attempt, `estimated_usd`
nullable decimal string, dated price hash, usage IDs/coverage and evidence reference/hash)
from `tranche_receipt` (`actual_usd` nullable, billing scope only, no invented arm or
launch allocation). Neither supplies money authority. Both require explicit unknown
reasons for partial/missing costs; the other amount field must be null.

`PublicCheckpoint` binds task/cell/seed/attempt and before/after artifact hashes.
It carries four ordered `tripwire_ids`, four boolean-or-null `tripwire_outcomes`
and four corresponding `tripwire_missing_reasons`; null requires a reason.
`feature_completed` and reference hash have their own missing reasons; actual
observations require grading receipt and exact produced artifact. Internal
`TrajectoryCheckpoint` uses typed pass/fail/unknown observations for state transitions;
this is an explicit separate public model, not an alternate input shape.

Required `eligibility: ResultEligibility` hash-binds registration/suite and the
same scoped admission references. Current inference/public-release flags are
literal false. Release state is withheld/embargoed/simulated_descriptive; no
released state exists. Caller-asserted independent PASS is refused. MEASURED
hidden grades/checkpoint outcomes cannot be parsed as released results while
appointed verification is unavailable; SIMULATED stays descriptive. Receipt hashes
and ordinary booleans cannot authenticate independent rights or clear the embargo.

`m11.schedule.build_schedule(registration, suite) -> ScheduleManifest` constructs
full fixed stage populations. `validate_schedule` checks exact frozen design and
checksum; `remaining_cells` / `resume_schedule` consume durable `store.list_dispatches()`
state rows, never regenerate IDs or replace attempted cells. All ambiguous active
states block continuation. The scheduler is not a controller lease or authorization.

`m11.prereg.freeze_registration(path, registration, suite) -> Registration`,
`verify_registration(path, suite, current_pins=...) -> Registration` and
`amend_registration(path, parent, suite, amendment, consumed_cell_ids=...)`
use an exclusive immutable JSON envelope. Verification without current pins only
checks artifact integrity. Any consumed campaign is conservatively ineligible for
redesign; retain the earlier campaign and disclose a new diagnostic campaign.

`m11.authorize.check_authorization(registration, suite, schedule=..., evidence=...,
ledger=...)` returns an explicit refusal with reasons and digests. Current source
cannot authorize even a simulated instrument run, nor native work or any spend.
Future runtime eligibility is a separate approval/review boundary.
`m11.accounting.load_ledger()` returns an explicit unavailable port. No exact M9
closure is staged; all monetary operations refuse. See `VENDORED.md` for intake.

Store and trajectory APIs are described alongside their source docstrings. They
persist metadata or describe transitions only, never perform grading, secret
discovery, process launch, M9 money mutations or reference-tree repair. No database
is opened during import. Future runtime metadata belongs outside OneDrive.

All source/AST review, hash/reference/schema behavior and SQLite/longitudinal
semantics remain unexecuted. Public release, independent data, rights and runtime
activation need their own gates. Shared record attributes/imports have been
statically reconciled with corrected DL1 `f0b82a4`; no fallback aliases or
duplicated canonical helpers are used. This source comparison supplies no import,
runtime or packaging result.
