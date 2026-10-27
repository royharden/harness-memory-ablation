# Report and export specification

Status: format only, runtime unverified and not measured. P0 and K/L gates remain
PENDING — needs Roy. Authority: adopted OUTER `planning/promoted/PLAN-M11-v1.md`,
sections 1–3, 7–9, 10 P13, 12 and 13. Metric definitions are in the single
[metrics specification](../metrics/CONTRACT.md); this document defines presentation
and rejection behavior, not another metric algorithm.

## Public boundary and inputs

Future installed-wheel analyze/report commands consume public result exports;
trusted grading and private data remain outside the wheel in evaluation extras.
Use static escaped HTML/JSON/Markdown with inline SVG; no hosted UI or network
dependency. Analysis produces validated records, and rendering consumes them.
DL1 owns shared export/schema identifiers; DL4 reconciles their imports later.
DL2 owns admission references; DL3 owns protocol/schedule/attempt lineage.
No producer, executable interface or integration is implemented by these docs.

Exports bind schema/analysis versions, campaign/experiment/system/mode, preregistration
hash, schedule and artifact digests, all planned slots and linked attempts, admission
and model evidence references, usage/price provenance, ledger reconciliation and
derived-record input hashes. Validate hashes and references before presenting results.
Tampered or mixed-mode inputs are refused with a clear reason, never silently
repaired or filtered into a favorable table. No report may grant admission or
authorization, open hidden data, run graders or call a provider.

Raw transcripts, secrets, private held-out material and local transcript links are
not public evidence links. Only admitted redacted exports may enter a future public
report; excerpts require manual review before export/publication. Publication,
rights and licences require their separate approvals.

## Accepted producer and display mapping

