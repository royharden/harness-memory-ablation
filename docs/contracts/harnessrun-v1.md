# Exported harnessrun v1

Specification only. Authority and seam owners: [contract index](README.md).
Source: frozen plan sections 3, 6, 7, 9, 10 (P2/P4/P7), 12.

## Wire rules

Future transport is UTF-8 JSONL, one complete record per line. The closure is
standalone and carries no private m11 imports. Every object is closed: only fields
listed for its record/variant are permitted. Unknown version, field, enum value,
duplicate JSON key, invalid reference or malformed line is a validation error;
retain bounded raw evidence and flag parser_schema_drift, never silently drop it.
Partial chunks are buffered until a full record exists; a truncated final record
is an error. This describes requirements, not a working JSON schema/parser.

Conventions: IDs are nonempty opaque strings, unique in their declared campaign
scope; references must resolve. SHA256 is 64 lowercase hex characters over exact
artifact bytes (directory artifacts use a frozen manifest hash). UTC times use
RFC3339; durations are finite nonnegative seconds, counts are nonnegative integers
(booleans are not counts), decimal USD values are nonnegative decimal strings.
Unknown is null with an explicit reason, never zero/empty/verified by default.
Required fields cannot be omitted; fields marked `?` below are required nullable
fields. Lists are ordered; set-like lists must contain no duplicates.

Common record fields: `schema_version` (literal `harnessrun/1`), `record_type`
(one of the ten records below). No arbitrary extension map. A later addition
requires a versioned contract. Common observed-record provenance is `evidence_ref`
(opaque redacted artifact reference), `evidence_sha256`, `source_locator` (bounded
record/byte location, not raw secret text). Evidence resolution is an exporter
responsibility; references confer neither public access nor publication rights.

## Request and launch records

| Record | Required fields beyond common fields |
| --- | --- |
| ProviderConfig | `vendor`, `endpoint_profile_id`, `requested_model_id`, `auth_reference_name?`, `billing_mode` (`api`, `none`, `subscription`) |
| AttemptSpec | `campaign_id`, `attempt_id`, `cell_id`, `parent_attempt_id?`, `retry_of?`, `experiment_kind` (`task`, `diagnostic`, `probe`, `longitudinal`, `smoke`), `mode` (`SIMULATED`, `MEASURED`), `suite_id`, `suite_sha256`, `task_id`, `task_sha256`, `treatment_id`, `treatment_manifest_sha256`, `harness_id`, `provider_config_sha256`, `model_settings_sha256`, `repeat`, `checkpoint?`, `workspace_ref`, `workspace_manifest_sha256`, `treatment_files`, `timeout_seconds`, `max_turns`, `output_cap_bytes`, `ledger_reservation_id?`, `spend_bound_sha256?`, `environment_names` |
| LaunchSpec | `launch_id`, `attempt_id`, `attempt_spec_sha256`, `argv`, `cwd`, `binary_sha256`, `image_sha256?`, `allowed_mounts`, `environment_names`, `deadline_utc`, `output_cap_bytes` |

`treatment_files` contains closed `{path, sha256, access}` entries; access is
`read_only` or `read_write`. `allowed_mounts` contains closed
`{source_ref, target_path, access}` entries with the same access enum.
`environment_names` and `argv` are arrays of strings. Environment entries are
names only, not values; auth_reference_name is a name, never credential contents.
cwd/paths are relative to admitted roots or container-absolute roots in the frozen
manifest, never arbitrary host paths. No shell interpolation in argv.

ProviderConfig bytes are separately hash-bound; requested model is exact for a
native launch, never an alias presented as proof. Null/scripted configurations
use billing_mode none and no auth reference. Subscription native dispatch and
priced subscription ingestion are disabled in MVP. Native MEASURED requires a
reservation, proven finite bound, pinned image and separately approved gates;
null fields cannot waive them. SIMULATED never becomes a paid/native launch.
timeout/max_turns/output cap are positive; checkpoint is 1..12 for longitudinal
and null otherwise. Repeat indexes are zero-based and schedule-bound, not silently
clamped to a design count. Treatment IDs must match the experiment manifest:
task M0/M1/M2; longitudinal L0/L1/L2. Other experiment arms require an explicit
frozen probe/diagnostic/smoke manifest, not a new scientific arm by inference.

HarnessPort exposes capabilities(), prepare(AttemptSpec), parse(bytes). prepare
returns data without spawning. The controller validates the resolved config,
pins, allowlists and authorization, reserves before spawn, begins exactly once,
and alone owns process-tree termination. A retry has a new attempt/launch ID and
explicit lineage, never overwrites an attempt or redispatches an ambiguous begin.
Primary outer automatic retries/replacements are prohibited. cleanup_pending
blocks scheduling. A deadline or native stop flag is not a monetary bound.

