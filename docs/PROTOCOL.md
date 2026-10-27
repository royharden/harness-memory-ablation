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

The current consumer targets the provisional `m11.campaign.PublicExport` producer
name. If unavailable it raises an explicit export-contract error; it never substitutes
a permissive local schema. Cost-observation field names and eligibility metadata
need producer reconciliation before source coherence is claimed. Until admission,
freeze and result-embargo eligibility can be resolved, even MEASURED exports produce
descriptive output with an explicit inference-unavailable reason. The separate pure
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
