from __future__ import annotations

from ..models import WorkflowState


class ReviewAgent:
    name = "review"
    allowed = {"pending", "approved", "rejected"}

    def run(self, state: WorkflowState, decision: str = "pending") -> WorkflowState:
        decision = decision.lower().strip()
        if decision not in self.allowed:
            raise ValueError(f"review decision must be one of {sorted(self.allowed)}")
        state.opportunity.review_status = decision
        state.opportunity.stage = "pending_review" if decision == "pending" else decision
        state.add_event(self.name, f"human review status={decision}")
        return state

