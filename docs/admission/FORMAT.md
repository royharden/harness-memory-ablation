# Admission and task-pack format specification

Status: format only. P0, full-pack admission, independent appointments and all executed
checks are PENDING — needs Roy. This document contains no task, answer, grader or receipt.
It specifies future records; its presence is never admission evidence.

Source-phase amendment: Roy adopted the delegated 2026-10-27 source ruling
(SHA256 38fbf484ee1347145f9ab80a971a305f7d4d2d7e3c492cc735183c284a84dbdb).
It supersedes P0-before-source restrictions below for private Dirty construction only.
P0 is not waived: no runtime, independent admission or acceptance/validated claim.

Controlling source: private OUTER planning/promoted/PLAN-M11-v1.md, SHA256
0126184f9d0ddd2de1f0fe4c9e7fb5c170d5676004c0a023bf8fe63d53c8e99c.
Section numbers below refer to that immutable plan. The portable format below is a
scoped interpretation for P1/P6/P10, not an amendment or second plan. A future schema
must preserve these semantics and reconcile field names with DL1's central contracts.

## Authority and custody (§§4–5)

| Actor | May produce/consume | Boundary |
|---|---|---|
| Builder | Dev tasks/seeds after construction grant; public manifests and receipts | No held-out content, P0 answers, independent worksheet, or independent verdict |
| Independent nonbuilder custodian | P0 sample, held-out pack, independent expected behavior and correct/wrong patches | Must be actually appointed; identity/lineage recorded |
| Named human semantic/rights reviewer | Reviews every P0 item and rights/semantic records across all items | Detailed audit at least six held-out tasks and all four held-out seeds' tripwires; disclose sampling |
| Separate custodian-side session | Adversarial check of every trusted grader | Different model lineage preferred; cannot replace human review |
| Operator | Reruns independent kit; receives sealed visible workspaces directly from custodian | Hidden grader volume inaccessible to agents/builders |
| Scheduler/grader consumer | Visible task material / opaque task ID and immutable candidate | Adapter does not own grading; hidden feedback never enters later longitudinal sessions |

No builder or builder child becomes an independent custodian/verifier by being renamed.
The P0 kit is self-contained stdlib/pytest/container material and imports no m11 code.
No appointments are made by this specification.

## Two distinct admission records (§§4–5,10 P1)

A future receipt must identify its gate as P0 or full_pack. Gate identity cannot be
inferred from an overall pass flag.

P0 precedes any product scaffold/implementation under the frozen plan. Format-only
documents may precede it. Required sample: three original tasks, one per class; one
seed, four tripwires, two reference checkpoints; correct patches, three plausible
wrong patches per task, and independently authored expected behavior tables.
Operator reruns in the approved Python 3.12 container. Every oracle passes, untouched
tasks fail, every wrong patch fails, null score is zero; three keyless reruns are stable.
Seed baseline and both references pass all active features and tripwires. Provenance,
rights, signatures, disjointness, mounts/config/grader separation and forbidden-context
canaries must pass. Any failure, missing appointment/signature or unavailable required
evidence is NO-GO: report M11 SKIPPED and do not implement. No dev-only downgrade.

Full-pack admission is a separate check of 100% of tasks, diagnostics, seeds and
references before held-out freeze/opening. It repeats hashes/counts, independent
authorship, rights/reviewer records, family disjointness, leakage, oracle/untouched/
wrong/null checks, three-run stability, isolation, baseline/accrued-feature/tripwire/
claim expectations. P0 never substitutes for it. Frozen-pack failure means SKIPPED in
execution; there is no dev-only research substitute. Passing either gate does not
authorize accounts, live calls, spending or publication.

### Receipt envelope

All mandatory evidence must resolve. Before a gate is attempted its status is PENDING;
an attempted admission with missing/unverifiable required evidence is NO-GO. These are semantic fields, not an approved
wire schema or signature mechanism.

| Field group | Required meaning |
|---|---|
| Gate/binding | gate kind, gate ID, pack ID/version/digest, controlling plan digest, evaluated item scope and expected/observed inventory |
| Independent manifest | author_session, lineage, reviewer_person, reviewed_at, source_hashes, rights_verdict, semantic_verdict, independent_expected_answers, gate_receipt_hash, signed no-forbidden-source attestation (§4 names retained) |
| Appointments/review | Custodian appointment reference, human identity and review coverage, separate adversarial-session identity/lineage and coverage |
| Execution | Operator identity, exact kit/source/config/image/Python pins, rerun IDs, evidence artifacts and per-item outcomes for each required check |
| Integrity/custody | Exact-byte SHA256 references; seal, visible/hidden separation, access/exposure events, family/split and isolation evidence |
| Decision | PENDING / NO-GO / PASS for this gate only, unresolved reasons and responsible actor, decision time and evidence references |

