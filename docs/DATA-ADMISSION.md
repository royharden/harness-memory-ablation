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

prepare_grade requires verified P0, full_pack for heldout, explicit future runtime
authority, isolated-image/evidence digests and frozen opaque-ID/suite/grader mapping.
It returns a nonexecuted plan only. bind_external_grade requires separately verified
hash-bound m11-grader-execution/1 evidence with identical attempt/artifact/task/grader
and image/isolation, suite and immutable grade-plan bindings. grade_plan_sha256 uses
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
