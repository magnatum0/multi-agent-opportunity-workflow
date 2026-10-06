from __future__ import annotations

from typing import Any

from ..models import WorkflowState
from ..providers import Assistant


class ProposalAgent:
    name = "proposal"

    def __init__(self, assistant: Assistant | None = None):
        self.assistant = assistant

    def run(self, state: WorkflowState) -> WorkflowState:
        opportunity = state.opportunity
        draft = (
            f"Hello {opportunity.company} team,\n\n"
            f"Your request for {opportunity.title.lower()} points to a practical opportunity to improve "
            f"{', '.join(opportunity.pain_signals[:4]) or 'the current workflow'}. "
            "I would begin with one auditable pipeline slice, explicit validation rules, and a review step before any operational action.\n\n"
            "Best regards,\nEsteban Barrera"
        )
        if self.assistant:
            result: dict[str, Any] = self.assistant.complete_json(
                "Refine the supplied proposal without adding facts, metrics, customers or capabilities. Return JSON with proposal.",
                {"evidence": opportunity.pain_summary, "proposal": draft},
            )
            candidate = result.get("proposal")
            if isinstance(candidate, str) and 80 <= len(candidate.strip()) <= 2000:
                draft = candidate.strip()
                state.ai_used = True
        opportunity.proposal = draft
        opportunity.stage = "proposal_ready"
        opportunity.review_status = "pending"
        state.add_event(self.name, f"proposal drafted; ai_used={state.ai_used}")
        return state

