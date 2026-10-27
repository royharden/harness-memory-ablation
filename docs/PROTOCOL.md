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
