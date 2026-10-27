# Protocol specification index

Status: format-only specification. No product implementation, data, execution,
admission or measurement is supplied here. Native work is disabled. P0 and all
independent, K and L gates remain pending; a USD 40 ceiling authorizes no spend.

The adopted **PLAN-M11-v1.md**, sections 3–9 and packages P3/P8/P12/P14 in section 10,
controls these documents. It is held in the private coordination shell at
`planning/promoted/PLAN-M11-v1.md`, outside the product repository. Section numbers
below are exact references into that immutable plan; these documents do not amend it.
No external/private absolute paths are needed to consume these formats.

- [Preregistration and schedule](preregistration-schedule.md): section 7, P8;
  freeze inputs, planned slots, stable identities and amendments.
- [Authorization and monetary boundary](authorization-money.md): sections 3, 9,
  11–12, P3/P14; source-ledger intake and refusal requirements.
- [Longitudinal transitions](longitudinal.md): sections 6, 8, 12, P12;
  tree carry, missingness and checkpoint handoff.

Field names here are semantic requirements for future shared contracts, not a
second executable schema or invented M9 API. DL1 owns central contract reconciliation.
The accepted producer mappings below reconcile the available seams; implementation,
executable schemas and executed compatibility checks remain pending.

## Accepted producer mappings

Producer definitions are [harnessrun v1](../contracts/harnessrun-v1.md) and
[treatment/parser requirements](../contracts/treatment-parser.md). These mappings
consume those definitions without adding fields or variants to closed records.
Metric/report consumers are [metrics](../metrics/CONTRACT.md) and
[reports](../report/CONTRACT.md); this section supplies protocol linkage, not new
metric formulas. Unknown schema versions, fields, enums or unresolved references
are invalid rather than permission to extend `harnessrun/1` implicitly.

| Protocol concept | Accepted producer representation and consumer rule |
|---|---|
| Planned slot | `AttemptSpec.cell_id` and `AttemptRecord.cell_id` refer to the stable scheduled slot; `campaign_id` scopes it. Preserve the frozen schedule separately so a cell with no attempt remains visible. |
| Attempt and launch | `attempt_id`, `parent_attempt_id`, `retry_of`; `LaunchSpec.launch_id` and `attempt_spec_sha256`; result `AttemptRecord.attempt_spec_sha256` is required and non-null, while `launch_id` and `launch_spec_sha256` are required nullable fields. Do not create a separate wire Result variant. |
| Arm and ordering | `AttemptSpec.treatment_id`, zero-based `repeat`, `experiment_kind` and nullable `checkpoint` (1..12 for longitudinal) resolve to the frozen experiment manifest. Task M0/M1/M2 and longitudinal L0/L1/L2 never merge. Schedule ordinal/block/class, trajectory ID and before/after hashes remain protocol metadata keyed to producer IDs, not extra harnessrun fields. |
| Process versus outcome | `AttemptRecord.status` uses pending/running/finished/timeout/spend_cap/output_cap/crash/refused/cleanup_pending; `process_state` is separate. Scientific pass/fail/evaluator_error comes from `GradeResult.verdict` and protocol missingness evidence. `finished` is not pass, and unstarted cells are not synthetic finished/refused attempts. |
| Cleanup and missing artifacts | `cleanup_pending` blocks dispatch and overrides the process outcome until resolved; prior stop events retain it. Nullable artifact/launch fields remain null when absent. No GradeResult is fabricated without its required immutable artifact hash; missing infrastructure remains a protocol missing checkpoint/slot. |
| Mode and lineage | `AttemptSpec.mode` and `AttemptRecord.mode` retain SIMULATED/MEASURED across schedule/attempt/derived-record joins. A scripted outcome cannot satisfy native authority or enter a measured research table. |
| Exact model | `ProviderConfig.requested_model_id` plus `ModelEvidence` requested/advertised/provider-returned IDs stay distinct; `model_evidence_ids` resolve `model_evidence_id`. `model_coverage` must be complete and every relevant response match before fixed-model wording. A configuration echo cannot supply provider proof. |
| Usage and prices | `usage_observation_ids` resolve `UsageObservation`; preserve scope/counter_basis, disjoint nullable buckets, usage_source and coverage. `pricetable_sha256` binds the dated price record. Partial/unknown usage or a price gap is unknown cost, never zero or released liability. |
| Raw usage provenance | `evidence_ref`, `evidence_sha256`, `source_locator` resolve the redacted hash-bound capture and half-open bytes:start:end range, not a HarnessEvent ID. Deduplicate the raw tuple (attempt_id, evidence_sha256, source_locator); a new observation ID cannot bill replay again. Ambiguous cross-capture replay keeps coverage unknown. |
| Limits and ledger | Use canonical `Limitation.code` plus preserved `raw_code` aliases and evidence; disposition cannot weaken stop gates. `ledger_run_id`/`ledger_reservation_id` resolve actual M9 IDs; other ledger operations remain the existing LedgerPort boundary, not a second monetary total. |

Use producer UTC RFC3339 timestamps, lowercase SHA256 digests, nonnegative finite
numeric domains and required nullable fields with explicit reasons as defined in
harnessrun v1. Protocol metadata must not be injected into its closed JSONL records.
Billing `harness_estimate_usd`, authoritative ledger holds and scope-level billing
receipts stay separate; the accepted contracts require the same retained unknown
reservation semantics as [the monetary protocol](authorization-money.md).