independent_expected_answers is a reference to custodian-owned evidence, not answer
text in a builder-readable receipt. gate_receipt_hash must identify a finalized receipt
artifact unambiguously; a future serializer must define its hash scope without a
self-referential digest. Signatures/attestations must bind the reviewed manifest and
gate evidence; signer identity and verification evidence are required, not a typed
person's name alone. The concrete signing mechanism awaits the appointed parties.
Public/build-visible receipts contain counts, IDs, checks and opaque references only;
no hidden assertions, expected values, patch content or secret locations.

Preserve per-item and per-rerun outcomes; an aggregate pass cannot conceal a missing
case. PENDING means the gate has not been attempted or is awaiting its authorized run.
Once admission is attempted, missing required evidence or any failed control is NO-GO;
only a complete observed pass is PASS. Never emit PASS from static source review.
Exposure invalidates confirmation; preserve the event and stop, do not reseal the same
exposed material as untouched confirmation.

## Pack inventory and roles (§5)

| Split | Tasks and patch inventory | Seeds/references |
|---|---|---|
| P0 independent sample | 3 tasks, one/class; correct and 3 wrong/task | 1 seed, 4 tripwires, 2 references |
| Builder dev after grant | 18 families, 6/class; 18 correct, 54 wrong | 2 dev seeds, 24 checkpoint references |
| Independent held-out | 36 families, 12/class; 36 correct, 108 wrong | 4 held-out seeds, 48 checkpoint references |
| Independent diagnostics | 4 families: 2 ceiling, 2 floor; outside primary estimand | No extra seeds specified |
| Conditional held-out growth | 48 families, 16/class; 48 correct, 144 wrong | No change to four held-out seeds |

Conditional growth is prospective, requires Roy's decision, renewed full admission,
and complete-stage affordability under the cumulative USD40 ceiling (§§7,9). Do not
silently shrink counts/repeats/calibration or substitute 36 after growth is triggered.
Diagnostic patch/check inventory must be explicit in the custodian manifest and
validated in full; this table invents no extra diagnostic quota absent from §5.

Each item carries opaque item/family IDs, split/class, source hashes, author session/
lineage, creation-after-adoption provenance, rights/semantic review references, and
its artifact inventory. Only fresh original standard-library Python microrepositories:
2–6 modules, roughly 80–400 lines. No client/Gauntlet/partner material, historical
sessions, third-party benchmark tasks, scraped datasets, model downloads or personal
canonical skills. Denylist scanning is weak supporting evidence, never originality
proof. Proposed MIT rights are still Roy's decision, not an asserted licence.

### Task and memory records (§5; P6)

Visible task.md, fixture/ and minimal public tests are separate from hidden/, oracle/
and wrong/{1,2,3}/. Logical names describe custody partitions, not permission to put
private data into a product/public tree. Inventory pins each artifact's exact bytes,
role, owner and exposure scope. The custodian transmits sealed visible workspaces
directly to the operator scheduler. Builder receives public manifest/receipt only.

Three balanced classes: memory-independent (fully specified); decision-dependent
(one disclosed synthetic project choice present only in M1/M2, never an answer patch);
misleading-memory (current task/code refutes explicitly stale/decoy facts).
Memory fact fields: id, type (decision/convention/gotcha), status (current/stale/decoy),
provenance, date, value. M1 and M2 retain identical IDs, values, statuses and provenance;
only representation changes. Neutral ballast keeps byte lengths within ±10%, with
native token counts recorded separately. M0 has no memory file. Decision token must
be absent from visible task/fixture. Floor diagnostics require an unknowable constant;
diagnostics never trigger held-out resampling.

Family separation spans P0/sample, dev, diagnostics and held-out, including parameter
families. Pin split seed 11027. IDs alone do not establish disjointness: authorship,
source/family and leak-review evidence are mandatory.

### Seed and checkpoint records (§§5,8; P10)

Dev recipe: invoice-rounding and inventory-reservation libraries. Each seed has 12
ordered feature requests, four always-valid baseline tripwires, four registered README
claims with deterministic tests/anchors and expected checkpoint mappings, and a
reference artifact at every checkpoint. Record seed/split/author/review IDs, baseline
hash, ordered feature/checkpoint IDs, accrued-test sets, tripwire IDs, claim IDs/anchors,
reference artifact hashes and custodian-owned expected behavior references.

The P0 sample has its separately specified two references; it is not a shortened
held-out trajectory. Full dev inventory is 2×12=24 references; held-out is 4×12=48.
No future feature spec/test is exposed early. No reference or oracle artifact is ever
exposed to the experimental agent, including current/past checkpoint references.
Only permitted source/treatment
tree carries between fresh sessions; archive before/after source/memory hashes and
invalid writes. No hidden feedback, oracle repair or rollback. A failed candidate
continues through 12 prescribed sessions unless safety/infrastructure prevents it;
lost infrastructure tree ends that trajectory with remaining checkpoints unknown.

