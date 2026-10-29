# Non-operational activation template

Round2 source construction; independence PENDING - Roy, runtime-unverified.
No runtime, import, test, network/model call, account or credential use has occurred.
INT's construction disposition remains distinct from independence and runtime
evidence; this template supplies no P0, independent, product, scientific or
execution acceptance.

`config/activation.example.json` is closed non-secret metadata. It has no secret
value field: `credential_environment_name` contains only `M11_PROVIDER_API_KEY`.
Required placeholders in the example:

- `<PLACEHOLDER_MODEL_PIN>`: a future exact model ID with authentic version/model evidence.
- `<PLACEHOLDER_ACCOUNT_ID>`: Roy's authorized existing account identifier and approval.
- `<PLACEHOLDER_ENDPOINT_PROFILE_ID>`: approved, pinned provider endpoint-profile identifier.

Credential value illustration belongs only in this handoff documentation:

    M11_PROVIDER_API_KEY = <PLACEHOLDER_API_KEY>

This is a non-operational named marker, never a real/invented key and not an .env
file. The next authorized non-Dirty integrator supplies the actual value through
the separately approved runtime environment. Do not put that value or its marker
in activation JSON, public records, argv, captures, executable source or reports.
An actual key must never be committed, including in documentation.
No credential files are requested or read, and source performs no environment lookup.

Future CLI entrypoint: `m11 configuration check config/activation.example.json`.
It accepts only explicitly named activation JSON templates, bounded64KiB, rejects
unknown fields/duplicate keys/nonfinite data and returns a refusal with sanitized
placeholder names/field locations. Exit3 is intentional even for filled fields:
template inspection never grants activation. Do not run it in this source-only
phase. Static source/AST/JSON inspection is the current check boundary.

Native adapter prepare/planned-launch guards reject explicit named placeholders,
including embedded, differently cased or bracket-stripped markers. Permit/policy/
capability bindings and provided runtime environment also have that guard. It is
a marker detector, not evidence that arbitrary non-placeholder strings are real
accounts/models/keys or that all secrets can be identified. Missing authentic
RuntimeVerifier, namespace, M9 journal and P0/activation still refuse by default.
No new config framework, provider record extension or permit issuer is introduced.

Future focused refusal checklist (not executed): named markers in model/account/
endpoint/credential-reference/context/permit/argv/environment refuse; unknown secret
value/verified/hash fields reject; true or numeric operational flags reject;
duplicate keys, missing slots and oversized JSON reject without echoing values;
filled metadata still cannot authorize or dispatch; existing native/CLI gates remain.

Spend reported: USD0. USD40 is the hard cumulative testing ceiling, not current
spend or account/key approval. No signup/credits/installs/runtime is granted for
M11. Future activation still needs independent P0, actual approved receipts and
keys/accounts, freeRAM>3GB recorded plus Roy notification before runtime/container
steps, and authentic money/namespace/cleanup authorities. Protected databases are
untouched. No resource watcher or builder-lineage stand-in is appointed.
