from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from magnatum_workflow.agents.discovery import DiscoveryAgent
from magnatum_workflow.storage import SQLiteStore
from magnatum_workflow.workflow import WorkflowEngine


QUALIFIED = {
    "source": "fictional_rss",
    "company": "Andes Operations Demo",
    "title": "Automate invoice and inventory reconciliation",
    "description": "Manual spreadsheets need API integration, validation, anomaly detection and an auditable dashboard.",
    "website": "https://example.invalid/andes",
    "contact_email": "ops@example.invalid",
}


class FakeAssistant:
    def __init__(self):
        self.calls = 0

    def complete_json(self, instruction, payload):
        self.calls += 1
        if "pain_summary" in instruction:
            return {"pain_summary": "Grounded summary from supplied evidence.", "company_context": "Fictional demo context."}
        return {"proposal": "Hello team, this is a grounded proposal based only on the supplied workflow evidence. " * 2}


class WorkflowTests(unittest.TestCase):
    def test_discovery_identifier_is_stable(self):
        agent = DiscoveryAgent()
        first = agent.run(QUALIFIED).opportunity.opportunity_id
        second = agent.run(dict(QUALIFIED)).opportunity.opportunity_id
        self.assertEqual(first, second)

    def test_pending_review_is_safe_default(self):
        state = WorkflowEngine().run(QUALIFIED)
        self.assertEqual("pending_review", state.opportunity.stage)
        self.assertEqual([], state.followups)

    def test_approval_creates_two_followups(self):
        state = WorkflowEngine().run(QUALIFIED, review_decision="approved")
        self.assertEqual("followup_scheduled", state.opportunity.stage)
        self.assertEqual([3, 7], [item.day for item in state.followups])

    def test_irrelevant_record_is_archived(self):
        record = {
            "source": "fictional",
            "company": "Banner Demo",
            "title": "Refresh a banner",
            "description": "Change colors and typography.",
        }
        state = WorkflowEngine().run(record)
        self.assertEqual("archived", state.opportunity.stage)
        self.assertEqual("", state.opportunity.proposal)

    def test_assistant_is_optional_and_audited(self):
        assistant = FakeAssistant()
        state = WorkflowEngine(assistant=assistant).run(QUALIFIED)
        self.assertTrue(state.ai_used)
        self.assertEqual(2, assistant.calls)
        self.assertEqual("ops@example.invalid", state.opportunity.contact_email)

    def test_state_and_audit_persist_in_sqlite(self):
        with tempfile.TemporaryDirectory() as temp:
            store = SQLiteStore(Path(temp) / "workflow.db")
            state = WorkflowEngine(store=store).run(QUALIFIED, review_decision="approved")
            restored = store.load(state.opportunity.opportunity_id)
            self.assertIsNotNone(restored)
            self.assertEqual("followup_scheduled", restored.opportunity.stage)
            self.assertEqual(len(state.audit), store.audit_count(state.opportunity.opportunity_id))
            store.close()


if __name__ == "__main__":
    unittest.main()

