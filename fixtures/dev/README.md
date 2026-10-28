# Builder-owned development task source

18 original synthetic development families: six memory-independent, six decision-dependent,
six misleading-memory. Authored after the scoped source-construction adoption by
0985_Codex_gpt-61-sol_Sub_M11DevTasks. This is private-only builder lineage,
not P0, independent, diagnostic or held-out material. Rights and semantic review are PENDING.
All task, oracle, wrong-variant and checker source remains NOT_RUN.

`manifest.json` is the inventory seam. Each task has two candidate modules, minimal public
unittest source and separate hidden checker source (four modules in the development
microrepository, excluding the alternative replacement trees). Expected behavior is
builder-authored, never independent. Each of the correct and three deliberately incorrect
variants is a full replacement pair of `core.py` and `helpers.py`, not a brittle textual diff.
Nothing here proves that a checker, oracle or wrong tree works; no such source was run.

Candidate visibility is an allowlist: mount only `visible_paths`; copy `fixture/` contents
to the candidate module root. Do not mount task metadata, authoring/, hidden/, oracle/,
wrong/ or canonical fact inventory. A future isolated trusted grader sets the candidate
module root on its import path and loads hidden checker source by file. Inventory tooling
must never import the candidate. Grader integrity, self-checks, error classification,
process isolation and independent data admission remain separate obligations.

`memory/facts.json` is trusted authoring input. M1 prose and M2 JSON repeat the six fact
fields and content. Neutral whitespace keeps UTF-8 byte lengths within the plan tolerance; exact bytes depend on checkout line endings. Native token counts,
native loading and semantic equality have NOT been verified. Treatment preparation alone
selects M1 or M2 and supplies the future native memory file; M0 supplies neither file.
No memory is part of `visible_paths` before treatment preparation.

Each decision-dependent task withholds exactly one synthetic project choice from visible
specification, fixture and public examples; this artificial information intervention is
explicitly disclosed. Stale and decoy facts have matching status/provenance in both formats;
current misleading-task specifications are sufficient to refute them. Memory-independent
tasks are fully specified and have irrelevant housekeeping facts.

`authoring/` retains tool-aided source construction scripts as private provenance, excluded
from candidate/trusted grading inventories. These scripts only construct source strings and
metadata; construction did not import or execute any task, patch or checker. They are not
part of the wheel or a proposed future execution path. Do not run them as an admission check.

A future independent custodian must supply and review disjoint families; these names do
not prove cross-split disjointness. No independent answer, gate receipt, signature, runtime
result, licence approval or public-release authority is supplied by this inventory.
