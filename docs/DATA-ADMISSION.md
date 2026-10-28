# Private data admission and evaluation source

Construction checkpoint only: runtime-unverified. Independent P0/full-pack, human
rights/semantic review, instrument acceptance and K/L remain PENDING. The delegated
2026-10-27 source ruling permits this private source, not execution or gate bypass.
The controlling plan and [admission specification](admission/FORMAT.md) retain
authority; older format-only wording describes the earlier phase.

## Separate evaluation closure

evaluation/ is a stdlib private source package outside src/ and the wheel. It never
imports m11 or candidate code, starts a process, installs anything or calls a model.
Its modules are intended for a future approved operator:

- formats: duplicate-key/closed JSON, exact-byte hashes and confined nonlinked paths.
- inventory: caller-enumerated artifact hash inspection; no recursive private search.
- admission: m11-admission/1, external signatures/appointments and per-item controls.
- intake: sealed manifest hash and gate binding; visible-only materialization plan.
- registration: stdlib exact canonical registration/suite/cell/attempt join, no wheel dependency.
- wire: narrow accepted GradeResult ID/Text domains; not a general model parser.
- grade: immutable candidate/opaque-task/grader binding, offline grading plan and
  external verified receipt binding. No candidate or grader execution exists here.
- cli: inspect is HASH_INSPECTION_ONLY; admit has no external verifier context and
  therefore cannot PASS. Do not run these commands in the current construction phase.

An unattempted gate is PENDING. Supplied incomplete, malformed or unverifiable gate
evidence is NO-GO, with the frozen plan's SKIPPED/no execution consequence. No independent
receipt or successful control is supplied by this source.

## Provisional source APIs

assess_gate(raw, root=..., context=...) returns GateAssessment. GateContext is trusted
operator configuration from actual external appointments, builder-lineage registry,
pinned corpus digest and signature-verifier callback. There is no permissive default
or CLI flag making a signer legitimate. The callback must verify exact finalized
receipt bytes/digest against externally appointed authority, including referenced
rights/semantic/attestation evidence. A caller-supplied always-true callback is not a
valid deployment. Missing verifier/appointment/builder registry refuses admission.

Receipt schema_version=m11-admission/1 is closed. See evaluation/admission.py FIELDS,
REQUIRED_CHECKS and _items for the single source definition. It separates P0 and
full_pack, enforces class/count/reference/diagnostic/human-audit coverage, distinct
adversarial lineage and complete per-item/control coverage in each of three distinct explicit run IDs. The operator session, kit/config/image hashes
and exact Python3.12 patch version must match trusted operator context; each unique
item grader hash needs separate adversarial-session evidence coverage. Receipt hash is
outside the finalized receipt bytes, avoiding self-reference. No sample filled
receipt, signature, oracle or independent expected answer is provided.

Evidence files are read only under the externally selected custody root with exact
hash checks, no links, path traversal or arbitrary imports. Hash equality proves
byte identity only; external human/semantic and adversarial review establish what
the signed controls mean. This does not infer rights, originality or independence
from hashes. D11 remains private-only; MIT is a proposal.

prepare_visible_intake accepts a closed m11-sealed-pack/1 manifest (pack_id,
artifacts). Artifact entries are path, sha256, visibility (visible/trusted).
It verifies the pinned pack/receipt before returning visible identities only.
Trusted paths/contents never enter its result. The future operator must enforce
mount separation and exposure logging; a plan is not materialization evidence.

prepare_grade requires verified P0, full_pack for heldout/diagnostic, explicit future runtime
authority, isolated-image/evidence digests and frozen opaque-ID/suite/grader mapping.
It returns a nonexecuted plan only. bind_external_grade requires separately verified
hash-bound m11-grader-execution/1 evidence with identical attempt/artifact/task/grader
and image/isolation, suite and immutable grade-plan bindings. Current m11-grade-plan/2 requires a registration_binding_sha256 and rejects historical
source-only plan/1 rather than silently adapting it. GradeRequest now requires that
binding digest. grade_plan_sha256 uses
UTF-8 sorted-key JSON with compact separators, non-ASCII preserved and nonfinite
numbers refused, without any self-hash field. The resulting GradeResult uses accepted harnessrun
fields but does not import its wheel. No grade is fabricated for absent artifacts.
Model failures versus evaluator/infrastructure missingness stay in the protocol.

DL1 owns shared GradeResult reconciliation; DL3 owns suite/registration/export
joins. Neither local pack IDs nor gate verdicts are interchangeable with their wire
fields. Concrete serializers/signature mechanisms, the trusted verifier provider,
frozen suite mapping and isolated executor remain external integration seams.

