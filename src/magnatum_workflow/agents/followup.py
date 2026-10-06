from __future__ import annotations

from ..models import FollowUp, WorkflowState


class FollowUpAgent:
    name = "followup"

    def run(self, state: WorkflowState) -> WorkflowState:
        opportunity = state.opportunity
        if opportunity.review_status != "approved":
            raise ValueError("follow-up requires an approved proposal")
        state.followups = [
            FollowUp(
                day=3,
                angle="technical clarification",
                message=f"Follow up with {opportunity.company} on the proposed auditable first pipeline slice.",
            ),
            FollowUp(
                day=7,
                angle="decision closure",
                message=f"Ask {opportunity.company} whether the workflow should be scoped, deferred or closed.",
            ),
        ]
        opportunity.stage = "followup_scheduled"
        state.add_event(self.name, "Day 3 and Day 7 follow-ups scheduled")
        return state

