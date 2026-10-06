from __future__ import annotations

import argparse
import json
from pathlib import Path

from .storage import SQLiteStore
from .workflow import WorkflowEngine


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the sanitized MAGNATUM workflow demo")
    parser.add_argument("--auto-approve", action="store_true", help="Approve qualified fictional proposals")
    parser.add_argument("--data", type=Path, default=Path("sample_data/opportunities.json"))
    parser.add_argument("--db", type=Path, default=Path(".local/demo.db"))
    args = parser.parse_args()
    args.db.parent.mkdir(parents=True, exist_ok=True)
    records = json.loads(args.data.read_text(encoding="utf-8"))
    engine = WorkflowEngine(store=SQLiteStore(args.db))
    for record in records:
        decision = "approved" if args.auto_approve else "pending"
        state = engine.run(record, review_decision=decision)
        opportunity = state.opportunity
        print(
            f"{opportunity.opportunity_id} | {opportunity.company} | score={opportunity.score} "
            f"| stage={opportunity.stage} | ai_used={state.ai_used} | audit={len(state.audit)}"
        )


if __name__ == "__main__":
    main()

