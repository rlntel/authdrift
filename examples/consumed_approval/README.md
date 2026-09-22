# Consumed approval continuity fixture — PRE-EXECUTION REVIEW

**Status:** proposed adapter; do not execute before maintainer review.

**Pinned upstream:** `cheerstopriya/authdrift@f79a62e97c7f61f189dcd6b926601db3071dff1e`

## Authority contract

`APR-001` grants one qualifying consequential use for `CASE-17`. Once a legitimate `consume_approval()` domain transition reduces its remaining uses to zero, `APR-001` remains historical evidence but no longer authorizes any outstanding, uncommitted later effect.

## Mapping to AuthDrift v0.1

| AuthDrift input | Adapter mapping |
|---|---|
| `run()` | Synthetic workflow that observes authority, reaches the checkpoint, then attempts `EFFECT-002`. |
| `checkpoint()` | `authority_observed`, after the workflow's authority read and before `EFFECT-002`. |
| `revoke()` | `consume_approval()`, the real synthetic domain transition that exhausts `APR-001`. |
| `revoked()` | Independent read: `remaining_uses == 0`. |
| `committed()` | Durable sink read for `EFFECT-002`. |

## Why review is required before execution

AuthDrift v0.1 invokes the callback at the checkpoint. The proposed mapping is valid only if externalizing the genuine `consume_approval()` domain transition through that callback preserves the workflow's intended ordering and authorization semantics.

If it does not, this integration should be reported as needing an adapter / `BLOCKED_NOT_EXECUTED`; the fixture must not be rearranged merely to obtain a CLOSED or REVOCATION_ESCAPE result.

## Expected behavior only if mapping is accepted

The vulnerable path retains the pre-checkpoint authority observation. The corrected path re-reads current authority after continuation. Under the declared contract, the later effect must not inherit authority once the approval has been consumed.

The domain-event ledger is intentionally separate from AuthDrift's JSON evidence because v0.1 measures confirmed invalidation and later commit behavior, not the richer causal explanation of which domain event produced the invalidation.
