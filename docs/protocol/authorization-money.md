# Authorization and monetary boundary

Authority: PLAN-M11-v1 sections 3, 6–7, 9, 11–12 and P3/P14.
See [schedule](preregistration-schedule.md). This is a refusal/intake specification;
no account, key, spend, source access, vendoring or live dispatch is authorized.

## Sole monetary authority and intake

The unmodified M9 `src/m9/ledger/` closure is the sole monetary authority behind
`LedgerPort.reserve/begin/settle/snapshot/export`. M11 metadata and reports cannot
independently authorize money. Planning pin
`a0f2bd01b2dcadf9b778cab9cf7ff9a416fe6c30` is provenance, not verified source,
passed tests, availability or a licence. No M9 bytes were accessed for this package.

Authorized future intake must record exact source repository/commit, closure paths
and hashes, original attribution and redistribution rights, unmodified copied-test
inventory and execution receipts. Vendor byte-for-byte; no patches or alternative
ledger. Verify actual inventory rather than assert the six tests reported by planners.
Missing source requires a concrete amendment; missing licence blocks public release.
S3 and a locally recreated monetary ledger are not substitutes.

Each CLI launch maps to one unique valid M9 run_id at stage `draft`. Maintain a
reversible raw-ID mapping and factorial/retry lineage in `m11_attempt_meta`.
Record registration, campaign/stage, slot/attempt/launch, parent/retry-of,
experiment/system/arm/repeat/checkpoint, source-ledger IDs and provenance digests.
Future ID length/alphabet constraints and exact reserve/begin/settle result shapes
must be taken from authorized source; do not invent wire compatibility now.

## Launch monetary transitions

| Transition | Required behavior |
|---|---|
| Planned → reserved | Validate scientific/authorization gates and cumulative headroom; reserve full proven next liability in M9 before process spawn |
| Reserved → begun | Begin once for that unique launch; persist controller/M9 linkage; ambiguous begin never redispatches |
| Begun → observed settlement | Retain actual source-ledger IDs and all costs, including failed/timeout/invalid attempts; handle covered usage only with dated disjoint rates |
| Unknown charge or crash ambiguity | Settle unknown usage with full reservation upper bound; preserve ambiguous reservation/hold; estimates never release headroom |
| Known overbound charge | Record the actual charge and halt new work, even if it exceeds the reserved bound |
| Reconcile | Attach billing-scope receipt separately; never double-enter a tranche aggregate as an additional fee or invent per-arm actual bills |

These are semantic obligations, not asserted M9 state names. Proven-undispatched
retry/release semantics require exact-source inspection and copied tests; never
infer safety from a missing local result. Conservative launch bounds remain held
through campaign close; billing receipts are reported separately. No list-price
estimate, including harness cost fields, frees funds.

## Price and usage record requirements

Keep raw observation digest, usage source `harness_reported`, provider/version,
request/event identity, coverage, cumulative-versus-delta interpretation and dated
immutable `pricetable/1` hash with normalized disjoint billing buckets. Deduplicate
replays; convert cumulative reports to deltas without double billing.

- Codex input100/cached80 means ordinary20 + cached80. Output100/reasoning80
  bills output100 only; reasoning subset remains metadata.
- Claude ordinary input, cache-read and cache-write are disjoint; distinguish
  5-minute/1-hour cache writes when exposed. `total_cost_usd` is an estimate/cross-check.
- Missing/ambiguous counters, date gaps, hidden retries or no matching price row
  mean unknown, never zero or a text-length guess. Keep known subtotal and coverage.
- Subscription ingestion is disabled. Any later token-only ingestion cannot
  supply priced measured cells or allocate subscription fees.

These examples specify accounting semantics, not fixture data or measured usage.

## Cumulative allocation and live refusal

Future authority must enforce across all systems/tranches/keys and diagnostic reruns:

`actual incurred + outstanding upper liabilities + proposed next liability + committed paid external work ≤ USD 40`.

Represent known charges and remaining upper liabilities without counting the same
dollars twice; a retained full launch bound covers that launch's known portion plus
remaining uncertainty. The exact projection from M9 needs source reconciliation.
Use one sequential controller and exclusive cumulative campaign allocation, never
a fresh USD 40 per stage. Include paid authorship, grading/compute and other fees.
Current authorized spend is zero; keyless external spend must remain USD 0.

Before each native dispatch require every relevant reference, scoped to this exact
campaign/stage: P0 and full-pack admission as applicable, rights/custody/no exposure,
frozen preregistration and current pin equality, signed activation/tranche, approved
account/model/terms/credential path, model/version/capability evidence, clean-up and
isolation/delivery gates, complete usage/retry coverage, finite-liability proof,
and headroom. Approval references never contain secret values. Do not read secret files.

Stage A itself requires a verified external hard billing limit. A soft alert,
empirical mean, wall timeout or native budget flag is insufficient. Include any
lag/overshoot and exact scope. Later per-launch proof must bound request context,
output, rates/fees and every in-flight/scheduled/retried/nested/background call:

`U_request = (Cmax × max(input/cache rates) + Omax × output_rate)/1e6 + bounded request fees`

`c_launch = native_stop_threshold + N_after_stop_max × U_request + other bounded liability`

Every term needs exact-model/version evidence. Unknown/unbounded terms refuse
dispatch. Native stop capabilities remain hypotheses until verified; Codex bounds
remain unsupported until demonstrated. No metering proxy is introduced.

Before C/D1, full remaining calibrated equal reservations must fit before held-out
opening, not just the next call. Full Claude A–D1 is 672 launches (780 with growth);
no feasibility is asserted at USD 40. An unaffordable valid design stays unrun.
Do not reduce counts, caps, calibration, failure costs or usage coverage to make it fit.

Stop new scored work on unknown usage/retry coverage, model/config drift, missing
approval/terms, unproven liability/headroom or cleanup failure. Retain artifacts,
missing outcomes and holds. Matching configured IDs alone does not prove fixed
model: require exact requested/provider-returned equality on relevant responses.
Unknown identity blocks fixed-model inference; mismatch stops the headline rather
than relabelling it. Reports distinguish estimates, scope-level actual receipts,
SIMULATED and MEASURED provenance and never promote source review to L acceptance.
