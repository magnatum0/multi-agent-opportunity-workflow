from __future__ import annotations

from typing import Any

from ..models import WorkflowState
from ..providers import Assistant


class EnrichmentAgent:
    name = "enrichment"

    def __init__(self, assistant: Assistant | None = None):
        self.assistant = assistant

    def run(self, state: WorkflowState) -> WorkflowState:
        opportunity = state.opportunity
        evidence = {
            "company": opportunity.company,
            "title": opportunity.title,
            "description": opportunity.description,
            "website": opportunity.website,
            "pain_signals": opportunity.pain_signals,
        }
        opportunity.pain_summary = (
            "Operational evidence indicates needs around " + ", ".join(opportunity.pain_signals[:5])
            if opportunity.pain_signals
            else "No material automation or data pain was detected."
        )
        opportunity.company_context = f"Source: {opportunity.source}; website supplied: {bool(opportunity.website)}."
        if self.assistant:
            result: dict[str, Any] = self.assistant.complete_json(
                "Use only the supplied evidence. Return JSON with pain_summary and company_context. Do not invent names, emails, metrics or customers.",
                evidence,
            )
            if isinstance(result.get("pain_summary"), str) and result["pain_summary"].strip():
                opportunity.pain_summary = result["pain_summary"].strip()
            if isinstance(result.get("company_context"), str) and result["company_context"].strip():
                opportunity.company_context = result["company_context"].strip()
            state.ai_used = True
        opportunity.stage = "enriched"
        state.add_event(self.name, f"context enriched; ai_used={state.ai_used}")
        return state