## Capability and evidence records

| Record | Required fields beyond common fields |
| --- | --- |
| CapabilityRecord | `harness_id`, `cli_version`, `binary_sha256`, `image_sha256?`, `provider_config_sha256`, `settings_sha256`, `model_evidence`, `native_memory`, `usage_buckets`, `spend_bound` |
| ModelEvidence | observed provenance, `model_evidence_id`, `attempt_id`, `response_id?`, `requested_model_id`, `advertised_model_id?`, `provider_returned_model_id?`, `evidence_kind` (`configuration_echo`, `harness_advertised`, `provider_response`, `unavailable`), `strength` (`verified`, `hypothesis`, `unsupported`), `unknown_reason?` |

Each of the four capability fields is a closed
`{status, evidence_ref?, evidence_sha256?, reason}` object; status is
verified/hypothesis/unsupported. Verified needs an evidence reference/hash tied
to the exact capability and pins; configuration echo does not verify provider
identity, native memory loading, complete usage or a spend bound. Unsupported and
hypothesis remain visible, not coerced to true. Missing image evidence means
native admission is unavailable, not local-host permission.

Each relevant response needs its own identity evidence, including nested calls.
No response ID is acceptable only for non-response observations; unavailable
response identity carries its locator and reason. Requested, advertised and
provider-returned IDs remain distinct. Only exact requested=provider-returned on
every relevant response with complete response coverage permits model-held-fixed
inference. An advertised echo alone never does. Mismatch stops the headline;
unknown stops new scored headline work, retaining descriptive outcomes and spend
as model_unverified. No rescue relabelling of primary results. Matching IDs do not
prove identical hidden system settings; Claude versus Codex is a system comparison.

## Parsed records and accounting observations

| Record | Required fields beyond common fields |
| --- | --- |
| HarnessEvent | observed provenance, `event_id`, `attempt_id`, `sequence`, `kind`, `payload` |
| UsageObservation | observed provenance, `observation_id`, `attempt_id`, `scope_id`, `counter_basis` (`incremental`, `cumulative`, `final`), `usage_source` (literal `harness_reported`), `coverage` (`complete`, `partial`, `unknown`), `unknown_reason?`, `buckets`, `input_total?`, `cached_input_subset?`, `reasoning_output_subset?`, `harness_estimate_usd?`, `pricetable_sha256?` |

HarnessEvent payload is a closed tagged union: `started` has `{launch_id}`;
`response` has `{response_id}`; `memory_source` has `{source_ref, source_sha256?,
observation}` where observation is listed/read/unexpected; `stop` has `{reason}`
using terminal attempt statuses below; `parser_error` has `{code, detail_ref}`
where code is parser_schema_drift. Sequence is ordered per attempt; event IDs
deduplicate replay. Memory source observations are partial loader evidence;
absence of a read event does not establish non-reading or absence of context.
Tool/output content stays in bounded redacted capture artifacts, not open payloads.

UsageObservation references its original raw stream record through observed
provenance (`evidence_ref`, `evidence_sha256`, `source_locator`), not a HarnessEvent
ID. For usage, source_locator is a half-open byte range `bytes:start:end` in the
hash-bound capture, with decimal nonnegative start < end. The exporter must
resolve that capture/range; unresolved provenance is invalid. The same rule
applies to incremental, cumulative and final observations, whether or not that
raw record also yields a response/stop event. Raw record identity for replay is
the tuple (attempt_id, evidence_sha256, source_locator); observation_id identifies
the parsed observation. Re-encoding the same raw record under another observation
ID cannot add usage. Cross-capture replay needs pinned provider IDs/scope evidence;
if unavailable it is ambiguous coverage, not an assumed fresh billable increment.

Buckets is closed with required nullable counters: `ordinary_input`,
`cached_input`, `cache_write_5m`, `cache_write_1h`, `output`. These are disjoint
billable buckets, not overlapping totals. Unknown/not-applicable reason belongs
in unknown_reason; known not-applicable buckets are zero only when supported by
the pinned format. input_total and subset fields are metadata, never additional
billable buckets. Codex input100/cached80 means ordinary20+cached80; output100
with reasoning80 means output100, not180. Claude ordinary/read/5m-write/1h-write
remain disjoint; ambiguous undifferentiated cache-write duration stays unknown.

