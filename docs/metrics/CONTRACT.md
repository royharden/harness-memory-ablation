# Metrics specification

Status: format only; no implementation, data, expected-answer worksheet or executed
validation. P0, independent worksheets and K/L acceptance remain PENDING — needs Roy.
The adopted OUTER `planning/promoted/PLAN-M11-v1.md`, sections 7, 8, 10 (P9/P11),
11 and 12, controls these definitions. This document translates those sections for
future producers and consumers; it does not amend the plan.

## Input and ownership seams

DL1 owns shared schemas and their eventual identifiers. Analysis consumes frozen
schedule slots, all linked attempts, immutable artifacts, grading receipts, usage,
model evidence and the authoritative M9 ledger export. It must not infer a missing
slot from the attempts table alone. Each derived record retains source IDs, input
hashes, preregistration/analysis version and provenance mode. DL4 owns future
analysis/rot/report behavior only after a separate implementation grant.

DL2 admission receipts establish data eligibility; report code cannot manufacture
admission. DL3 protocol/scheduler records establish planned cells, disposition and
trajectory lineage. These are proposed consumer requirements for reconciliation
with those owners, not new central schemas or proof that producers exist.

Every numeric result carries a definition/version, value or explicit unavailable
reason, numerator/denominator where applicable, population, mode, coverage and
input references. Missing is never implicitly zero. SIMULATED and MEASURED inputs
cannot form one research table or estimate. Simulation produces no inferential table.

## Task outcomes and missingness — section 7

Primary schedule: 36 tasks, balanced 12/class, three arms M0/M1/M2 and three
repeats: 324 study slots per primary system. Four diagnostics × three arms × one
repeat are a separate 12-slot population. Optional Codex remains a separate system
comparison. Any growth to 48 requires the plan's prospective decision and gates;
never infer it from observed rows or reduce the scheduled design for affordability.

After dispatch, candidate syntax/import/runtime errors, invalid patches, crash,
timeout and spend/output-cap stops are scored failures. Trusted-grader self-check
failure, missing/tampered grader and infrastructure loss are evaluator/missing
outcomes. Zero-work auth/rate/container failure is `infra_excluded` only with
evidence of no tool call or file change. Preserve every attempt and its cost,
including excluded, diagnostic and invalid attempts. No best-of or replacement;
one success maximum per scheduled slot. An ambiguous begin is not replayable.

Show planned, started, completed, pass, scored failure, evaluator_error,
infra_excluded, unstarted and unknown counts with explicit definitions. Started
and completed are operational counts, not mutually exclusive outcome categories;
partition terminal slot dispositions separately to prevent double counting.

Completed primary requires all three repeats in every arm for every prespecified
task. Scored agent failures are outcomes; missing infrastructure/grader slots make
the campaign INCOMPLETE. Show operational success over planned slots and worst/best
missingness bounds (unknown pass indicators set to zero/one, fixed planned
denominator). Do not use those bounds as a completed-primary point estimate.
Exploratory complete-task blocks require all arms/all three repeats for each
included task. Available-repeat summaries expose per-task and per-arm denominators.
Fewer than two independent tasks yields no estimate or interval.

## Statistics — sections 7, 10 P9 and 11

For a completed primary, `d_t = mean_3(pass_M2) - mean_3(pass_M0)` and the primary
effect is the task-weighted mean, conditional on the frozen equal class mixture.
Prominently show descriptive by-class differences; M2−M1, M1−M0, optional Codex,
repeat variability, tokens, caps, adherence and diagnostics are secondary/unadjusted.
M2−M0 combines information and discipline; M2−M1 is the narrower representation
comparison. Assigned-arm intent-to-treat is primary; adherence is secondary.

Task-cluster bootstrap: 10,000 draws, seed 11028, draw 12 task IDs with replacement
within each class (16 only for authorized 48-task growth), carry all repeats, arms
and cost vectors together and retain equal class weights. Never sample attempts as
independent observations. Label degenerate bootstrap degenerate/unavailable, not
certain. Wilson and exact two-sided McNemar use repeat 0 only; do not pool 108
task-repeats as independent tasks. All-repeat rates use task-cluster uncertainty.
Partial/exploratory populations and paired exclusions must be disclosed explicitly;
never promote them to the prespecified completed primary.

Independent statistical worksheets must precede porting. Their author/custodian
and expected answers remain external to this package. Future K checks include
Wilson boundary/interior cases, exact McNemar, paired bootstrap against an
independent reference, tolerance 1e-4, task/class weights, partial blocks and six
pairing/exclusion cases from P9/section 11. This specification supplies no answers.
No winner badges, equivalence claims or favorable interim stopping.

## Economics — sections 7, 9 and 12

