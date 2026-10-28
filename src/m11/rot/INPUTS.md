# Rot metric inputs

These pure functions accept observations and source text only. They neither run
candidate code nor establish grading/admission provenance. Caller code binds
observations and reference results to the frozen seed, arm, checkpoint, artifact
hash and deterministic grader records. Outputs are runtime-unverified source.

`analyze_python(source: str, *, reference: dict | None = None)` returns `clones`
and `complexity`, each carrying its frozen definition and unavailable reason.
An optional reference is the same-shaped result for the same checkpoint;
`reference_excess` subtracts its fraction or aggregate fields. Without a
reference, excess is unavailable. Syntax errors make both metrics unavailable.
Empty significant function tokens make clone fraction unavailable; no functions
make complexity unavailable, with observed count/sum still zero.

Clone token normalization retains token type and exact spelling except nonkeyword
names become ID. Body positions start at the first body AST node, ending at the
last node's end; lambda bodies use their expression span. Nested body tokens
belong to the innermost scope; class body tokens are excluded unless owned by a
contained function/lambda. A nested definition header can belong to its enclosing
body, while the nested body never does. All owned tokens count in the denominator,
including bodies shorter than 30 tokens; matches require different body IDs.
Participating token start positions are unioned across all windows. Complexity
traverses body nodes only, stops at nested scopes, and counts each child
function/lambda separately. Length is def/expression start through end lines,
subtracting the complete line ranges of nearest nested scopes, including lambdas;
a shared line is subtracted once. No class is a function.

`tripwire_area(checkpoints)` accepts a list/tuple of zero through twelve mappings:

* `checkpoint`: unique integer 1 through 12 (booleans rejected).
* `tripwires`: mapping of exactly four nonempty, stable baseline IDs to states.
* `feature_tests`: optional mapping of feature IDs to states.

States are `pass`, `fail`, `unknown`, `generated_code_error` (failure), or
`infrastructure_loss` (unknown). Missing checkpoints contain four unknown cells.
Missing individual baseline entries are malformed, rather than inferred. Baseline
area always divides by 48 and returns failure numerator, unknown count, lower/
upper bounds, and unavailable point value when unknown cells exist. Excess uses
the prescribed zero reference. `first_observed_failure` is evidence only;
`first_failure_exact` discloses earlier unknown checkpoints. Final failure and
unknown counts are separate.

Feature completion reports only the explicitly observed feature inventory and
does not infer a scheduled feature denominator. Empty inventory discloses that
limitation. Established-regression area activates each feature on its first
observed pass and counts only checkpoints strictly after activation; absent
observations then count unknown. It exposes activation checkpoints and its own
arm-dependent denominator. It never contributes to baseline rot.

`claim_drift(claims)` requires a mapping with exactly two keys:

* `registered`: list of exactly four mappings, each with `claim_id` (unique
  nonempty string), `anchor_present` (bool or null), `present` (bool or null),
  and `outcome` (`pass`, `fail`, `unknown`).
* `unregistered`: list of unique nonempty addition IDs, disjoint from registered
  IDs. These additions are listed and never scored.

`present=false` records observed deletion; `anchor_present=false` records an
observed missing anchor. Either counts as failure regardless of unknown fields;
an observed failing test also establishes failure. Otherwise any unknown presence,
anchor or test observation suppresses the point estimate and exposes bounds with
denominator four. Null never means deleted or missing anchor. The
caller supplies deterministic test outcomes; no text/model judgment is used.
Unexpected fields, duplicate IDs, invalid state values and malformed types raise
TypeError/ValueError rather than becoming numeric zero.

This normalized input is the exact export/2 PublicClaim adapter shape; no source
path or invented anchor string is needed. Older source_anchor inputs are not an
alternate accepted shape. The frozen claim-drift/1 arithmetic is unchanged.
