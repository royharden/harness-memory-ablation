# Preregistration and schedule formats

Authority: PLAN-M11-v1 sections 3, 5–7, 9–10 (P8), 12.
See [authorization](authorization-money.md) and [longitudinal](longitudinal.md).
Format-only; no frozen campaign or admission receipt exists here.

## Registration envelope

A future immutable registration records these semantic groups. References must
resolve to content digests, versioned records and attributed receipts, never secrets.

| Group | Required content |
|---|---|
| Identity | registration ID/version, campaign and experiment kind, SIMULATED or MEASURED provenance, creation time, signer/authority references, canonical serialization version and digest |
| Corpus/custody | suite and task/seed hashes, class membership/counts, split seed 11027, original-source/rights and human-review receipts, P0 and full-pack gate references, seal and exposure/access record references |
| Intervention | all treatment/fact/discipline hashes, materialization paths, semantic-equality and length/token records, arm definitions and immutable task-memory policy |
| Execution | code, image/binary, CLI, configuration, provider profile, requested exact model/settings and analysis hashes; requested/advertised/provider-returned identity evidence policy |
| Design | estimands, class weights, exclusions, missingness policy, diagnostic separation, complete ordered schedule/checksum, randomization algorithm/version with seed 11027, analysis seed 11028 |
| Resources | wall/output/turn limits, equal treatment thresholds, calibrated cost and overshoot evidence, immutable dated price-table hash, finite-liability proof, cumulative allocation and external paid commitments |
| Authority | exact authorized stage and scope, account/model/terms/credential-reference approval, signed activation and tranche references; secrets are excluded |
| Evolution | parent registration/amendment digest, reason and prospective effective boundary, preserved old schedule and consumed slots |

Freeze runner, analysis, treatments, schedule, model/image/CLI/settings and budget
proof before held-out opening. Authoring may be external; builders see only admitted
public manifests and receipts. Hidden results remain unread until frozen final analysis.
An exposure invalidates confirmation, rather than creating a repair opportunity.

Registration states: DRAFT → FROZEN; a change yields a distinct prospective AMENDMENT
linked to preserved FROZEN bytes. Verification compares current pins/checksum and
scope to that frozen record. Missing evidence or a changed pin refuses dispatch.
No retrospective rewrite may bless already exposed outcomes. A scientific redesign
requires the prospective signed amendment and renewed applicable gates.

## Schedule and identities

A planned slot binds campaign/registration, system, experiment, task or seed,
class where applicable, arm and repeat or checkpoint. A schedule row also records
stable slot ID, immutable ordinal/block/arm order and schedule digest. An attempt
binds that slot to attempt ID, launch ID, parent/retry-of lineage, immutable
AttemptSpec/LaunchSpec hashes, workspace reference and the source-ledger run mapping.
These are distinct identities: a planned slot exists even if never launched.

The scheduler permutes task/repeat blocks with seed 11027 and balances arm order.
The exact deterministic algorithm and its version must be frozen with the complete
schedule; the plan supplies no algorithm-specific output to fabricate here.
Resume reads the original IDs/order and durable lifecycle, never regenerates or
replaces missing cells. Live concurrency is one. No automatic outer retry,
replacement or best-of selection. Requested reruns belong to separately disclosed
diagnostic campaigns and the same cumulative app budget. Ambiguous begin never replays.

| Stage | Fixed design | Launch count |
|---|---|---:|
| A Claude smoke/probe | 3 smoke + 9 behavioral probes | 12 |
| B Claude dev calibration | 18 tasks × 3 arms × 2 repeats | 108 |
| C Claude task | 36 tasks × 3 arms × 3 repeats + 4 diagnostics × 3 arms | 336 |
| D0 Claude longitudinal dev | 2 seeds × 3 arms × 12 sessions | 72 |
| D1 Claude longitudinal held-out | 4 seeds × 3 arms × 12 sessions | 144 |
| E optional Codex task system | 12 canaries + 336 task/diagnostic launches | 348 |

Stage C contains 324 study slots and 12 diagnostic slots. Diagnostics have one
repeat, remain outside the estimand and cannot trigger held-out resampling.
Primary task arms M0/M1/M2 and longitudinal arms L0/L1/L2 are different experiment
labels, not interchangeable slots. Codex longitudinal is outside MVP.
Conditional growth to 48 tasks changes C to 444 and E to 456; it requires Roy's
prospective decision, extra independent material, renewed admission and affordable
complete-stage bounds. If the adopted dev-sd growth trigger >.55 fires and growth
is unavailable, do not silently fall back to 36. Never shrink counts to fit USD 40.

## Caps and outcome handoff

Provisional dev wall limits are 900 seconds/task, 1200/session, output 10 MiB.
Freeze final task wall cap at twice maximum successful dev duration, clamped
600–1800 seconds; session cap analogously uses full dev-seed calibration and
900–2400 seconds. No successful calibration blocks held-out opening. Money
threshold is at least twice maximum successful dev estimated cost and twice dev
P99, plus proven overshoot; equal across arms. Wall time is no monetary bound.

Preserve controller status separately from scientific outcome and usage coverage.
Agent syntax/import/runtime error, invalid patch, crash, timeout or spend/output
stop after dispatch counts as agent failure. Trusted-grader fault/tampering or
infrastructure loss yields evaluator_error/missing. Zero-work authorization,
rate or container failure is infra_excluded only with evidence of no tool call
and no file change. All incurred costs remain, whatever the outcome.

Complete primary requires every prescheduled repeat in every arm/task. Scored
agent failures are observed outcomes; missing grader/infrastructure slots make it
INCOMPLETE. Report all planned slots, operational success and worst/best missingness
bounds. Exploratory complete-task blocks require all repeats/arms for each included
task; available-repeat views expose denominators. Under two independent tasks gives
no estimate/interval. No missing slot is replaced or excluded to claim completion.

Analysis consumes task-weighted records, preserving the frozen equal class mix,
all repeats/arms/cost vectors and paired task identities. Repeat 0 supplies Wilson
and exact McNemar; repeats are not independent tasks. Unknown comparison-arm costs
suppress economic ratios; zero passes and undefined bootstrap draws remain explicit.
SIMULATED inputs never enter a measured inferential table. Detailed statistics stay
in the plan and analysis contract, not in a second algorithm specified here.
