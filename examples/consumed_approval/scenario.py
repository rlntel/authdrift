"""Synthetic AuthDrift adapter for review only.

Pinned upstream: cheerstopriya/authdrift@
f79a62e97c7f61f189dcd6b926601db3071dff1e

Do not run before maintainer review of the callback/ordering mapping.
"""

from authdrift import Scenario, checkpoint


def build_scenario(safe: bool = False):
    state = {
        "approval": {
            "id": "APR-001",
            "case_id": "CASE-17",
            "remaining_uses": 1,
        },
        "durable_sink": [],
        "domain_events": [
            {"seq": 1, "type": "approval_issued", "approval_id": "APR-001"}
        ],
    }

    def authority_available() -> bool:
        approval = state["approval"]
        return approval["case_id"] == "CASE-17" and approval["remaining_uses"] > 0

    def consume_approval() -> None:
        """Real synthetic domain transition used as AuthDrift's callback.

        It is intentionally not named revoke: the scenario under review asks whether
        this normal one-use consumption event is a faithful v0.1 invalidation hook.
        """
        if not authority_available():
            return
        state["approval"]["remaining_uses"] = 0
        state["domain_events"].append(
            {
                "seq": len(state["domain_events"]) + 1,
                "type": "approval_consumed",
                "approval_id": "APR-001",
                "reservation_id": "RES-001",
                "case_id": "CASE-17",
            }
        )

    def authority_is_invalid() -> bool:
        """Independent state read; does not trust consume_approval() return data."""
        return state["approval"]["remaining_uses"] == 0

    def later_effect_committed() -> bool:
        """Inspect the durable synthetic sink, not model narration or intent."""
        return any(item["effect_id"] == "EFFECT-002" for item in state["durable_sink"])

    def workflow() -> None:
        observed_authority = authority_available()
        state["domain_events"].append(
            {
                "seq": len(state["domain_events"]) + 1,
                "type": "authority_observed",
                "approval_id": "APR-001",
                "available": observed_authority,
            }
        )

        checkpoint("authority_observed")

        state["domain_events"].append(
            {
                "seq": len(state["domain_events"]) + 1,
                "type": "later_effect_attempted",
                "effect_id": "EFFECT-002",
            }
        )

        permitted = authority_available() if safe else observed_authority
        if permitted:
            state["durable_sink"].append(
                {
                    "effect_id": "EFFECT-002",
                    "case_id": "CASE-17",
                    "approval_id": "APR-001",
                }
            )
            outcome = "later_effect_committed"
        else:
            outcome = "later_effect_blocked"

        state["domain_events"].append(
            {
                "seq": len(state["domain_events"]) + 1,
                "type": outcome,
                "effect_id": "EFFECT-002",
            }
        )

    return Scenario(
        name="consumed-approval-continuity",
        run=workflow,
        revoke=consume_approval,
        revoked=authority_is_invalid,
        committed=later_effect_committed,
        trigger="authority_observed",
    )
