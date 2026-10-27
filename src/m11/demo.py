"""Builder-authored offline demonstration; no grader, model, process or file effects."""

from harnessrun import AttemptSpec, ContractError, ProviderConfig, canonical_json, sha256_bytes

from .adapters.base import PreparationContext
from .adapters.null import NullAdapter
from .adapters.scripted import ScriptedAdapter, ScriptedPatch, ScriptedScenario


def build_demo() -> dict:
    before = "answer = 0\n"
    target = "answer = 1\n"
    settings_hash = sha256_bytes(canonical_json({"kind": "synthetic-control"}))
    provider = ProviderConfig(vendor="synthetic", endpoint_profile_id="offline",
        requested_model_id="synthetic-no-model", auth_reference_name=None, billing_mode="none")
    scenario = ScriptedScenario(scenario_id="builder-demo-1", patches=(ScriptedPatch(
        path="example.py", expected_before_sha256=sha256_bytes(before.encode()),
        replacement_utf8=target),), trace_jsonl=b"")
    rows = []
    for harness, adapter_class in (("null", NullAdapter), ("scripted", ScriptedAdapter)):
        context = PreparationContext(launch_id=f"demo-{harness}-launch", provider=provider,
            cli_version="SIMULATED", binary_sha256=sha256_bytes(b"synthetic-not-a-binary"),
            image_sha256=None, cwd="/workspace", allowed_mounts=(),
            deadline_utc="2100-01-01T00:00:00Z", executable="synthetic-no-executable")
        spec = AttemptSpec(campaign_id="builder-offline-demo", attempt_id=f"demo-{harness}",
            cell_id=f"demo-{harness}-cell", parent_attempt_id=None, retry_of=None,
            experiment_kind="task", mode="SIMULATED", suite_id="builder-demo",
            suite_sha256=sha256_bytes(before.encode()), task_id="synthetic-example",
            task_sha256=sha256_bytes(before.encode()), treatment_id="M0",
            treatment_manifest_sha256=sha256_bytes(canonical_json({"arm": "M0", "files": []})),
            harness_id=harness, provider_config_sha256=sha256_bytes(canonical_json(provider)),
            model_settings_sha256=settings_hash, repeat=0, checkpoint=None,
            workspace_ref="synthetic:memory-only", workspace_manifest_sha256=sha256_bytes(before.encode()),
            treatment_files=(), timeout_seconds=60.0, max_turns=1, output_cap_bytes=1024,
            ledger_reservation_id=None, spend_bound_sha256=None, environment_names=())
        adapter = (adapter_class(context, settings_hash, scenario) if harness == "scripted"
                   else adapter_class(context, settings_hash))
        launch = adapter.prepare(spec)  # Data only: never dispatched.
        artifact = {"example.py": before}
        for patch in adapter.planned_patches(spec):
            if patch.path not in artifact or sha256_bytes(artifact[patch.path].encode()) != patch.expected_before_sha256:
                raise ContractError("synthetic patch before hash mismatch")
            artifact[patch.path] = patch.replacement_utf8
        rows.append({"harness_id": harness, "mode": "SIMULATED",
            "outcome": "pass" if artifact["example.py"] == target else "fail",
            "artifact_sha256": sha256_bytes(artifact["example.py"].encode()),
            "launch_data_sha256": sha256_bytes(canonical_json(launch)), "dispatched": False})
    return {"schema_version": "m11-demo/1", "mode": "SIMULATED",
        "authorship": "builder-authored synthetic; not independent admission evidence",
        "status": "runtime-unverified source construction",
        "grading": "local text comparison only; not a trusted GraderPort receipt",
        "independent_admission": False, "measured_result": False,
        "external_spend_usd": "0", "rows": rows}
