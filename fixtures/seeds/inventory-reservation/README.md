# inventory-reservation

Original builder-owned DEVELOPMENT seed only. Rights: private_only_pending_review.
Execution: NOT_RUN. Independent/P0/held-out status: absent.

<a id="claim-inventory-reservation-C1"></a>
- [inventory-reservation-C1] Reserving supply never mutates the caller reservation mapping.
<a id="claim-inventory-reservation-C2"></a>
- [inventory-reservation-C2] Requests above available supply raise ValueError.
<a id="claim-inventory-reservation-C3"></a>
- [inventory-reservation-C3] Missing SKUs have zero available supply.
<a id="claim-inventory-reservation-C4"></a>
- [inventory-reservation-C4] A zero reservation preserves the existing quantity.

Reference sources and checkers share builder lineage. They are private construction artifacts, not independent oracles. Future trusted custody must keep references and future features/tests out of candidate workspaces. No source execution has occurred.

Each checkpoint exposes baseline README/tripwires/claim checks, its feature request, and only tests with ordinal <= current. Earlier requests may be archived; future requests and all references are withheld by future custody tooling. Tests are source only and have not been evaluated.
