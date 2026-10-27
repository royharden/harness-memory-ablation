"""Candidate Claude stream mappings. Hypotheses only until pinned native verification."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation

from harnessrun import AttemptSpec, ContractError, LaunchSpec

from .base import AdapterBase, CaptureParser, NativePreparationRefused, PreparationContext, closed, counter, empty_buckets


class ClaudeAdapter(AdapterBase):
    harness_id = "claude"

    def __init__(self, context: PreparationContext, settings_sha256: str,
                 parser: ClaudeParser | None = None):
        super().__init__(context, settings_sha256)
        if parser is not None and parser.requested_model_id != context.provider.requested_model_id:
            raise ContractError("parser requested model differs from provider pin")
        self.parser = parser

    def planned_launch(self, spec: AttemptSpec) -> LaunchSpec:
        """Inspection-only argv candidate; not an eligibility or authorization result."""
        return self._launch(spec, (self.context.executable, "--print", "--verbose",
                                  "--output-format", "stream-json", "--model",
                                  self.context.provider.requested_model_id,
                                  "--max-turns", str(spec.max_turns)))

    def prepare(self, spec: AttemptSpec) -> LaunchSpec:
        self._validate(spec)
        raise NativePreparationRefused(
            "Claude native launch refused: P0/runtime activation, pinned image, model/loader/usage "
            "evidence, M9 reservation and finite liability authorization unverified")

    def parse(self, data: bytes) -> tuple:
        if self.parser is None:
            raise ContractError("bind ClaudeParser to exact attempt and frozen capture before parsing")
        return self.parser.parse(data)


class ClaudeParser(CaptureParser):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._advertised: str | None = None

    def _map(self, value: dict[str, object], start: int, end: int) -> tuple:
        kind = value.get("type")
        if kind == "system" and value.get("subtype") == "init":
            closed(value, {"type", "subtype", "cwd", "session_id", "tools", "mcp_servers",
                           "model", "permissionMode", "slash_commands", "apiKeySource",
                           "claude_code_version", "output_style", "agents", "skills", "plugins", "uuid"})
            model = value.get("model")
            if model is not None and (not isinstance(model, str) or not model):
                raise ContractError("invalid advertised model")
            self._advertised = model
            # Tool/plugin lists cannot prove absence of global memory or loader sources.
            return (self._model(None, model, None, start, end),)
        if kind == "assistant":
            closed(value, {"type", "message", "parent_tool_use_id", "session_id", "uuid", "error"})
            message = closed(value.get("message"), {"id", "type", "role", "model", "content",
                            "stop_reason", "stop_sequence", "usage", "container", "context_management"})
            response_id = message.get("id")
            model = message.get("model")
            if response_id is not None and (not isinstance(response_id, str) or not response_id):
                raise ContractError("invalid response ID")
            if model is not None and (not isinstance(model, str) or not model):
                raise ContractError("invalid response model")
            records = [self._model(response_id, self._advertised, model, start, end)]
            if response_id:
                records.append(self._event("response", dict(response_id=response_id), start, end))
            records.append(self._claude_usage(message.get("usage"), start, end, "incremental"))
            return tuple(records)
        if kind == "result":
            closed(value, {"type", "subtype", "is_error", "duration_ms", "duration_api_ms", "num_turns",
                           "result", "session_id", "total_cost_usd", "usage", "modelUsage",
                           "permission_denials", "uuid", "errors", "stop_reason", "structured_output"})
            is_error = value.get("is_error")
            if type(is_error) is not bool:
                raise ContractError("result requires explicit boolean error state")
            return (self._claude_usage(value.get("usage"), start, end, "final", value.get("total_cost_usd")),
                    self._event("stop", dict(reason="crash" if is_error else "finished"), start, end))
        # Unknown record types must not silently hide nested usage/retries.
        raise ContractError("unrecognized Claude native stream record")

    def _claude_usage(self, raw: object, start: int, end: int, basis: str,
                      estimate: object = None):
        if raw is None:
            return self._usage(start, end, empty_buckets(), basis=basis)
        usage = closed(raw, {"input_tokens", "output_tokens", "cache_read_input_tokens",
                            "cache_creation_input_tokens", "cache_creation", "server_tool_use",
                            "service_tier", "inference_geo"})
        buckets = empty_buckets()
        buckets["ordinary_input"] = counter(usage.get("input_tokens"))
        buckets["cached_input"] = counter(usage.get("cache_read_input_tokens"))
        buckets["output"] = counter(usage.get("output_tokens"))
        # Undifferentiated writes never become an assumed five-minute bucket.
        creation = usage.get("cache_creation")
        total_write = counter(usage.get("cache_creation_input_tokens"))
        if creation is not None:
            split = closed(creation, {"ephemeral_5m_input_tokens", "ephemeral_1h_input_tokens"})
            five = counter(split.get("ephemeral_5m_input_tokens"))
            hour = counter(split.get("ephemeral_1h_input_tokens"))
            if total_write is not None and five is not None and hour is not None and five + hour != total_write:
                raise ContractError("Claude split cache-write counters contradict total")
            buckets["cache_write_5m"], buckets["cache_write_1h"] = five, hour
        decimal_estimate = None
        if estimate is not None:
            if isinstance(estimate, bool) or not isinstance(estimate, (str, int, float)):
                raise ContractError("invalid harness estimate")
            try:
                amount = Decimal(str(estimate))
            except InvalidOperation as exc:
                raise ContractError("invalid harness estimate") from exc
            if not amount.is_finite() or amount < 0:
                raise ContractError("invalid harness estimate")
            decimal_estimate = format(amount, "f")
        return self._usage(start, end, buckets, basis=basis, estimate=decimal_estimate)
