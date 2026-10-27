# Treatment equality and parser scenarios

Specification only; no task data, fixtures, native streams or admission answers.
Authority/seams: [index](README.md). Record definitions:
[harnessrun v1](harnessrun-v1.md). Sources: plan sections5–9 and section10 P5/P7.

## Treatment manifest and equality receipt

Future format `treatment/1` is a closed object with required `version`,
`experiment_kind`, `arm_id`, `fact_set_sha256`, `files`, `byte_length`,
`native_token_count?`, `tokenizer_pin?`, `equality_receipt_sha256?`,
`update_permission` (none/typed_memory_only), `discipline_sha256?`.
Files are closed `{path, sha256, access}` entries as in harnessrun.
Unknown token count/tokenizer stays null; byte equality cannot imply token equality.

Fact entries are closed `{id, type, status, provenance, date, value}` objects.
Type is decision/convention/gotcha; status is current/stale/decoy. IDs are unique;
provenance/date/value are preserved exactly across representations. No correct
patch is encoded in a fact. A future renderer may change representation/order,
never the fact IDs, values, statuses or provenance (including stale/decoy facts).

Equality receipt `treatment-equality/1` binds left/right manifest hashes,
ordered canonical fact-set hash, fact IDs, equality verdict, left/right byte
counts, relative byte difference, ballast hashes, leak-check receipt hash,
token counts/tokenizer pins (nullable with reason). Canonical fact comparison is
by ID and all six fields, after decoding the admitted representations; duplicate
IDs fail. The byte tolerance is symmetric: max(lengths)/min(lengths) <=1.10 for
the nonempty paired M1/M2 files; neutral ballast cannot add instructions or facts.
The shared fact-set hash excludes neutral ballast and representation syntax.
Hash exact bytes of the treatment files separately from fact semantics.

Task M0 has no memory file, files=[], byte_length=0, no fact-set/equality receipt,
no injected tokens and no update permission. For that arm fact_set_sha256 is null;
paired M1/M2 require a fact hash and equality receipt. Native CLAUDE.md/AGENTS.md
delivery is pinned and fixed/read-only for all scored task attempts. M2–M0
bundles information and discipline; M2–M1 is the narrower representation
comparison. Reading/adherence remains secondary; nonadherence stays in assigned
arm. No external summarizer/model call.

Decision-token leak check inspects admitted visible task/fixture material only
and emits a receipt; token must be absent outside M1/M2. This specification does
not select tokens, task answers or held-out inputs. Future canary probes are
separate non-scored manifests: three repeats/arm, require six M1/M2 successes and
three M0 absences before that harness scores. Simulated adherence/refusal precedes
separately authorized native probes. Probe success is compliance evidence only;
source lists/read events remain partial loader evidence.

Longitudinal L0 carries source only; L1 static prose; L2 starts with the same facts
and permits typed memory updates plus discipline. Archive before/after source and
memory hashes at each of twelve checkpoints. Malformed writes are archived and
recorded as nonadherence; no oracle repair/rollback or feedback. Carry only allowed
tree into a fresh process/home, no future requests/tests. L2–L1 bundles permission
and structure; it is not pure format causality. No hidden data is admitted here.

## Deferred conformance scenarios

These are written acceptance requirements for later authorized implementation,
not executable fixtures or passed tests. All synthetic outputs must remain
SIMULATED and cannot share a research table with MEASURED observations.

| Scenario | Required future observation/disposition |
| --- | --- |
| Null versus scripted | Null leaves failing artifact untouched; scripted consumes an explicit deterministic trace/patch scenario. Neither calls a native system or produces provider proof. Grades remain outside adapters. |
| Chunked stream and truncated tail | Buffer partial bytes/UTF-8 sequences until a full record; preserve locators. Missing final bytes flags parser_schema_drift and incomplete evidence; no fabricated terminal success. |
| New fields/version, malformed shape, duplicate keys | Reject closed-schema violations, retain bounded redacted evidence and stop scored work pending reconciliation; never silently discard usage. |
| Claude init/assistant/result | Keep requested flag, advertised init model and per-response assistant.message.model distinct; candidate mappings are hypotheses until pinned CLI verification. Result cost is an estimate only. Final usage reconciles with per-response usage rather than double counting. |
| Claude cache buckets | Ordinary input/read/5m-write/1h-write stay disjoint. Missing duration/rate/bucket yields unknown, never silently price at a convenient duration. |
| Codex turn completion | Parse pinned turn-completed usage, preserve requested -m and any advertised context. Provider-returned identity may stay unknown; configuration echo cannot complete it. |
| Codex input100/cached80, output100/reasoning80 | Normalize ordinary20+cached80 and output100; subset counters do not add billable usage. This arithmetic requirement is not captured native evidence. |
| Cumulative/delta/final overlap | For each scope, contribute only new deltas; reconcile final totals. Replay of the same source record adds zero cost; preserve the replay evidence. |
| Reset, out-of-order counters, hidden nested retry | Do not infer negative usage or assume completeness. Preserve records and flag unknown_usage/unobservable_retry as appropriate; stop new scored work and retain liabilities. |
| Missing price or mismatched date/model | Known counts may remain descriptive; cost unknown. No cost/pass or comparative ratio if either arm has unknown cost. |
| Model mismatch or missing response identity | Mismatch stops headline; unknown stops new scored headline work. Keep failed/successful outcomes and spend descriptive, labelled model_unverified where applicable. |
| Unexpected loader source / absent read evidence | Unexpected global memory/skill/plugin/MCP source fails admission. No listed/read source is not proof of absence; missing read evidence stays unknown. |
| Timeout/output cap/crash after dispatch | Terminal attempt retained as agent failure; all usage/cost stays included. Controller handles tree cleanup; cleanup_pending blocks scheduler. |
| Ambiguous begin or cleanup failure | No automatic replay or replacement. Preserve M9 reservation, candidate artifact and exact attempt lineage; scheduler refuses new dispatch while unresolved. |
| Grader fault versus bad candidate | Candidate error fails; trusted grader missing/tampered/self-check failure is evaluator_error. Infrastructure tree loss means missing future checkpoints, not zero rot. |
| Treatment unequal/status omitted/duplicate fact ID | Refuse before dispatch; no rewording stale/decoy status away. No post-result treatment repair. |
| SIMULATED/MEASURED merge | Reject research-table merge. Preserve mode in attempts, lineage and exports; a scripted pass cannot become a measured result. |

Static documentation inspection cannot establish any K/L acceptance above. Later
work must demonstrate actual schema roundtrips, parser goldens/replay handling,
treatment/leak checks, simulated probes, process isolation/cleanup and pinned
native streams/model/usage/billing coverage after the relevant gates. S42/M22
consumer conformance is separate; no consumer work or live calls are performed.