Read the [metrics producer mapping](../metrics/CONTRACT.md#accepted-producer-mapping)
for joins and scientific eligibility. The accepted
[harnessrun contract](../contracts/harnessrun-v1.md) owns raw record fields;
[protocol schedule](../protocol/preregistration-schedule.md) and
[longitudinal transitions](../protocol/longitudinal.md) supply planned populations
and checkpoint semantics. Rendering does not add fields to closed wire records.

Display `AttemptRecord.mode` and `AttemptSpec.mode` consistently with frozen
registration mode; disagreement is invalid input, not permission to pick a label.
Keep `status`, `process_state` and `GradeResult.verdict` separate in attempt views:
finished never means pass and cleanup_pending never means clean completion.
Pre-launch refusal with null launch/start/artifact fields remains visible with its
reason; dispatched failures retain their costs. Join all attempts to planned slots
without replacing missing cells. Explicit protocol metadata must resolve cell/slot,
seed/task and trajectory identity; unresolved metadata blocks the affected derived
view, not the visibility of the planned population or missing evidence.

Expose usage_coverage and model_coverage as complete/partial/unknown, alongside
nullable fields and unknown_reason. Identity views resolve model_evidence_ids to
ModelEvidence, showing each of the requested, advertised and provider-returned IDs,
evidence_kind and strength. Coverage and provider-response evidence, not a configured
label, control fixed-model wording. Usage observations retain evidence_ref,
evidence_sha256 and bytes:start:end source_locator; these are opaque provenance,
not automatically clickable artifact URLs. Report normalized disjoint usage once;
separate harness_estimate_usd, dated-price analysis and ledger/billing reconciliation.
See the [monetary boundary](../protocol/authorization-money.md).

Import Limitation.code/raw_code and its closed disposition
(stop/retain_descriptive/missing/secondary) without replacing them with display prose.
Report affected campaign/slot/checkpoint IDs by validated joins from attempt_id;
do not add those fields to the closed Limitation wire record. The limitations table
below explains interpretation and gate consequences, not an alternate enum.
Aliases remain recorded in raw_code. Aggregate unavailable reasons such as
undefined_zero_pass are derived-result reasons, not new harnessrun Limitation codes.
No synthetic attempt/limitation row is fabricated for an unstarted slot.

Admission-dependent reference layouts remain pending accepted DL2 formats. Until
then show pending eligibility; do not manufacture a receipt or claim source review
as admission. These mappings establish documentation compatibility only.

## Required views — section 12

| View | Required content |
|---|---|
| Status | Not measured, SIMULATED or MEASURED; complete/incomplete and reasons; P0/full-pack/K/L state separately; exact system/model evidence strength; limitations visible before research claims. |
| Task headline | Experiment/system/arm/class, tasks/repeats, planned/started/completed/pass/fail/evaluator/infra/unstarted/unknown, judged coverage, task effect and interval eligibility, repeat-0 Wilson/McNemar, prominent class companions. |
| Task companions | Per-class results, diagnostics/probes outside primary mix, paired per-task records and exclusions, all attempts and hashes, secondary comparisons, tokens/timeouts/caps/adherence. |
| Economics | Dated-list-price heading, usage buckets/source/coverage and price hash, known subtotal/failure cost, cost/pass and undefined states, bootstrap undefined-draw mass, distinct-task and solved-intersection views, study-total versus arm allocation. Actual tranche reconciliation remains separate. |
| Longitudinal | Seed/arm/checkpoint/system/model, new-feature completion, tripwire failures/R numerator and fixed48 denominator/bounds, first/final failure, secondary established-regression area/denominators, clone/complexity/reference excess, four-claim drift, memory bytes/tokens, cost coverage and divergence. Every seed trajectory gets an SVG. |
| Provenance | All planned slots including unstarted ones, linked launch/retry/parent IDs, immutable artifact and before/after hashes, pins/amendments, failures/missingness, coverage and source references. Never expose private artifact contents by implication. |

Every numeric cell includes its population/denominator and unavailable reason
where applicable. Do not turn null/unknown into zero or omit empty planned cells.
Operational and mutually exclusive outcome counts are distinguished. Missingness
bounds accompany incomplete schedules; exploratory tables are visibly exploratory.
Assigned-arm intent-to-treat remains primary even when memory was not followed.

SIMULATED and MEASURED results never share a research table. SIMULATED reports
contain no inferential table, live-performance assertion or research winner badge.
Unknown usage in either comparison arm suppresses economic ratios; zero passes is
undefined, never an infinite bar. A bootstrap with undefined denominators displays
undefined mass and no ordinary finite interval. Unknown model identity is prominently
`model unverified`; only exact requested/provider-returned equality on every relevant
response supports model-held-fixed wording. Claude versus Codex is always a system
comparison, even with matching IDs. Preserve adverse and null outcomes.

## Escaping and deterministic rendering

Treat every imported field, label, claim, path, error, excerpt and identifier as
untrusted text. Escape HTML text and quoted attributes for their distinct contexts;
escape SVG labels likewise. Generate SVG structure/numeric geometry internally;
never interpolate input markup, style, event attributes or executable URLs.
Do not embed raw JSON inside executable script blocks; serialize as a separate JSON
artifact with a proper serializer. Use a fixed local stylesheet and no imported
script/resource URLs. Disallow raw imported HTML in Markdown; escape text/links,
including table separators and code delimiters, for the output context. Only allow
explicitly safe link schemes/destinations; untrusted paths are displayed as text.
No automatic fetches, embedded files, shell commands or transcript hyperlinks.

Future adversarial checks must cover tags/attributes, quotes/ampersands, closing
script/SVG constructs, event handlers, executable URLs, Markdown links/tables/code
delimiters and Unicode text. These are check categories, not authored fixtures.
Sort by the frozen schedule and stable IDs; preserve complete provenance on export.
Determinism means same admitted input/version yields the same content, not a claim
that rendering or validation has run.

## Limitations registry — section 12

For each occurrence retain code, raw alias, affected campaign/slot/attempt/checkpoint
IDs, detection evidence reference, effect on interpretation and disposition/owner.
Absent evidence remains unknown; rendering cannot diagnose an event from prose.
Aliases normalize only through the documented future central schema.

| Code | Detection input and report disposition |
|---|---|
| unknown_usage | Usage coverage absent/incomplete; show known subtotal and suppress economic claims. |
| unobservable_retry | Nested/retry coverage cannot be established; preserve uncertainty and stop new scored work. |
| budget_bound_unproven | Liability proof absent/unbounded; no new dispatch; do not infer safety from mean cost. |
| undefined_cost_ratio | Unknown cost or zero successes/undefined bootstrap denominator; show reason and undefined mass. |
| model_substitution | Requested/provider model mismatch; stop headline/new scored work, retain descriptive spend/outcomes. |
| model_unverified | Missing provider identity; label model unverified and stop model-fixed headline work. Alias unverified_model. |
| parser_schema_drift | Pinned parser/schema mismatch; retain raw reference, unknown affected fields, no invented usage. |
| global_context_leak | Unexpected context/canary or isolation evidence; admission/exposure breach, stop new work. |
| treatment_not_loaded | Failed behavioral probe or delivery evidence; block harness on probe failure, retain assigned-arm outcomes. Alias treatment_not_read. |
| stale_memory_followed | Recorded adherence evidence follows stale fact; secondary nonadherence, never reassign arm. |
| decoy_followed | Recorded adherence evidence follows decoy; secondary nonadherence, never repair outcome. |
| memory_write_invalid | Invalid memory write receipt/hash; archive and retain nonadherence. |
| grader_flake | Stability/self-check failure; stop new work and mark evaluator/missing outcomes. |
| evaluator_error | Trusted-grader fault/missing/tampered grader or infrastructure evidence; missing, not candidate failure. |
| oracle_circularity | Independent expected-answer lineage invalid/absent; admission pending or invalid, no confirmation. |
| heldout_exposure | Custody/access breach receipt; invalidate confirmation and stop new work. |
| timeout | Dispatched attempt deadline stop; scored failure and cost retained. |
| spend_cap_stop | Dispatched monetary stop; scored failure, retained costs/holds and cap/headroom restriction. |
| agent_error | Candidate error/crash/invalid patch receipt; scored failure. |
| infra_excluded | Evidence of zero-work infrastructure/auth/rate failure; missing slot, incurred costs retained. |
| cleanup_pending | Owned-process cleanup incomplete; block scheduler and preserve ambiguous attempt. |
| workspace_lost | Infrastructure artifact/tree unavailable; end trajectory, remaining checkpoints unknown. |
| trajectory_divergence | Source/memory lineage differs; show affected hashes/checkpoints, no repair or imputation. |
| claim_deleted | Registered claim removed or required anchor missing; counts toward drift numerator/4. |
| metric_unavailable | Syntax/parse failure or zero metric denominator; unavailable, not zero. Alias metric_parse_failure. |
| ceiling | Dev threshold/diagnostic evidence; disclose construction redesign trigger, never resample held-out results. |
| floor | Dev threshold/diagnostic evidence; disclose instrument failure/redesign trigger, never resample held-out results. |

Always disclose the authored class mix, artificial hidden decisions, small Python
libraries, four seeds/no run-variance estimate, custodian-lineage bias, uncertain
backend/config identity, cap truncation, partial loader evidence and generalization
limits. Probes demonstrate behavior in the probe, not use of memory on every task.
Low rot alone does not demonstrate successful feature development.

## Future acceptance and release handoff

README research numbers must be generated from validated analysis records;
unmeasured cells stay unmeasured. Preserve the plan section 1 opening and prior-art
credit; no new leaderboard or general maintainability claim. Instrument acceptance,
measured results and publication approval are separate states.

Deferred P13 checks: complete planned-cell/attempt exports, denominator/coverage and
complete/incomplete gates, unknown/zero-success ratio rendering, model evidence
labels, all seed SVGs, failures and limitations, adversarial output escaping,
tamper/mixed-mode rejection and standalone public stub consumption. Installed-wheel
analyze/report and grading-extras boundary, full keyless journeys, independent
worksheets and live validation all remain deferred. This package performs only
source/diff and Markdown link/path review, with no executable product or fixtures.
