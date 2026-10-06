from __future__ import annotations

from typing import Any

from .agents import DiscoveryAgent, EnrichmentAgent, FollowUpAgent, ProposalAgent, ReviewAgent, ScoringAgent
from .models import WorkflowState
from .providers import Assistant
from .storage import SQLiteStore


class WorkflowEngine:
    def __init__(self, store: SQLiteStore | None = None, assistant: Assistant | None = None, threshold: int = 45):
        self.store = store or SQLiteStore()
        self.threshold = threshold
        self.discovery = DiscoveryAgent()
        self.scoring = ScoringAgent()
        self.enrichment = EnrichmentAgent(assistant)
        self.proposal = ProposalAgent(assistant)
        self.review = ReviewAgent()
        self.followup = FollowUpAgent()

    def run(self, record: dict[str, Any], review_decision: str = "pending") -> WorkflowState:
        state = self.discovery.run(record)
        self.store.save(state)
        state = self.scoring.run(state)
        if state.opportunity.score < self.threshold:
            state.opportunity.stage = "archived"
            state.add_event("workflow", f"score below threshold={self.threshold}; archived")
            self.store.save(state)
            return state
        self.store.save(state)
        state = self.enrichment.run(state)
        self.store.save(state)
        state = self.proposal.run(state)
        self.store.save(state)
        state = self.review.run(state, review_decision)
        self.store.save(state)
        if review_decision == "approved":
            state = self.followup.run(state)
            self.store.save(state)
        return state

