# Canonical CLI source seam

Construction source, runtime-unverified; no imports, instrument run, independent
admission, inference or public release is established by this reconciliation.

DL3 owns `m11.campaign.PublicExport` and
`parse_export(str | bytes | dict) -> PublicExport`. Read-only source pin:
`e7e6e8a29b775715dbdd9d18abc8c0e30a7386af`, campaign.py and SOURCE-API.md.
This declaration is provisional until its producer's focused corrections are
reviewed and integrated. DL1 does not vendor a competing producer or merge that
unreviewed commit. Existing harnessrun records remain the separate ten-record
closure; no campaign fields are added to them.

CLI analyze/report read a bounded explicit public JSON object with duplicate-key
rejection, call the canonical parser, require its PublicExport return type, then
pass `model_dump(mode="json")` to DL4's `analyze_export(payload) -> dict`. DL4 owns
the corresponding parse_export intake, calculations and unavailable reasons.
CLI report sends that analysis result to exactly render_html/render_markdown/
render_json, never the raw export or an alternate shape. Strict Python tuple
fields are handled by the canonical JSON-aware parser, not by coercive local DTOs
or direct strict model_validate of a JSON-decoded dict.

The canonical nested registration/suite/ResultEligibility and required arrays are
retained without filtering or population changes. Withheld, embargoed and
simulated_descriptive release states plus literal-false inferential/public-release
flags remain producer/analysis gates. Caller-asserted PASS or unavailable evidence
cannot be repaired by the CLI. Absent modules/dependencies or contract errors
return an explicit refusal. The existing SIMULATED builder demo stays a separate
m11-demo/1 text-comparison output; it cannot substitute for m11-export/1.

Helper seam: harnessrun.canonical_json returns UTF8 bytes; the pinned DL3 helper
of the same spelling returns UTF8-compatible text. Sorting, compact separators,
ensure_ascii=False and nonfinite rejection agree, but return types differ. DL3
owns any explicit text adapter/deduplication for metadata consumers; DL1 supplies
canonical_json, sha256_bytes and sha256_json, with no fallback helper aliases.

Known integration boundary: earlier integrated DL4 source uses direct
PublicExport.model_validate(payload), which fails strict Python tuple handling
for JSON-mode lists. Its explicit r2 task replaces that intake with parse_export;
CLI does not weaken either schema to hide the pending consumer reconciliation.
Native dispatch and all execution commands retain current P0/runtime refusal.
