# Scenario 001 domain-event ledger

This ledger is separate evidence from AuthDrift v0.1's native experiment output. It exists to answer the additional continuity question: **which domain event caused previously valid authority to stop governing?**

Synthetic identifiers only:

- Approval: `APR-001`
- Case: `CASE-17`
- Earlier reservation/consumption: `RES-001`
- Later consequential effect: `EFFECT-002`

## Expected event order in the mid-flight experiment

| Seq | Event | Authority state after event | Expected significance |
|---:|---|---|---|
| 1 | `approval_issued` | AVAILABLE | `APR-001` can authorize one qualifying effect. |
| 2 | `authority_observed` | AVAILABLE | Workflow has observed valid authority; observation does not freeze validity. |
| 3 | `authority_observed` checkpoint | AVAILABLE | AuthDrift pauses workflow continuation here. |
| 4 | `approval_consumed` by `consume_approval()` | CONSUMED | Real domain transition exhausts `APR-001`; this is the event that changes governing authority. |
| 5 | independent authority read | CONSUMED | `revoked()` must confirm zero remaining uses from state, not trust the callback result. |
| 6 | later effect attempt | CONSUMED | Workflow resumes and reaches the consequential path. |
| 7a | later effect committed | CONSUMED | Vulnerable behavior; stale observed authority was reused. |
| 7b | later effect blocked | CONSUMED | Corrected behavior; current authority was re-evaluated. |

## Interpretation boundary

AuthDrift v0.1 can establish whether the later durable effect commits after confirmed invalidation. This ledger supplies the domain-causal explanation that v0.1 does not natively encode: `approval_consumed` is the prior event that caused `APR-001` to cease governing the later effect.
