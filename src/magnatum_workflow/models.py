from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class Opportunity:
    opportunity_id: str
    source: str
    company: str
    title: str
    description: str
    website: str = ""
    contact_email: str = ""
    score: int = 0
    tier: str = "unscored"
    pain_signals: list[str] = field(default_factory=list)
    pain_summary: str = ""
    company_context: str = ""
    proposal: str = ""
    stage: str = "discovered"
    review_status: str = "not_requested"


@dataclass
class FollowUp:
    day: int
    angle: str
    message: str


@dataclass
class AuditEvent:
    agent: str
    stage: str
    detail: str
    created_at: str = field(default_factory=utc_now)


@dataclass
class WorkflowState:
    opportunity: Opportunity
    followups: list[FollowUp] = field(default_factory=list)
    audit: list[AuditEvent] = field(default_factory=list)
    ai_used: bool = False
    errors: list[str] = field(default_factory=list)

    def add_event(self, agent: str, detail: str) -> None:
        self.audit.append(AuditEvent(agent=agent, stage=self.opportunity.stage, detail=detail))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "WorkflowState":
        return cls(
            opportunity=Opportunity(**payload["opportunity"]),
            followups=[FollowUp(**item) for item in payload.get("followups", [])],
            audit=[AuditEvent(**item) for item in payload.get("audit", [])],
            ai_used=bool(payload.get("ai_used", False)),
            errors=list(payload.get("errors", [])),
        )

