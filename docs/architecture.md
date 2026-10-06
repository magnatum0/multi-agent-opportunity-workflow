# Architecture notes

## Why a hybrid workflow

Opportunity workflows combine tasks with different reliability requirements. Stable identifiers, score thresholds, audit events, and schedules should be deterministic. Language refinement can benefit from an LLM, but its output must be optional, validated, and reviewable.

## Shared state

Each run carries a `WorkflowState` containing the normalized opportunity, score, pain signals, enrichment notes, proposal, review status, follow-up actions, AI-use flag, errors, and audit events.

Every agent receives that state and returns an updated state. `WorkflowEngine` controls the order and branches. `SQLiteStore` persists a JSON snapshot plus append-only audit events after every transition.

## State transitions

| Current stage | Condition | Next stage |
|---|---|---|
| discovered | record validated | scored |
| scored | score below threshold | archived |
| scored | score meets threshold | enriched |
| enriched | context available | proposal_ready |
| proposal_ready | no human decision | pending_review |
| pending_review | rejected | rejected |
| pending_review | approved | approved |
| approved | follow-ups created | followup_scheduled |

## AI boundary

The optional assistant receives only the fictional or caller-supplied opportunity evidence. It may return a pain summary, company context, or refined proposal. The workflow ignores any assistant-generated email address and never performs an outbound action.

## Production extensions

A production implementation could add durable queues, Postgres checkpointing, role-based review, rate-limit policies, observability, and a graph orchestrator such as LangGraph. Those are intentionally outside this repository's claims.

