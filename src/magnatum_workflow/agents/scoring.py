from __future__ import annotations

from ..models import WorkflowState


SIGNALS = {
    "api": 12,
    "integration": 12,
    "automate": 14,
    "automation": 14,
    "manual": 8,
    "spreadsheet": 8,
    "invoice": 10,
    "inventory": 10,
    "validation": 8,
    "anomaly": 8,
    "audit": 8,
    "dashboard": 6,
    "data": 5,
    "document": 6,
    "workflow": 8,
}


class ScoringAgent:
    name = "scoring"

    def run(self, state: WorkflowState) -> WorkflowState:
        opportunity = state.opportunity
        text = f"{opportunity.title} {opportunity.description}".lower()
        hits = [(word, points) for word, points in SIGNALS.items() if word in text]
        opportunity.pain_signals = [word for word, _ in hits]
        score = min(85, sum(points for _, points in hits))
        if opportunity.contact_email:
            score += 10
        if opportunity.website:
            score += 5
        opportunity.score = min(100, score)
        opportunity.tier = "A" if score >= 70 else "B" if score >= 45 else "discard"
        opportunity.stage = "scored"
        state.add_event(self.name, f"score={opportunity.score}; tier={opportunity.tier}; signals={opportunity.pain_signals}")
        return state

