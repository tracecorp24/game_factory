"""
Execution Ledger and Transactional Outbox Service.
Guarantees atomic writes of run events and outbox events in a single PostgreSQL transaction.
"""
from datetime import datetime, timezone
import json
from typing import Any, Dict, List, Optional
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from packages.contracts.events import EventEnvelope, EventType
from services.api.app.db.models.ledger import RunEvent, OutboxEvent
from services.api.app.modules.ledger.redaction import redact_data


class LedgerService:
    """
    Core Ledger Service responsible for append-only event logging,
    monotonic sequencing, SHA256 integrity verification, and transactional outbox.
    """

    @classmethod
    async def get_next_run_seq(cls, session: AsyncSession, run_id: str) -> int:
        """
        Thread-safe monotonic sequence calculator for a given run_id.
        """
        stmt = select(func.coalesce(func.max(RunEvent.run_seq), 0)).where(RunEvent.run_id == run_id)
        result = await session.execute(stmt)
        max_seq = result.scalar_one()
        return int(max_seq) + 1

    @classmethod
    async def record_event(
        cls,
        session: AsyncSession,
        event: EventEnvelope,
        raw_payload: Optional[Dict[str, Any]] = None,
    ) -> RunEvent:
        """
        Atomically records an event to run_events and outbox_events in the current transaction.
        - Calculates next monotonic run_seq if required
        - Applies sensitive data redaction
        - Computes and sets cryptographic integrity hash
        - Writes both RunEvent and OutboxEvent
        """
        # 1. Determine monotonic sequence number
        current_next_seq = await cls.get_next_run_seq(session, event.run_id)
        run_seq = event.run_seq
        if run_seq is None or run_seq < current_next_seq:
            run_seq = current_next_seq

        # 2. Sanitize and redact payload preview
        raw = raw_payload if raw_payload is not None else event.payload_preview
        sanitized_payload = redact_data(raw, level=event.redaction_level)

        # 3. Calculate SHA256 integrity hash
        event_type_str = event.event_type.value if isinstance(event.event_type, EventType) else str(event.event_type)
        integrity_hash = EventEnvelope.calculate_hash(
            event_id=event.event_id,
            event_type=event_type_str,
            run_id=event.run_id,
            run_seq=run_seq,
            occurred_at=event.occurred_at,
            payload_preview=sanitized_payload,
            payload_ref=event.payload_ref,
        )

        # 4. Construct RunEvent entity (Append-only)
        db_run_event = RunEvent(
            event_id=event.event_id,
            run_id=event.run_id,
            run_seq=run_seq,
            event_type=event_type_str,
            schema_version=event.schema_version,
            occurred_at=event.occurred_at,
            recorded_at=datetime.now(timezone.utc),
            project_id=event.project_id,
            campaign_id=event.campaign_id,
            request_id=event.request_id,
            workflow_version_id=event.workflow_version_id,
            node_execution_id=event.node_execution_id,
            attempt_id=event.attempt_id,
            agent_id=event.agent_id,
            trace_id=event.trace_id,
            span_id=event.span_id,
            actor_type=event.actor_type,
            actor_id=event.actor_id,
            correlation_id=event.correlation_id,
            causation_event_id=event.causation_event_id,
            payload_preview=sanitized_payload,
            payload_ref=event.payload_ref,
            redaction_level=event.redaction_level,
            integrity_hash=integrity_hash,
        )

        # 5. Construct Transactional Outbox entity
        outbox_payload = {
            "event_id": db_run_event.event_id,
            "event_type": db_run_event.event_type,
            "run_id": db_run_event.run_id,
            "run_seq": db_run_event.run_seq,
            "project_id": db_run_event.project_id,
            "occurred_at": db_run_event.occurred_at.isoformat(),
            "payload_preview": sanitized_payload,
            "payload_ref": db_run_event.payload_ref,
            "actor_type": db_run_event.actor_type,
            "actor_id": db_run_event.actor_id,
            "integrity_hash": integrity_hash,
        }

        db_outbox_event = OutboxEvent(
            event_id=db_run_event.event_id,
            run_id=db_run_event.run_id,
            payload=outbox_payload,
            dispatched_at=None,
            attempts=0,
            last_error=None,
        )

        # 6. Add both to same session (Atomic transaction)
        session.add(db_run_event)
        session.add(db_outbox_event)
        await session.flush()

        return db_run_event

    @classmethod
    async def get_run_events(
        cls,
        session: AsyncSession,
        run_id: str,
        since_seq: int = 0,
        limit: int = 1000,
    ) -> List[RunEvent]:
        """
        Retrieves ordered event stream for a run starting from since_seq.
        """
        stmt = (
            select(RunEvent)
            .where(RunEvent.run_id == run_id, RunEvent.run_seq > since_seq)
            .order_by(RunEvent.run_seq.asc())
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def get_undispatched_outbox(
        cls,
        session: AsyncSession,
        limit: int = 100,
    ) -> List[OutboxEvent]:
        """
        Retrieves pending undispatched events for relay to SSE/event bus.
        """
        stmt = (
            select(OutboxEvent)
            .where(OutboxEvent.dispatched_at.is_(None))
            .order_by(OutboxEvent.created_at.asc())
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def mark_outbox_dispatched(
        cls,
        session: AsyncSession,
        outbox_ids: List[str],
    ) -> None:
        """
        Marks processed outbox events as dispatched.
        """
        if not outbox_ids:
            return
        now = datetime.now(timezone.utc)
        stmt = (
            update(OutboxEvent)
            .where(OutboxEvent.id.in_(outbox_ids))
            .values(dispatched_at=now)
        )
        await session.execute(stmt)
        await session.flush()

    @classmethod
    async def record_outbox_failure(
        cls,
        session: AsyncSession,
        outbox_id: str,
        error_message: str,
    ) -> None:
        """
        Increments retry attempts and records failure message on outbox event.
        """
        stmt = (
            update(OutboxEvent)
            .where(OutboxEvent.id == outbox_id)
            .values(
                attempts=OutboxEvent.attempts + 1,
                last_error=error_message,
            )
        )
        await session.execute(stmt)
        await session.flush()