## Builder-owned development source

fixtures/dev and fixtures/seeds contain original builder-lineage dev-only material
authored after adoption. Their manifests name exact author sessions, private-only
rights and NOT_RUN status. They are not P0, held-out material or independently reviewed
expected answers. Correct/wrong/reference source is not a claimed oracle result.
Do not dispatch dev source before actual P0 and runtime authority. No hidden feedback
or reference artifact can enter a later experimental agent's workspace.

See [custodian packet](admission/CUSTODIAN-PACKET.md) for unfilled external work and
[dev authoring boundaries](admission/DEV-AUTHORING.md) for development custody.

Deferred execution: actual P0 appointments/kit/signatures/operator reruns; all oracle,
wrong/null/stability, seed/tripwire/claim and isolation checks; tamper/refusal and
wire/export integration; external-signature verification and TOCTOU-resistant mounted
custody; installed-wheel boundary and all K/L checks. Static inspection proves none.

## Joined source r4 — accepted producer names

Source reference: joined master d77f78d, harnessrun.models.GradeResult and
m11.campaign SuiteManifest/Registration/PlannedCell/SuiteTask/SeedCheckpoint.
No producer module is imported or invoked by evaluation.

evaluation.registration.prepare_registered_grade consumes exact canonical serialized
suite/registration/cell/attempt bytes plus FrozenJoinAuthority and actual existing
GradingAuthority/GateContext/verifiers. FrozenJoinAuthority has pinned suite and
registration digests and a mandatory caller verify_graph callback. The callback must
validate accepted complete closed producer models AND the frozen schedule/attempt
graph; this narrow stdlib join does not reimplement those validators. Missing callback
refuses. An always-true callback is not authentic caller authority or a valid deployment.

The bridge checks suite_sha256, campaign_id/registration_id, cell_id/attempt_id,
retained candidate artifact, execution task/hash/class, and exact seed/checkpoint or
task-to-opaque_task_id mapping. Cells without a retained exited artifact are unavailable;
no synthetic attempt/grade fills them. Probe/smoke grading is not silently reinterpreted.

m11-registered-grade-binding/1 pins registration/suite/cell/attempt canonical digests,
execution task/seed/checkpoint, mode/split, artifact and grader identity. Its digest is
inside m11-grade-plan/2, so the existing external execution receipt's full grade-plan
digest binds that exact registration join. bind_registered_grade checks the closed
binding and delegates actual signature/receipt checks to bind_external_grade.
Returned GradeResult has exactly harnessrun/1 fields and accepted Identifier<=256,
Text<=4096 domains with control characters refused. No extra suite/registration fields
are inserted into GradeResult. The binding envelope preserves their separate purpose.

This source emits neither PublicExport nor eligibility nor observed claim records.
Current public source refuses independent PASS and released MEASURED hidden outcomes;
the bridge does not bypass those restrictions. New m11-export/2 and
m11-public-claim/1 are owned by DL3. Registered claim IDs and builder reference
expectations never manufacture observed presence/anchor/test state. Consume their
actual published versioned DTO through the public producer, not shape fallback.
No filled observations, gate evidence or independent material is supplied here.
## Round2 missing authority handling

Construction disposition: accepted for construction, independence PENDING - Roy,
runtime-unverified. No current builder/child may act as delegated custodian, author,
verifier or evaluator stand-in. Only a later actual fresh nonbuilder seat is eligible
for separately scoped stand-in preparation; it remains not human-independent.

GateContext now requires independence_basis=human_independent before an independent
gate can PASS, plus all existing genuine human/signature/evidence checks.
Missing basis or delegated_stand_in refuses; the latter never converts construction
evidence to independent admission. Identity/lineage/appointment/evidence marker values
are refused explicitly, including named placeholders and pending/unknown entries.
Signature and external-grade receipt verifiers must be actual callables; a string
naming an unavailable verifier is refused before invocation. An always-true callable
still is not authentic authority and is not supplied by this source.

The [unfilled launch packet](admission/NONBUILDER-LAUNCH.md) lists every introduced
named placeholder. Run-local placeholders/DL2.json records the same names, locations,
required actual values and owners, all operational=false. The next non-Dirty integrator/
authorized operator fills real values only under the standing limits. Grade-plan/2,
frozen registration joins, builder dev source, NOT_RUN/private-only status, wheel
boundary and runtime/independent result embargo remain unchanged. No filled identity,
receipt, signature, independent answer or actual verifier implementation is provided.