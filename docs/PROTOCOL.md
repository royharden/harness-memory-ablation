# Public analysis and reporting source

Status: runtime-unverified source construction. The detailed
[metrics contract](metrics/CONTRACT.md) and [report contract](report/CONTRACT.md)
remain authoritative; this document does not amend the frozen study plan.

`m11.analysis.analyze_export(payload)` consumes the public producer envelope and
returns `m11-analysis/1`. `m11.report.render_html`, `render_markdown` and
`render_json` consume that result. Analysis owns reference validation, eligibility,
denominators, economic suppression and metric calculation. Rendering cannot admit
data or infer absent values. Planned cells, attempts, class companions, comparisons,
trajectories, limitations and provenance remain separate and visible.

Renderers accept finite JSON-like records, reject unsupported versions, unresolved
or mixed modes, and refuse populated recognized inferential fields in SIMULATED
data. The producer must supply descriptive-only SIMULATED analysis. Lists retain
their input order, including unstarted cells and adverse records; dictionary keys
have deterministic presentation order. Null remains explicit unknown/unavailable.

HTML uses escaped text, a fixed local stylesheet and no links, scripts, imported
resources or embedded JSON. Markdown escapes imported markup. JSON is a separate
artifact. Explicit trajectory `points` arrays may supply numeric `value` fields;
SVG plots use array order, retain unknown gaps and never calculate metrics. Raw
trajectory records remain visible even when a chart is unavailable.

P0 independent admission, independent worksheets, K/L acceptance, runtime rendering,
adversarial execution, wheel integration and publication remain deferred. Source
inspection or AST parsing establishes none of those gates. A supplied MEASURED
label is provenance, not acceptance. Admission, candidate outcome, construction
status and execution gates must remain distinct.

The current consumer uses canonical `m11.campaign.parse_export`, which returns
`PublicExport`, as declared in DL3's source handoff. If unavailable it raises an
explicit export-contract error; it never substitutes a permissive local schema.
Source integration against the actual accepted producer declaration remains a
separate checkpoint. Canonical r1 has no verified released-MEASURED state and its
eligibility flags are literal false. Even MEASURED input therefore remains descriptive
with the producer's explicit inference-unavailable reason. The separate pure
task-cluster helper implements the planned bootstrap and repeat-0 summaries for a
future eligible caller; calling it does not establish admission or acceptance.

`calculate_task_statistics` consumes normalized primary task cells, refusing
non-primary arm/class/repeat shapes and incomplete 36/48 balanced designs. It
returns conditional calculations only; canonical admission, growth and release
eligibility must be established before any research presentation. It refuses
SIMULATED inference. `summarize_trajectory` consumes rot's explicit documented
checkpoint input and produces twelve chart points with per-checkpoint denominator
four; a point is null if any observation is unknown. Its fixed48 trajectory area
and feature-completion records remain separate. Neither helper guesses producer
wire fields. Unpriced reported costs stay distinct from dated-price known subtotals.

Canonical class IDs `independent`, `decision`, `misleading` map explicitly to the
three metric strata; labels are not inferred from task text. Cost `kind` separates
per-attempt `list_price_estimate` from `tranche_receipt`; actual tranche bills are
retained without attempt allocation. Duplicate competing per-attempt estimates
refuse until reconciled, rather than being summed by guessed scope. Ordered
PublicCheckpoint tripwire IDs and boolean/null observations map explicitly to rot's
pass/fail/unknown input. Feature-completed observations, missing reasons, source and
reference evidence stay separate; they do not invent accrued-feature test inventory.

Static source reconciliation of DL1's integrated shared models and pinned DL3
declarations confirms canonical planned cells also carry their scheduler disposition.
Analysis retains that declared value separately from the derived outcome: missing
evaluator/infrastructure/unknown slots remain missing even without an attempt or
fabricated grade. Contradictory terminal declarations and grade/failure evidence
refuse instead of selecting a favorable outcome. A pre-launch refusal remains
unstarted; cleanup/running states remain unknown. This is semantic source inspection,
not executed reference resolution or evidence authentication.

## Export/2 observed claims

Analysis now accepts only canonical `m11-export/2`, with required
`claim_observations`; v1 is explicitly unsupported, with no implicit empty-array
upgrade. The parser still belongs to DL3. `summarize_public_claims` maps exactly
`m11-public-claim/1` records to the normalized claim scorer. Four registered IDs in
their frozen seed order are required at every longitudinal cell, including unknown
records. Candidate/checkpoint bindings are checked; immutable grader/receipt and
embargo eligibility validation stay with the canonical parser. Every original
observation, missing reason and provenance reference is retained in the result.

Observed false presence, false anchor-presence or a failing deterministic test
establish drift; remaining unknown components prevent a passing conclusion. Null
is never inferred deletion/absence. Added unregistered IDs are listed without
scoring or denominator changes. No source-anchor paths, assertion text or expected
answers are invented. The `claims` result section passes through the existing
escaped HTML/Markdown/JSON renderers. Current literal-false eligibility and measured
claim embargo remain unchanged; no source approval enables inference or release.
