# Admission to shared-contract mapping

Format-only reconciliation of accepted [admission FORMAT](../admission/FORMAT.md)
with [harnessrun v1](harnessrun-v1.md), [treatments](treatment-parser.md) and
[protocol scheduling](../protocol/preregistration-schedule.md).
Controlling source: PLAN-M11-v1 sections3–5,7–8,10 P1/P6/P10,12 as identified in
the [contract index](README.md). This is a semantic crosswalk, not wire
compatibility, an executable schema, a gate receipt or an admission decision.
P0/full-pack/K/L and independent rights/semantic verification remain pending.

## Identity and binding crosswalk

| Admission concept | Shared-contract binding | Required distinction |
| --- | --- | --- |
| gate kind, gate ID, receipt artifact digest | Registration's P0/full-pack gate references resolve the finalized admission receipt and its scope | Neither gate ID nor receipt digest is an attempt/cell ID; P0 PASS never substitutes for full_pack PASS |
| pack ID/version/digest and inventory | Frozen registration resolves the admitted pack to AttemptSpec.suite_id/suite_sha256 and its eligible execution items | Pack and suite need not be identical artifacts; pin the explicit mapping and both digests, not an assumed equality |
| opaque item/family ID, split/class and source hashes | Frozen suite mapping resolves AttemptSpec.task_id/task_sha256 and the execution-visible workspace manifest | Preserve family/split/class in the manifest; opaque ID alone proves neither family separation nor originality |
| seed ID and ordered feature/checkpoint IDs | Suite mapping binds each longitudinal execution item to its seed, prescribed feature request and AttemptSpec.checkpoint (1..12) | task_id here identifies the execution item, not a relabelled held-out task family; visible unit/hash cannot resolve to hidden references or future requests |
| immutable candidate and opaque grading task ID | AttemptRecord.artifact_sha256 joins GradeResult.artifact_sha256; suite mapping resolves AttemptSpec.task_id to GradeResult.opaque_task_id | Require same attempt and exact candidate, with pinned grader hash and receipt; display aliases cannot substitute for the authoritative mapping |
| admission operator/kit rerun IDs and evidence | Admission receipt execution group retains its own reruns/source/config/image/Python pins | These are admission checks, not scored attempts, native model evidence or paid launch ledger IDs |
| author_session, lineage, reviewer identity, rights/semantic and signing evidence | Admission receipt/manifest owns these requirements; registration pins permitted references | Harnessrun provenance hashes resolve captures; they do not prove independent authorship, rights, signature validity or human review |

The registration/suite mapping is immutable and digest-bound before dispatch;
unresolved, conflicting or changed mappings refuse dispatch. No new fields are
implicitly added to closed harnessrun/1 objects. Admission receipt fields remain
semantic groups until separately authorized schema/signing work. Bind the finalized
receipt digest using the admission format's non-self-referential hash scope.

## Gate, process and grading lifecycle

Admission PENDING means no authorized attempt of that gate is complete; an
attempted gate with missing required evidence or a failed control is NO-GO.
PASS applies only to that fully observed gate and scope. These uppercase decisions
never map to AttemptRecord.status or GradeResult.verdict by string conversion.
Static format review supplies none of them. P0 is construction admission under
the frozen plan; full-pack admission separately precedes held-out freeze/opening.
Neither decision grants live authorization, source access, spending or publication.

AttemptRecord.status describes controller lifecycle (pending/running/finished,
timeout, spend_cap, output_cap, crash, refused, cleanup_pending), not gate validity
or scientific success. A finished process can grade fail; a dispatched timeout,
cap stop, crash, bad patch or candidate syntax/import/runtime error is an agent
failure. Trusted-grader missing/tamper/self-check fault is evaluator_error;
infrastructure loss is missing. infra_excluded still requires evidence of no tool
call/file change. Keep all executed costs and unknown usage; no gate PASS cures
incomplete coverage, ambiguous begin/replay or cleanup_pending.

GradeResult requires an immutable artifact hash and grading receipt. If the
artifact was lost or grading never occurred, do not fabricate an artifact hash,
pass/fail or GradeResult merely to fill a row. Preserve AttemptRecord's nullable
artifact and the planned cell's missing/evaluator disposition in the scheduler
and report mapping. Where a real candidate exists but trusted grading fails, a
GradeResult may record evaluator_error with evidence of that fault. Missing
grader/infrastructure slots make the primary campaign INCOMPLETE, not agent fails
or silently replaced cells. Lost longitudinal infrastructure ends the tree with
remaining checkpoints unknown; a retained failing candidate continues as prescribed.

## Visibility and unchanged producer rules

Admission mappings expose only permitted opaque IDs, counts, checks and receipts.
No hidden expected values, patches, grader internals, secret locations, future
feature requests/tests or reference artifacts go to agents or public exports.
Hidden results remain unread until frozen final analysis; any exposure invalidates
confirmation and stops the affected work. Retire used held-out material from later
confirmation; later disclosure requires separate approval.

M0 absence, M1/M2 six-field fact equality including stale/decoy status, neutral
ballast and token/leak checks remain governed by the treatment specification.
Longitudinal before/after hashes and update permissions remain distinct from
static task treatment. Admission source hashes never replace usage raw-capture
byte-range provenance, model evidence, disjoint billing buckets or M9 reservations.
SIMULATED controls cannot become measured inference or independent admission.

Future static acceptance: trace each mapping above through registration, suite,
attempt, grading and report while retaining all source digests and custody limits.
Executed admission, signature/hash/tamper checks, sealed intake, grader controls,
source access/isolation and lifecycle behavior remain deferred. No sample evidence,
independent expected answers, task fixtures or grader code is created here.
