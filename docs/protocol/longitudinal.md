# Longitudinal state transitions

Authority: PLAN-M11-v1 sections 5–6, 8–10 (P12), 12.
See [schedule](preregistration-schedule.md) and [money](authorization-money.md).
Format-only; no seed, reference, checkpoint or grader data is authored here.

## Trajectory identity and carry

A trajectory binds registration/campaign, seed ID/hash, system/exact model, arm,
ordered 12 checkpoint IDs and immutable initial source/treatment hashes. Claude
held-out is four seeds × three arms × twelve sessions (144); full dev calibration
is two seeds × three arms × twelve (72), separate from held-out. One trajectory
per seed/arm; no Codex longitudinal MVP or run-variance estimate.

L0 carries source only; L1 static prose; L2 same initial facts plus typed-memory
read/update discipline. L2 update usage belongs to that session. L2−L1 bundles
structure and updating permission, so it is not pure format causality.
Carry only the allowed produced source/treatment tree into a fresh process/home;
no previous session store, external/global memory, future requests/tests, oracle
repair or hidden feedback. Visible accrued tests are identical across arms.

Each checkpoint records planned ID/ordinal, previous produced-tree reference,
before/after source and memory hashes (explicit absence for source-only treatment),
workspace/artifact reference, attempt/launch/M9 IDs, capability/config/model pins,
controller status, usage/coverage and grading receipt reference. Preserve malformed
memory and its hash as nonadherence; never silently normalize it. Hidden grading
results are stored outside subsequent agent context. Reference artifacts remain in
trusted grader custody and never become carried source.

## Transition table

| From/event | Durable disposition | Next action |
|---|---|---|
| Planned + all dispatch gates pass | Freeze before-hashes and identity; reserve/begin via shared controller/ledger | Launch one fresh process/home |
| Session ends with recoverable produced tree | Archive after-hashes/artifact and outcome, including candidate errors or invalid memory | Grade separately; carry produced tree to next prescribed session |
| Candidate code prevents execution | Observed tripwire failure, not unknown infrastructure outcome | Continue prescribed sessions without repair/rollback |
| Scored failure, timeout or cap stop | Keep all usage/cost, produced tree and attempt status | Continue if tree exists and safety/authorization gates permit |
| Cleanup ambiguous or process remains | cleanup_pending; preserve holds and artifacts | Block scheduler until explicitly resolved; no ambiguous replay |
| Trusted-grader fault/missing/tampered grader | evaluator_error/missing checkpoint observation | Stop new work on evaluator gate; preserve tree; only resume after resolution without fabricated results |
| Infrastructure tree lost | workspace_lost/trajectory_divergence, unknown unrecoverable checkpoints | End trajectory; remaining checkpoints unknown, never zeros or replacement trees |
| Safety, custody, identity or monetary gate fails | Stopped with explicit reason and all planned remainder retained | Halt new dispatch; no automatic repair/retry or early-success stopping |
| Twelve prescribed sessions represented | Preserve complete/missing coverage plus all artifacts | Report trajectory; no automatic measured/complete acceptance |

For every continued session, checkpoint input must match the previous produced
tree's digest. A disagreement is divergence requiring explicit disposition, not
permission to restore reference code. A safety pause does not erase planned slots.
The continuation rule for scored agent failure never overrides section 12 stop gates.

## Grader and report handoff

Trusted grading returns pass/fail/evaluator_error against the immutable artifact,
opaque seed/checkpoint and accrued feature/tripwire/claim mapping. It does not give
the scheduler hidden content to pass to later agents. Grader/code separation and
independent expectations require external admission; builders cannot certify them.

For each seed/arm, four baseline tripwires remain valid for twelve checkpoints.
Report raw failures/48 and unknown cells separately, with lower bound treating
unknown cells as zero and upper bound treating them as one. Persistent failure
counts at each checkpoint; recovery stops counting. Candidate-caused execution
failure counts as failure; missing infrastructure artifact is unknown. Reference
R is zero and excess is shown separately. Never reduce denominator to observed cells.

Also hand off new-feature completion, first/final tripwire failure,
established-regression area, clone/complexity excess, four registered README claims,
memory bytes/tokens, usage/cost coverage and divergence. Established-regression tests
join only after first pass; its arm-dependent denominator makes it secondary.
Deleted/false/missing-anchor registered claims count against the fixed four;
unregistered additions remain unscored. Syntax errors leave clone/complexity
unavailable, not zero. Algorithms remain `clones/1` and `complexity/1` from section 8.

Show all seed trajectories and paired L2−L0/L1−L0 signs descriptively, without pooled
session p-values or a general confidence claim from four seeds. Low R with zero
feature completion is not successful development. SIMULATED and MEASURED tables
remain separate, and source-only review proves none of these runtime behaviors.