## Grading and refusal boundary (§§3–8,12)

Future GraderPort.grade consumes an immutable artifact and opaque task ID outside
adapter custody. Correct patches/behavior tables are independently authored, never
derived from builder implementation. Required controls apply to every eligible item:
oracle passes, untouched/null fails with null zero, all wrong patches fail, three
reruns stable, all seed references/baselines/features/tripwires/claims valid.

Candidate syntax/import/runtime error, invalid patch, crash, timeout and spend/output
cap after dispatch are scored failures. Missing/tampered grader or failed trusted
self-check is evaluator_error; infrastructure loss is missing, not model failure.
Zero-work auth/rate/container failure may be infra_excluded only with proof of no
tool call/file change. All executed costs remain. Missing slots make primary campaign
INCOMPLETE; preserve all planned slots, no replacement. These distinctions must not
be collapsed by admission records or the future grader.

Before admission runs keep the gate PENDING. At an attempted gate return NO-GO on
absent appointment/signature/rights/semantic evidence,
wrong author/lineage, inconsistent scope/count/hash, leakage/family overlap, unstable
grader, failed oracle/null/wrong control, invalid seed/claim expectation, tampered seal,
isolation/canary breach, early held-out access, or unverifiable evidence. Identify
affected opaque IDs and reason without exposing hidden content. A previously passed
P0 does not cure an invalid full pack. Static format compliance proves none of these
runtime properties.

## Freeze, result embargo and retirement (§§5,7)

Before held-out opening, bind the approved full-pack receipt to a frozen runner,
analysis, treatments, schedule, exact provider/model/settings, image/CLI/code versions,
and budget proof. Preregistration pins suite/task/treatment/code/image/CLI/config/
provider/model/price/analysis hashes, estimands/exclusions, seeds, caps, billing proof,
authorization, schedule and checksum. Changed pins require a disclosed prospective
amendment; no retrospective rewriting. Full-pack admission alone cannot open the pack.

Record every access and lineage exposure. Hidden results stay unread until frozen
final analysis. Custodian/operator enforce the embargo; builder-readable intake
reports only permitted counts/checks/opaque IDs. Any exposure invalidates confirmation.
Retire used held-out material from later confirmation; any later release is manual
and requires separate approval. Do not silently recycle or release it.

## Accepted producer and consumer mappings

Reconciled against accepted product baseline d6a40177379a5494d65110854b9b403bc22de109.
The [shared runner contract](../contracts/harnessrun-v1.md),
[treatment contract](../contracts/treatment-parser.md),
[frozen schedule](../protocol/preregistration-schedule.md),
[trajectory protocol](../protocol/longitudinal.md),
[metrics](../metrics/CONTRACT.md) and [report](../report/CONTRACT.md) retain their
own semantic purposes. This section maps admission inputs to them; it adds no
record type, field or enum to the closed harnessrun/1 wire format.

| Admission concept | Accepted producer/consumer binding |
|---|---|
| P0/full_pack decision and evidence | External admission envelope referenced by frozen registration corpus/custody and authorization; not GradeResult.verdict, AttemptRecord.status or a new harnessrun record. PASS admits only its declared gate/scope, never a task pass, completed campaign, K/L result or dispatch authorization. |
| Admitted pack ID/version/digest | Custodian inventory and seal identify the reviewed corpus; AttemptSpec.suite_id/suite_sha256 identify the admitted suite manifest. Bind both through the frozen registration, with manifest roles/hash scope explicit. Pack/seal, suite and individual task hashes are not interchangeable. |
| Item/family/split/class | Reviewed inventory maps a task ID/hash to suite membership and frozen schedule class/split. AttemptSpec.task_id/task_sha256 carry the visible admitted task binding; family/class/custody evidence remains in the appropriate manifests/registration, not invented runner fields. |
| Planned task slot | Protocol slot ID corresponds to shared cell_id within the same campaign and experiment; preserve the frozen schedule mapping plus arm/repeat, and all linked attempt/launch IDs. A slot with no attempt is unstarted and must remain reportable; it is never omitted. |
| Longitudinal seed/checkpoint | Registration/trajectory manifest binds seed/hash, arm and ordered checkpoint to shared task_id/task_sha256, checkpoint and cell_id; GraderPort's opaque_task_id resolves the exact admitted seed/checkpoint/accrued-test mapping in trusted custody. No inference from bare checkpoint number or public task label. |
| Grading observation | GradeResult binds attempt_id, immutable artifact_sha256, opaque_task_id, grader_sha256 and receipt_ref/receipt_sha256; its pass/fail/evaluator_error enum is a grading outcome, never an admission decision. Resolution must preserve the specific artifact and admitted grader version. |
| Treatment eligibility | Admission leak/fact/source checks refer to treatment/1 and treatment-equality/1 manifests/receipts; semantic fact-set hash differs from exact treatment-file bytes. M0 absence and M1/M2 equality do not establish native loading or probe compliance. |
| Public derived result | Analysis/report retain registration/schedule, gate kind/scope, suite/item, attempt/artifact/grade and input hash references plus provenance. They consume eligibility and outcomes; they cannot generate independent admission or infer it from a metric value. |

