"""Candidate Codex JSON stream mapping, with no inferred provider model proof."""
from __future__ import annotations

from harnessrun import AttemptSpec, ContractError, LaunchSpec

from .base import AdapterBase, CaptureParser, NativePreparationRefused, PreparationContext, closed, counter, empty_buckets


class CodexAdapter(AdapterBase):
    harness_id = "codex"

    def __init__(self, context: PreparationContext, settings_sha256: str,
                 parser: CodexParser | None = None):
        super().__init__(context, settings_sha256)
        if parser is not None and parser.requested_model_id != context.provider.requested_model_id:
            raise ContractError("parser requested model differs from provider pin")
        self.parser = parser

    def planned_launch(self, spec: AttemptSpec) -> LaunchSpec:
        return self._launch(spec, (self.context.executable, "exec", "--json", "--model",
                                  self.context.provider.requested_model_id))

    def prepare(self, spec: AttemptSpec) -> LaunchSpec:
        self._validate(spec)
        raise NativePreparationRefused(
            "Codex native launch refused: P0/runtime activation, pinned image, model/loader/usage "
            "evidence and finite spend bound unsupported; no native fallback")

    def parse(self, data: bytes) -> tuple:
        if self.parser is None:
            raise ContractError("bind CodexParser to exact attempt and frozen capture before parsing")
        return self.parser.parse(data)


class CodexParser(CaptureParser):
    def _map(self, value: dict[str, object], start: int, end: int) -> tuple:
        kind = value.get("type")
        if kind == "thread.started":
            closed(value, {"type", "thread_id"})
            if not isinstance(value.get("thread_id"), str) or not value["thread_id"]:
                raise ContractError("thread ID missing")
            return (self._model(None, None, None, start, end),)
        if kind == "turn.started":
            closed(value, {"type"})
            return ()
        if kind in {"item.started", "item.updated", "item.completed"}:
            closed(value, {"type", "item"})
            item = closed(value.get("item"), {"id", "type", "text", "command", "aggregated_output",
                          "exit_code", "status", "changes", "tool", "arguments", "result", "error",
                          "server", "query", "items", "message"})
            item_kind = item.get("type")
            if item_kind not in {"agent_message", "reasoning", "command_execution", "file_change",
                                 "mcp_tool_call", "web_search", "todo_list", "error"}:
                raise ContractError("unknown Codex item type")
            if kind == "item.completed" and item_kind == "agent_message":
                # An item ID is not asserted to be a provider response ID.
                return (self._model(None, None, None, start, end),)
            return ()
        if kind == "turn.completed":
            closed(value, {"type", "usage"})
            raw = value.get("usage")
            buckets = empty_buckets()
            total = cached = reasoning = None
            if raw is not None:
                usage = closed(raw, {"input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens"})
                total = counter(usage.get("input_tokens"))
                cached = counter(usage.get("cached_input_tokens"))
                output = counter(usage.get("output_tokens"))
                reasoning = counter(usage.get("reasoning_output_tokens"))
                if total is not None and cached is not None:
                    if cached > total:
                        raise ContractError("cached subset exceeds Codex total input")
                    buckets["ordinary_input"] = total - cached
                if output is not None and reasoning is not None and reasoning > output:
                    raise ContractError("reasoning subset exceeds Codex total output")
                buckets["cached_input"] = cached
                buckets["output"] = output
            return (self._usage(start, end, buckets, input_total=total, cached=cached, reasoning=reasoning),)
        if kind in {"turn.failed", "error"}:
            closed(value, {"type", "error", "message"})
            return (self._usage(start, end, empty_buckets()),
                    self._event("stop", dict(reason="crash"), start, end))
        raise ContractError("unrecognized Codex native stream record")
