from __future__ import annotations

import hashlib
import re
from typing import Any

from ..models import Opportunity, WorkflowState


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


class DiscoveryAgent:
    name = "discovery"

    def run(self, record: dict[str, Any]) -> WorkflowState:
        company = _clean(record.get("company"))
        title = _clean(record.get("title"))
        description = _clean(record.get("description"))
        source = _clean(record.get("source")) or "manual"
        if not company or not title or not description:
            raise ValueError("company, title and description are required")
        stable_key = "|".join(part.lower() for part in (source, company, title))
        opportunity_id = hashlib.sha256(stable_key.encode("utf-8")).hexdigest()[:16]
        state = WorkflowState(
            opportunity=Opportunity(
                opportunity_id=opportunity_id,
                source=source,
                company=company,
                title=title,
                description=description,
                website=_clean(record.get("website")),
                contact_email=_clean(record.get("contact_email")),
            )
        )
        state.add_event(self.name, "record validated, normalized and assigned a stable identifier")
        return state