These are semantic mappings for DL1/DL3 reconciliation, not an assertion that an
admission schema, registry resolver or export join already exists. In particular,
the shared closed record set has no admission-envelope variant and no direct
preregistration field on AttemptSpec. Preserve external frozen-registration/
schedule bindings; any future additional wire field requires DL1's versioned
contract decision. Do not silently append fields or claim wire compatibility.
The seed/checkpoint-to-task mapping also needs an explicit frozen manifest
definition before implementation; it cannot be inferred from matching names.

Use shared ID/hash conventions when these references enter harnessrun: campaign-
scoped opaque IDs, exact-byte lowercase SHA256 (directory artifacts use a frozen
manifest hash), required nullable fields with reasons for unknowns, and references
that resolve within their declared scope. Missing evidence is not empty data or
a zero measurement. Receipt digest scope must avoid self-reference; this format
does not choose serialization or signing mechanics for independent parties.

### Outcome and visibility handoff

Keep admission state, process status, grading verdict, slot disposition and
measurement provenance separate. A finished process is not a passing grade.
A refused/unstarted attempt or lost artifact has no fabricated GradeResult:
retain the planned slot, attempt status/reason and missing grade/artifact coverage.
A trusted-grader failure may yield evaluator_error; candidate-caused errors stay
scored failures. The protocol/metrics owner maps observations into exclusive slot
outcomes while retaining overlapping operational counts and every incurred cost.

Intake emits only permitted opaque IDs, hashes, inventory/check coverage and gate
references. Hidden grader inputs, oracle/reference code, independent expected
answers, tripwire/claim expected values and hidden results stay in trusted custody.
Before frozen final analysis, reports must not reveal embargoed grading outcomes;
later public redacted exports still require applicable rights/manual approvals.
An opaque reference, even when hash-resolved, grants no artifact access or release
right. Keep task, diagnostic and longitudinal populations and SIMULATED/MEASURED
provenance distinct; source-review receipts are not scientific observations.

For downstream missingness, preserve unknown checkpoints/cells and explicit
unavailability reasons, never a synthetic zero. Metrics retain their fixed planned
denominators, tripwire/claim mappings and reference identity without exposing
private contents. Admission does not define a second rot/statistics algorithm.
All planned slots remain visible even when no grade or launch exists.
## Producer/consumer seams and future acceptance

| Seam | Producer → consumer | Reconciliation owner/trigger |
|---|---|---|
| Receipt/ID/status shape | This specification → DL1 central contracts → P1/P6 intake | DL1 with DL2, before any executable schema grant |
| Independent material | Appointed custodian/human → operator admission → sealed intake | INT/Roy appointments; builders never supply independent answers |
| Visible workspace and immutable candidate | Scheduler/controller → trusted grader | Future P4/P6 owners; mount/candidate binding verified keylessly |
| Longitudinal seed/checkpoints | Dev author or custodian → scheduler/rot/report | Future P10/P12/P11 owners; preserve fixed claims/tripwires and unknowns |
| Gate/campaign status | Operator receipts → prereg/report/authorize | DL3/DL4 and INT; P0/full-pack/K/L never inferred from S review |

Future static acceptance (no execution claimed):

- Confirm P1/P6/P10 fields and counts against §§4–5,8,10; keep conditional growth explicit.
- Confirm two gate kinds, immutable pack binding, evidence coverage and pending/refusal semantics.
- Confirm builder-readable manifests expose no hidden text, answers, grader internals or credentials.
- Confirm author/human/adversarial-session roles, signatures and source/rights records are required.
- Confirm grading failure vs evaluator/infrastructure unknown stays distinct.
- Confirm M0 absence, M1/M2 semantic equality, leak checks, family split and all seed mappings.
- Confirm every consumer has a named reconciliation owner before implementation.

Deferred executed validation: independent P0 appointments/kit/operator reruns; every
full-pack oracle/untouched/wrong/null and three-run stability check; inventory/hash/
tamper/signature/rights/lineage refusal cases; task/seed references, tripwires/accrued
features/claims; split/leakage/isolation/canary proof; sealed intake and hidden custody;
installed-wheel boundary; synthetic grader outcome checks; and K/L authorization
validation. These require later grants and actual evidence. Current status remains
not yet measured, no product/runtime acceptance, no approved spend or live calls.
