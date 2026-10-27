"""Fail-closed authorization records; source approval is not execution approval."""

from __future__ import annotations

from typing import Literal, Self

from pydantic import model_validator

from .accounting import LedgerPort, load_ledger
from .campaign import (
    ClosedModel,
    Digest,
    Identifier,
    Registration,
    ScheduleManifest,
    SuiteManifest,
    sha256_json,
)


class AuthorityEvidence(ClosedModel):
    """References to external evidence, never credentials or self-issued proof."""

    schema_version: Literal["m11-authority/1"] = "m11-authority/1"
    p0_receipt_sha256: Digest | None = None
    full_pack_receipt_sha256: Digest | None = None
    human_rights_review_sha256: Digest | None = None
    activation_sha256: Digest | None = None
    account_terms_approval_sha256: Digest | None = None
    finite_liability_proof_sha256: Digest | None = None
    external_hard_limit_sha256: Digest | None = None
    calibrated_complete_stage_bound_sha256: Digest | None = None
    model_response_coverage_sha256: Digest | None = None
    isolation_probe_sha256: Digest | None = None
    custody_no_exposure_sha256: Digest | None = None
    usage_retry_coverage_sha256: Digest | None = None
    cleanup_receipt_sha256: Digest | None = None


class AuthorizationDecision(ClosedModel):
    schema_version: Literal["m11-authorization/1"] = "m11-authorization/1"
    eligible: Literal[False] = False
    campaign_id: Identifier
    registration_sha256: Digest
    suite_sha256: Digest
    reasons: tuple[Identifier, ...]
    evidence_sha256: Digest
    ceiling_usd: Literal["40"] = "40"
    authorized_spend_usd: Literal["0"] = "0"
    ledger_available: bool
    disposition: Literal["refused_runtime_unverified"] = "refused_runtime_unverified"

    @model_validator(mode="after")
    def explicit_refusal(self) -> Self:
        if not self.reasons:
            raise ValueError("refusal must retain its reasons")
        return self


def check_authorization(
    registration: Registration,
    suite: SuiteManifest,
    *,
    schedule: ScheduleManifest | None = None,
    evidence: AuthorityEvidence | None = None,
    ledger: LedgerPort | None = None,
) -> AuthorizationDecision:
    """Describe every missing boundary; no caller flag can activate current source.

    Hashes establish reference integrity, not authenticity/rights or independent
    admission. Later approved runtime activation needs a separately reviewed gate.
    Even SIMULATED instrument execution remains blocked until P0 clears.
    """
    evidence = evidence or AuthorityEvidence()
    reasons = ["runtime_not_authorized", "independent_p0_not_executed", "spend_authorized_zero"]
    suite_hash = sha256_json(suite)
    if registration.suite_sha256 != suite_hash:
        reasons.append("suite_digest_mismatch")
    if registration.schedule_sha256 is None:
        reasons.append("registration_not_frozen")
    if schedule is None:
        reasons.append("schedule_missing")
    elif (
        schedule.registration_id != registration.registration_id
        or schedule.campaign_id != registration.campaign_id
        or schedule.suite_sha256 != suite_hash
        or sha256_json(schedule) != registration.schedule_sha256
    ):
        reasons.append("schedule_digest_or_identity_mismatch")
    for ref in suite.admission_refs:
        if ref.status == "NO-GO":
            reasons.append("p0_no_go_m11_skipped" if ref.gate_kind == "P0" else "full_pack_no_go_execution_skipped")
    for kind in ("P0", "full_pack"):
        # P0 is always required. Held-out gates apply to held-out execution only.
        if kind == "full_pack" and registration.stage not in ("C", "D1", "E"):
            continue
        if not any(r.gate_kind == kind and r.status == "PASS" for r in suite.admission_refs):
            reasons.append(f"{kind}_scoped_receipt_missing")
    for field in (
        "p0_receipt_sha256", "human_rights_review_sha256", "activation_sha256",
        "account_terms_approval_sha256", "finite_liability_proof_sha256",
        "custody_no_exposure_sha256", "usage_retry_coverage_sha256", "cleanup_receipt_sha256",
    ):
        if getattr(evidence, field) is None:
            reasons.append(f"missing_{field}")
    if registration.stage in ("A", "E") and evidence.external_hard_limit_sha256 is None:
        reasons.append("external_hard_limit_required_before_first_probe")
    if registration.stage in ("C", "D1", "E"):
        if evidence.full_pack_receipt_sha256 is None:
            reasons.append("missing_full_pack_receipt_sha256")
        if evidence.calibrated_complete_stage_bound_sha256 is None:
            reasons.append("complete_stage_affordability_unproven")
    if registration.mode == "MEASURED":
        if registration.requested_model_id is None or evidence.model_response_coverage_sha256 is None:
            reasons.append("model_identity_unverified")
        if evidence.isolation_probe_sha256 is None:
            reasons.append("isolation_and_delivery_unverified")
        if registration.launch_bound_usd is None:
            reasons.append("budget_bound_unproven")
        required_pin_roles = {"code", "image", "cli", "config", "provider", "model", "price", "analysis", "billing_bound", "authorization"}
        if not required_pin_roles <= {pin.role for pin in registration.pins}:
            reasons.append("required_frozen_pins_missing")
    availability = (ledger or load_ledger()).availability()
    if not availability.available:
        reasons.append(availability.reason)
    # No monetary arithmetic here: only exact M9 may project cumulative incurred
    # cost plus remaining upper liabilities and committed external fees.
    reasons.append("m9_cumulative_headroom_not_authorized")
    return AuthorizationDecision(
        campaign_id=registration.campaign_id,
        registration_sha256=sha256_json(registration),
        suite_sha256=suite_hash,
        reasons=tuple(dict.fromkeys(reasons)),
        evidence_sha256=sha256_json(evidence),
        ledger_available=availability.available,
    )


authorize = check_authorization