Metrics consume the full schedule plus linked attempts, with operational counts
separate from mutually exclusive scientific dispositions. Infrastructure loss keeps
the fixed planned denominator and unknown bounds; unknown tripwire cells leave
point R unavailable. Candidate failures still continue the produced longitudinal
tree unless a stop gate intervenes. Before/after hash linkage stays in checkpoint
metadata and never sends hidden feedback or reference artifacts to later agents.

## Accepted admission seam

The [admission format](../admission/FORMAT.md) owns receipt, inventory and custody
semantics. The shared [admission crosswalk](../contracts/admission-seam.md) owns
their mapping to closed harnessrun records. Consume those definitions; this
reconciliation neither defines receipt wire fields nor establishes any actual gate.

| Protocol reference | Accepted binding and required disposition |
|---|---|
| Registration gate references | Resolve each gate kind/ID, finalized receipt digest and evaluated pack/scope separately. P0 and full_pack are distinct; P0 PASS cannot replace full-pack admission or authorize held-out opening. Receipt hash scope must be non-self-referential and its signing/evidence references verifiable. |
| Suite and execution item | Freeze an explicit mapping from pack ID/version/digest and inventory to `AttemptSpec.suite_id/suite_sha256` and eligible `task_id/task_sha256`. Pack, suite and execution-visible artifact need not be byte-identical. Preserve both digests and source/family/split/class lineage; opaque IDs alone prove neither independence nor eligibility. |
| Longitudinal seed/checkpoint | The frozen suite mapping resolves the seed, ordered feature/checkpoint and execution item to `AttemptSpec.checkpoint` and `task_id`. Only the current permitted visible unit is dispatched; future requests/tests and any oracle/reference artifact remain outside agent context. |
| Admission decision versus result | PENDING before the authorized gate attempt; an attempted gate with missing/unverifiable required evidence or a failed control is NO-GO; PASS requires complete observed evidence for that gate/scope. None converts to `AttemptRecord.status` or `GradeResult.verdict`. Static format review supplies no gate PASS. |
| Immutable candidate and grade | Resolve the execution item to `GradeResult.opaque_task_id`; require the same attempt and exact artifact hash as `AttemptRecord`, with grader hash and receipt binding. If no candidate exists or no grading occurred, retain the missing slot/checkpoint without fabricating GradeResult. A real candidate with a trusted-grader fault may have an evidenced evaluator_error. |

Before held-out opening, bind the full-pack receipt and immutable suite mapping
to the frozen runner/analysis/treatments/schedule/model/config/image/CLI/code/price
and budget/authority evidence described in [registration](preregistration-schedule.md).
Unresolved, conflicting or changed mappings refuse dispatch or require a disclosed
prospective amendment with renewed applicable gates; never rewrite exposed results.
Admission PASS alone supplies neither native/model proof nor monetary authorization.

Custodian/operator enforce direct sealed-visible-workspace delivery and access
records. Builders/intake/report consumers receive permitted opaque IDs, counts,
checks and receipt references only, never hidden answers, grader internals or secret
locations. Hidden results remain unread until frozen final analysis; no hidden
feedback flows to later longitudinal agents. Exposure invalidates confirmation and
stops affected work; resealing does not restore it. Retire used held-out material
from later confirmation; any release remains manual and separately approved.

Admission check reruns stay in their receipt evidence group, not in the scored
schedule or native launch/ledger IDs. Scored agent failures, evaluator faults,
infrastructure missingness and all incurred costs retain their existing protocol
dispositions. A gate PASS cannot cure incomplete usage/model coverage, release an
unknown M9 hold, erase a missing slot or complete an incomplete campaign.

## Producer and consumer seams

| Record | Future producer | Future consumer | Reconciliation owner |
|---|---|---|---|
| Frozen registration and schedule | preregistration/scheduler | controller, analysis, report, authorization | DL1 contracts; protocol owner for semantics |
| Admission and custody receipts | appointed nonbuilder custodian/operator | authorization and intake | INT for appointments; DL1 for receipt references |
| Attempt/launch identity and lifecycle | scheduler/controller | LedgerPort metadata, store, reporting | DL1 contracts/controller owner |
| Bound and approval references | authorized operator | authorization/controller | INT for approvals; protocol owner for refusal rules |
| Reservation/begin/settlement IDs | unmodified pinned M9 ledger | M11 metadata/store, reporting | protocol owner after authorized M9 intake |
| Checkpoint source/memory hashes | longitudinal controller | trusted grader and reports | controller/contract owners |

The protocol owner currently owns documents only; no listed seam assigns another
seat new work. No builder or reviewer child fills a custodian/human-review role.

## Future static acceptance checklist

After P0/source-construction eligibility and an implementation grant, inspect that:

- frozen records cover every required pin, slot, gate and amendment reference;
  identifiers survive resume, and live concurrency is one;
- controller dispatch requires both valid scientific gates and monetary authority;
  no run flag, estimate or simulated receipt substitutes for either;
- money mutations reach only the pinned M9 closure, with one unique run per launch,
  unknown holds retained and no aggregate billing double entry;
- checkpoint carry never imports hidden feedback, future requests or reference code;
  candidate failure and lost infrastructure take different transitions;
- reports retain every planned slot/attempt, unknown liability and missing checkpoint,
  and cannot label incomplete or simulated records as completed measured research.

This is a future inspection checklist, not an executed acceptance result. Executed
K tests in section 10, native L verification, rights/custody review and source-ledger
tests are deferred. No runtime or empirical claim follows from document review.
