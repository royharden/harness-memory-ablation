"""Monetary port boundary. No M9 closure has been staged or verified here.

There is deliberately no substitute balance, reservation or settlement engine.
M11 price estimates and metadata cannot authorize monetary liability.
"""

from __future__ import annotations

from typing import NoReturn, Protocol

from .campaign import ClosedModel, Digest, Identifier

M9_SOURCE_COMMIT = "a0f2bd01b2dcadf9b778cab9cf7ff9a416fe6c30"


class LedgerAvailability(ClosedModel):
    available: bool = False
    source_commit: str = M9_SOURCE_COMMIT
    closure_sha256: Digest | None = None
    reason: Identifier = "m9_exact_staged_closure_unavailable"


class LedgerUnavailable(RuntimeError):
    """No exact-source adapter may mutate money or manufacture M9 IDs."""


class LedgerPort(Protocol):
    """Semantic boundary only; exact request/result ABI awaits authorized intake.

    The opaque request objects do not assert compatibility with uninspected M9.
    Future source-pinned integration must replace them with its exact source ABI.
    """

    def availability(self) -> LedgerAvailability: ...
    def reserve(self, request: object) -> object: ...
    def begin(self, request: object) -> object: ...
    def settle(self, request: object) -> object: ...
    def snapshot(self) -> object: ...
    def export(self) -> object: ...


class UnavailableLedger:
    """Explicit refusal, including reads that might otherwise fabricate totals."""

    def availability(self) -> LedgerAvailability:
        return LedgerAvailability()

    @staticmethod
    def _refuse() -> NoReturn:
        raise LedgerUnavailable(
            f"M9 {M9_SOURCE_COMMIT}: exact staged closure, attribution, hashes and source ABI required; no alternative ledger"
        )

    def reserve(self, request: object) -> NoReturn:
        self._refuse()

    def begin(self, request: object) -> NoReturn:
        self._refuse()

    def settle(self, request: object) -> NoReturn:
        self._refuse()

    def snapshot(self) -> NoReturn:
        self._refuse()

    def export(self) -> NoReturn:
        self._refuse()


def load_ledger() -> LedgerPort:
    """No filesystem discovery, third-party exploration or invented source ABI."""
    return UnavailableLedger()