Counter normalization is per attempt/scope, never across cells. Record IDs plus
source locators identify duplicate replay; cumulative counters contribute deltas
only, and a final total reconciles rather than adds to already counted usage.
Counter resets, incompatible overlapping sources, missing fields, hidden retries
or ambiguous scopes make coverage incomplete/unknown, never negative deltas or
text-length estimates. Preserve all raw observations and provenance even when
their billable contribution is zero due to replay. Complete means every billable
response/nested call is accounted for, not merely that a terminal line appeared.

Price calculation requires a dated immutable pricetable/1 hash with matching
model/date/buckets. Gaps produce unknown, not free usage. harness_estimate_usd
(including Claude total_cost_usd) is a cross-check only. Unknown cost in either
arm suppresses cost/pass and ratios; no successful-outcomes-only cost sums.

## Attempt result, grade and limitations

| Record | Required fields beyond common fields |
| --- | --- |
| AttemptRecord | `campaign_id`, `attempt_id`, `cell_id`, `launch_id?`, `parent_attempt_id?`, `retry_of?`, `mode`, `attempt_spec_sha256`, `launch_spec_sha256?`, `created_at`, `started_at?`, `ended_at?`, `status`, `exit_code?`, `process_state` (`not_started`, `running`, `exited`, `cleanup_pending`), `artifact_sha256?`, `transcript_ref?`, `transcript_sha256?`, `usage_observation_ids`, `usage_coverage` (`complete`, `partial`, `unknown`), `model_evidence_ids`, `model_coverage` (`complete`, `partial`, `unknown`), `billing_provenance_hashes`, `ledger_run_id?`, `ledger_reservation_id?`, `wall_seconds?`, `harness_estimate_usd?`, `limitation_codes` |
| GradeResult | `attempt_id`, `artifact_sha256`, `opaque_task_id`, `verdict` (`pass`, `fail`, `evaluator_error`), `grader_sha256`, `receipt_ref`, `receipt_sha256` |
| Limitation | `attempt_id`, `code`, `raw_code`, `evidence_ref`, `evidence_sha256`, `disposition` (`stop`, `retain_descriptive`, `missing`, `secondary`) |

`model_evidence_ids` references ModelEvidence.model_evidence_id;
all record references resolve their named IDs. AttemptRecord is the result
snapshot, not a second Result record. Status is one of pending, running, finished,
timeout, spend_cap, output_cap, crash, refused, cleanup_pending. Pending/running
are nonterminal; terminal records have ended_at. A refused pre-launch record has
null launch/start/exit/artifact fields and a limitation identifying why. Lost
artifacts remain null and visible as missing. Finished describes process end,
never grader pass. cleanup_pending overrides an otherwise terminal process
outcome until cleanup is resolved, with prior outcome retained by stop events.
Every planned cell remains visible even when no attempt starts.

GraderPort.grade(immutable_artifact, opaque_task_id) is separate from adapters.
Candidate syntax/import/runtime error, invalid patch, crash or dispatched cap stop
is failure; trusted-grader self-check/tamper/missing grader or infrastructure loss
is evaluator_error/missing. infra_excluded needs evidence of zero tool calls and
no file change. All executed attempt costs stay included, including failures.
Public exports carry opaque references/receipts, never hidden tests/answers.

Limitation.code is closed to the plan section12 union: unknown_usage,
unobservable_retry, budget_bound_unproven, undefined_cost_ratio,
model_substitution, model_unverified, parser_schema_drift, global_context_leak,
treatment_not_loaded, stale_memory_followed, decoy_followed, memory_write_invalid,
grader_flake, evaluator_error, oracle_circularity, heldout_exposure, timeout,
spend_cap_stop, agent_error, infra_excluded, cleanup_pending, workspace_lost,
trajectory_divergence, claim_deleted, metric_unavailable, ceiling, floor.
Preserve raw_code, normalizing only unverified_model to model_unverified,
treatment_not_read to treatment_not_loaded, and metric_parse_failure to
metric_unavailable. Unknown codes require a schema revision, not silent success.
Disposition must follow the plan's actual gate; it cannot soften a required stop.

LedgerPort.reserve/begin/settle/snapshot/export returns actual M9 IDs. Metadata
binds one M9 run to each CLI launch. M9 remains the sole monetary authority;
unknown charges hold the full reservation through campaign close, estimates
never free headroom, known overbound charges are recorded and halt. Billing
exports reconcile tranche scope without inventing per-arm bills or duplicate
fees. No native dispatch is authorized by this specification; the cumulative
USD40 ceiling includes all tranches/systems and paid outside costs.
