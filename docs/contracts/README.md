# M11 contract specifications

Status: proposed format specification for P2/P4/P5/P7; no implementation,
conformance execution, P0 admission, capability verification or measured result.
All K/L and independent gates remain pending. Dirty Mode permits this source
review only. These formats do not grant dispatch, spending or publication.

The controlling source is OUTER `planning/promoted/PLAN-M11-v1.md`, adopted
2026-10-27, original payload SHA256
`0126184f9d0ddd2de1f0fe4c9e7fb5c170d5676004c0a023bf8fe63d53c8e99c`.
That private plan is deliberately not a distributable dependency of harnessrun.
References below name its exact numbered headings. A conflict goes to INT; this
specification cannot amend the frozen plan.

| Specification | Controlling plan sections |
| --- | --- |
| [harnessrun v1](harnessrun-v1.md) | 3. Exported runner contract — harnessrun v1; 6. Isolation, native delivery and model evidence; 9. Monetary authority, token pricing and $40 activation; 12. Reporting, stopping and known failure modes |
| [Treatment and parser requirements](treatment-parser.md) | 5. Data, authorship and custody; 6. Isolation, native delivery and model evidence; 7. Preregistered task experiment; 8. Separate longitudinal experiment and exact rot metrics; 9; 10. Build packages — 14, after P0 and later Roy launch |

## Producer and consumer seams

DL1 owns central contract reconciliation. Future implementation names below are
interfaces, not paths created or grants activated by these documents.

| Producer | Consumer | Shared boundary and reconciliation |
| --- | --- | --- |
| Scheduler/preregistration (P8/P12) | HarnessPort.prepare; controller (P4/P7) | AttemptSpec binds one scheduled cell and attempt to frozen pins; missing launch never becomes an adapter success |
| HarnessPort.prepare (P7) | Controller/workspace (P4) | LaunchSpec is data; only controller spawns/kills, checks reserve/begin and records cleanup |
| Native/null/scripted adapters (P2/P7) | Store/accounting/report (P2/P3/P13) | Closed parsed records; raw provenance and unknowns retained; no adapter grades or authorizes money |
| LedgerPort (P3) | Controller/schedulers | Actual M9 IDs; reserve/begin/settle/snapshot/export; M11 metadata is not another money authority |
| Treatment builder (P5) | Workspace/controller and preregistration | Equality receipt and path/hash manifest; same-content constraint fails closed before dispatch |
| GraderPort (P6, outside adapter custody) | Store/analysis/report | Immutable artifact and opaque task ID yield pass/fail/evaluator_error; no hidden content in public export |
| Public harnessrun closure (P4) | Future S42/M22 consumers | Small public schemas and null/scripted conformance closure, no private m11/evaluation import; consumer integration deferred |

No consumer in another app is edited or required to exist. Native capabilities
remain hypotheses until pinned-version verification. A future consumer must reject
unknown schema versions rather than silently reinterpret fields.

## Future static acceptance checklist

- Trace every required pin, ID, status and nullable field through prepare, parse,
  store and export without secret values or fabricated zeroes.
- Check closed record variants, rejection of unknown fields, finite numeric
  domains, references, SIMULATED/MEASURED separation and alias preservation.
- Trace replay/delta scopes, final-versus-incremental usage and billing subset
  semantics; ensure estimates cannot release M9 liabilities.
- Inspect argv arrays, mount/environment allowlists, workspace boundaries,
  controller-only process ownership and ambiguous-begin refusal.
- Inspect treatment equivalence, M0 absence, immutable task memory and explicit
  longitudinal update permission.
- Check exported closure has no private dependency or hidden-data content.

These are future review targets, not completed implementation checks. Executed
schema roundtrips, parser conformance, loader/probe behavior, process cleanup,
isolation, M9 behavior, installed-wheel imports and native/model/billing evidence
are deferred until separately authorized. P0 remains a prerequisite to product
implementation under the current grant.