Heading: **estimated at dated list prices**. Per arm, sum every executed
launch/nested-usage estimate, including failure, timeout and infrastructure costs,
then divide by passing scheduled slots. Also expose distinct tasks solved,
cost/distinct-task-solved, failure cost, known subtotal, coverage and the
solved-intersection view. Identify study totals versus allocated arm analysis
costs: diagnostics and invalid attempts remain in incurred study totals.

Unknown cost in either comparison arm suppresses cost/pass and comparative cost
ratios; no complete-case economic headline. Coverage below 100% suppresses cost
claims and blocks new scored work while valid descriptive pass outcomes remain.
Zero passes yields unavailable `undefined_zero_pass`, never infinity or zero cost.
Recompute ratios inside each paired task-bootstrap draw; expose undefined-draw
mass and suppress an ordinary finite ratio interval if any denominator is undefined.
Do not discard undefined draws or substitute their values.

Keep usage buckets/source/coverage, price date/hash, harness estimates, ledger
reservations and tranche-only actual reconciliation distinct. List-price estimates
are not actual charges or headroom releases. Unknown actual costs retain their
holds under M9. No duplicate monetary authority belongs in analysis/report code.

## Longitudinal and rot — section 8

Separate Claude experiment: four seeds × three arms × twelve checkpoints, one
trajectory each (144 launches). Two dev seeds × three arms × twelve sessions are
separate calibration. No Codex longitudinal MVP. L0 source only; L1 static prose;
L2 typed memory plus read/update permission. L2−L1 bundles updating with structure.

For each seed/arm, R is the sum of failed tripwire indicators across twelve
checkpoints and four always-valid baseline tripwires, divided by 48. Display raw
failure numerator, fixed denominator 48 and unknown-cell count. Lower/upper bounds
set unknown cells to zero/one; point R is unavailable when cells are unknown.
Persistent failure counts at every checkpoint; recovery ends that contribution.
Generated code preventing execution is a tripwire failure; lost infrastructure
artifact is unknown. Reference R is zero; display excess over reference.

Show each seed trajectory and paired L2−L0/L1−L0 signs descriptively. No pooled
session p-value or general confidence claim from four seeds; run variance is
unmeasured. New-feature completion is separate from rot. A null seed can retain
R=0 with no new features completed. Report final tripwire failures, first failure,
and secondary established-regression area: a feature test joins after its first
pass; expose arm-dependent denominators and activation checkpoints.

Sessions continue from produced trees despite scored failures, without repair or
rollback, through twelve requests. Infrastructure tree loss ends the trajectory;
remaining checkpoints are unknown. Preserve every before/after source/memory hash,
invalid memory write and divergence reference; do not infer later artifacts.

## Frozen source metrics — section 8, P11

`clones/1`: tokenize Python; remove comments/layout/newline/indent/dedent/endmarker;
retain keywords/literal values; replace nonkeyword NAME with ID. Token ownership
is unique to function/lambda scope; exclude nested function/class body tokens from
parent ownership. Slide 30-token windows at stride 1 within each function body.
Match identical windows only across different function bodies, union participating
source token positions (each overlapping position once), divide by all significant
function-owned positions. Zero denominator is unavailable. Show fraction and
same-checkpoint reference excess; syntax failure is unavailable, never zero.

`complexity/1`: per function/lambda start at 1; add If, IfExp, For, AsyncFor,
While and ExceptHandler counts, comprehension if clauses, each match_case except
a final bare wildcard, and `operands - 1` per BoolOp. A bare wildcard is final,
unguarded MatchAs with no pattern/name; guarded wildcard counts. Stop parent
traversal at nested FunctionDef/AsyncFunctionDef/Lambda/ClassDef; independently
count child functions/lambdas, never class bodies as functions. Function length
uses def/end lines excluding nested source lines from parent. Publish function
sum/count/max, longest length and same-checkpoint reference excess. This is M11's
disclosed count, not standard cyclomatic complexity. Syntax failure is unavailable;
tripwire failure disposition remains separately visible.

README drift uses exactly four registered assertions per seed with frozen
deterministic tests, claim IDs/source anchors and checkpoint expectation mappings.
False, deleted or missing-anchor assertions count in numerator/4. List unregistered
additions unscored. No model/Jev judgment changes correctness, rot or drift.

## Future acceptance handoff

Static reconciliation: DL1 confirms shared field names and mode/unknown enums;
DL2 confirms admission references; DL3 confirms schedule and trajectory dispositions.
DL4 checks formula/version alignment and report consumption against those contracts.
No schema import or producer availability is established in this phase.

Deferred P9/P11 execution includes independent worksheets; failure-cost/unknown/
zero-pass and undefined-ratio cases; mixed provenance refusal; persistent/recovering
tripwire area and infrastructure bounds; shifted/overlap clone union; nested
scope/lambda/guarded wildcard and syntax-unavailable checks; deleted claims and
null-R versus feature completion. No fixtures or evaluation data are authored here.
