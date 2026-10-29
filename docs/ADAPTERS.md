# Adapter source boundary

Construction source only; no adapter, parser, model, process or usage behavior has
been executed. Native mappings are hypotheses pending exact CLI/image verification.
P0, runtime activation and all independent-data gates remain pending. Source-only
construction does not permit dispatch or spend.

`m11.adapters` exports `PreparationContext`, `NullAdapter`, `ScriptedAdapter`,
`ScriptedScenario`, `ScriptedPatch`, `ClaudeAdapter`, `ClaudeParser`, `CodexAdapter`,
`CodexParser`, `UsageNormalizer`, `UsageContribution`, and
`NativePreparationRefused` (a `ContractError`). Shared wire records come only from
the standalone `harnessrun` closure.

All adapters accept `(context, settings_sha256)`; scripted additionally requires
an explicit `ScriptedScenario`. Native adapters optionally accept a prebound parser
as their third argument; their `parse` delegates to it or refuses without it.
Context is closed frozen preparation data containing
the resolved provider configuration, launch ID, CLI version, binary/image pins,
executable, cwd, typed mount list and deadline. It contains no environment values.
These supplied pins are claims for later controller verification, not observations.
Missing genuine pins cannot be repaired with fabricated hashes. Capability records
never default to verified. The wire format requires binary/version pins; when these
are unavailable, callers must report capability unavailable rather than construct
a counterfeit capability record.

`capabilities()` returns a shared record. Null/scripted capabilities are unsupported
for native claims; native model/memory/usage are hypotheses and finite spend bound
is unsupported. `prepare(spec)` produces data without spawning. Null/scripted
require SIMULATED, billing none, no auth reference and exact provider/settings pins.
Their launch argv begins with an internal `m11-simulated-*` marker for in-process
controller interpretation, not an executable command to spawn. Null returns no
patches. Scripted returns deterministic, hash-guarded replacement data from
`planned_patches(spec)`. Neither writes files, calls a model or grades a candidate.
The controller must check containment, current candidate hash and allowed write
scope before applying a scripted replacement.

Every scripted scenario retains `SIMULATED` and
`builder-authored synthetic; not independent admission evidence`. Its closed patch
records bind a canonical relative POSIX path, exact before hash and replacement
UTF-8 text. Its trace must use the matching attempt ID. Synthetic model evidence
cannot claim native verification. No builder-authored trace is a P0/held-out answer
or independent metric worksheet.

Claude/Codex `prepare` defaults to `NativePreparationRefused`. Optional typed
`PreparationAuthorization` is reserved for a future trusted controller: exact
verified capability pins/receipt scope, task delivery, isolation policy and
authenticated runtime permit must pass its external verifier before prepare can
return launch data. The only provided verifier is unavailable and always refuses;
source cannot issue permits or authenticate independent evidence. Inspection-only
`planned_launch(spec)` returns a candidate argv with an exact requested model.
Neither path spawns. Hashes, booleans or supplied capability labels alone cannot
grant eligibility through the default boundary.

Task input is explicit bounded hash-bound UTF8 stdin, separate from LaunchSpec;
Claude's candidate text input mode and Codex's `-` operand require exact-version
verification in the future task-delivery receipt. Input text is never in argv.
Isolated image/config/home, allowed paths/mounts, admission, model/loader/usage
proof, monetary reservations, finite liability and signed live activation remain
controller gates. No native CLI fallback or subprocess exists in the adapter
package. Subscription/priced subscription ingestion remains disabled.

Native parser constructors require keyword arguments `attempt_id`,
`requested_model_id`, `evidence_ref`, `capture` (frozen exact bytes), and optional
`max_record_bytes`. Feed exact ordered chunks through `parse(bytes)`, which
returns a tuple of shared observations/events, then call `finalize()`. A complete
record requires its newline. The parser checks every supplied chunk against the
capture and binds each observation to the full capture SHA256 and half-open raw
`bytes:start:end` range. A partial UTF-8 sequence waits for a complete record;
truncated tails, malformed JSON, duplicate keys and unknown mapped fields/types
yield parser-schema-drift plus unknown usage. Oversized buffering or mismatched
capture input raises a refusal. Capture storage/redaction/access is a separate
controller/exporter responsibility; parsing never copies raw output into wire
payloads. No source-list absence is interpreted as proof of non-reading.

The Claude hypothesis maps system-init advertised model separately from
assistant-message model/response identity. Assistant usage is incremental;
result usage is final reconciliation. Cache input/read/write remain disjoint.
Only explicit 5m/1h split counters populate write buckets; undifferentiated write
duration remains unknown. `total_cost_usd` is only an estimate, never a price row
or M9 charge. Codex turn-completed usage subtracts cached subset from input and
keeps reasoning as a subset of output. Missing subsets stay unknown. Codex item
IDs are not promoted to provider response IDs. No terminal line establishes
complete response/nested-call coverage; native usage stays partial.

`UsageNormalizer.add(observation)` returns a contribution retaining the original
observation, nullable bucket deltas, coverage, reasons and replay flag.
`observations` and `contributions` retain every call. Scope totals are separate per
attempt; cumulative/final counters reconcile prior counts instead of adding them
again. Exact raw-provenance replays contribute zero even with a different parsed
observation ID. Conflicting raw interpretations, reused IDs, resets, unknown
earlier counters, incremental records after final and ambiguous cross-capture
freshness remain unknown. A caller must establish that supplied scope IDs are
disjoint; the normalizer cannot infer provider identity or hidden retries.
`totals(attempt_id)` returns nullable counters; no observations returns unknown,
not zero. No prices, incurred charges, monetary headroom or scientific eligibility
are computed here. Missing price/model/coverage evidence cannot become free use.

Deferred execution: closed-schema conformance, chunk/replay/counter goldens,
scripted controller application, native streams/version argv, full loader/model/
nested-call coverage and all billing/isolation/activation checks. These require
the later authorized validation phase and do not follow from source inspection.
