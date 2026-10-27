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
All enums and record layouts must be reconciled there before implementation.

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
