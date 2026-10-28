# Metadata journal bridge — runtime unverified

`m11.journal.MetadataLaunchJournal(store: MetadataStore,
receipt_authority: ExistingReceiptAuthority | None = None)` has the exact
`DurableLaunchJournal` method signatures in DL1's integrated `process.py`:
`claim`, `record_spawn_intent`, `record_started`, `record_cleanup_pending`,
`group_state` and `record_finished`. It depends on those protocol dataclasses;
process/controller imports no journal implementation, avoiding an import cycle.

`claim` always raises typed `JournalUnavailable(ControllerRefusal)`. The actual
cross-ledger atomic M9-begin/local-claim contract is not staged, and separate
SQLite plus M9 calls cannot truthfully satisfy it. No local ID, hash or permit
object can make this return a grant. `group_state` always returns `unknown`:
no live exclusive namespace/ownership lease through the controller's signal
operation exists. It performs no PID probe, process call or ownership assertion.

Useful recovery API `record_authenticated_claim(claim, attempt, launch, permit,
attestation, receipt=bytes)` archives an **existing externally consumed** claim.
It matches the exact frozen cell/suite, attempt/launch/permit/attestation and M9
run/begin receipt bindings. The injected `ExistingReceiptAuthority` must authenticate
original external signatures/issuer/revocation/receipt scope; no implementation or
permissive default is supplied. This is evidence authentication, not a second
runtime, monetary or independent-data authorization authority.

`ExistingReceiptAuthority.authenticate_claim(..., receipt)->None` must reject by
raising on any unauthenticated/conflicting claim. Its
`authenticated_existing_event(claim, kind, observation: bytes)->bytes` must return
the authenticated original receipt for that exact observation, never mint one from
controller-reported values. Receipt bytes are bounded/private; public exports do
not receive raw receipts, output or signature payloads.

Store claim/event transactions enforce unique claim/attempt/launch/cell bindings,
exact replay only, immutable event order and durable spawn intent before started.
SQLite lock waits are bounded and synchronous FULL is requested; this is source,
not proof of crash/fsync behavior. An ambiguous claim/spawn and even an archived
finished receipt keep cleanup/scheduling blocked. Local `finish_attempt` and
`resolve_cleanup` cannot unlock these journal claims without the missing external
lease/M9 reconciliation contract. No settlement or headroom release is performed.

Unavailable dependencies remain: exact pinned M9 closure and atomic claim backend,
authentic external receipt verifier, live namespace/descendant ownership lease and
signal handoff, approved cleanup/reconciliation and independent P0/runtime activation.
No DB/process/model/import/test execution, grants or independent evidence are supplied.
