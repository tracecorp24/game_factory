"""
Integration tests for LedgerService, monotonic sequencing, atomicity, redaction, and outbox dispatch.
"""
from datetime import datetime, timezone
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from packages.contracts.events import EventEnvelope, EventType
from services.api.app.db.base import Base
from services.api.app.db.models import (
    Organization,
    Workspace,
    Project,
    Campaign,
    Request,
    Workflow,
    WorkflowVersion,
    Run,
    RunEvent,
    OutboxEvent,
)
from services.api.app.modules.ledger.service import LedgerService
from services.api.app.modules.ledger.redaction import redact_data


@pytest.fixture
async def async_db_session():
    """Provides an isolated in-memory SQLite database session for ledger tests."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        # Seed parent foreign key records
        org = Organization(id="org_1", name="Test Org")
        ws = Workspace(id="ws_1", org_id="org_1", name="Test Workspace")
        proj = Project(id="proj_1", workspace_id="ws_1", name="Test Project")
        camp = Campaign(id="camp_1", project_id="proj_1", objective="UA")
        req = Request(id="req_1", campaign_id="camp_1", normalized_brief_json={})
        wf = Workflow(id="wf_1", project_id="proj_1", name="Test Pipeline")
        wfv = WorkflowVersion(id="wfv_1", workflow_id="wf_1", version=1, graph_json={}, sha256="sha256:dummy")
        run = Run(id="run_1", request_id="req_1", workflow_version_id="wfv_1", project_id="proj_1", state="running")

        session.add_all([org, ws, proj, camp, req, wf, wfv, run])
        await session.commit()

        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_ledger_record_event_atomic_and_monotonic(async_db_session: AsyncSession):
    session = async_db_session

    ev1 = EventEnvelope.create(
        event_type=EventType.RUN_STARTED,
        project_id="proj_1",
        campaign_id="camp_1",
        request_id="req_1",
        run_id="run_1",
        run_seq=1,
        payload_preview={"status": "started"},
    )
    recorded1 = await LedgerService.record_event(session, ev1)
    await session.commit()

    assert recorded1.run_seq == 1
    assert recorded1.integrity_hash.startswith("sha256:")

    # Verify atomic outbox entry creation
    outbox_entries = await LedgerService.get_undispatched_outbox(session)
    assert len(outbox_entries) == 1
    assert outbox_entries[0].event_id == recorded1.event_id
    assert outbox_entries[0].dispatched_at is None

    # Record second event - sequence must automatically advance monotonically
    ev2 = EventEnvelope.create(
        event_type=EventType.AGENT_STARTED,
        project_id="proj_1",
        campaign_id="camp_1",
        request_id="req_1",
        run_id="run_1",
        run_seq=1,  # Passing 1 will test auto-monotonic increment to 2
        payload_preview={"agent": "concept_agent"},
    )
    recorded2 = await LedgerService.record_event(session, ev2)
    await session.commit()

    assert recorded2.run_seq == 2


@pytest.mark.asyncio
async def test_ledger_redaction_of_sensitive_data(async_db_session: AsyncSession):
    session = async_db_session

    raw_payload_with_secrets = {
        "model": "claude-3-5-sonnet",
        "api_key": "sk-secret-token-12345",
        "nested": {
            "password": "super-secret-password",
            "contact_email": "developer@gamee.com",
        },
        "safe_metric": 42,
    }

    ev = EventEnvelope.create(
        event_type=EventType.MODEL_CALL_FINISHED,
        project_id="proj_1",
        campaign_id="camp_1",
        request_id="req_1",
        run_id="run_1",
        run_seq=1,
        redaction_level="sanitized",
        payload_preview=raw_payload_with_secrets,
    )

    recorded = await LedgerService.record_event(session, ev, raw_payload=raw_payload_with_secrets)
    await session.commit()

    preview = recorded.payload_preview
    assert preview["api_key"] == "[REDACTED_CREDENTIAL]"
    assert preview["nested"]["password"] == "[REDACTED_CREDENTIAL]"
    assert preview["nested"]["contact_email"] == "[REDACTED_EMAIL]"
    assert preview["safe_metric"] == 42


@pytest.mark.asyncio
async def test_get_run_events_and_since_seq(async_db_session: AsyncSession):
    session = async_db_session

    for i in range(1, 6):
        ev = EventEnvelope.create(
            event_type=EventType.NODE_STARTED,
            project_id="proj_1",
            campaign_id="camp_1",
            request_id="req_1",
            run_id="run_1",
            run_seq=i,
            payload_preview={"step": i},
        )
        await LedgerService.record_event(session, ev)
    await session.commit()

    all_events = await LedgerService.get_run_events(session, run_id="run_1", since_seq=0)
    assert len(all_events) == 5
    assert [e.run_seq for e in all_events] == [1, 2, 3, 4, 5]

    filtered_events = await LedgerService.get_run_events(session, run_id="run_1", since_seq=3)
    assert len(filtered_events) == 2
    assert [e.run_seq for e in filtered_events] == [4, 5]


@pytest.mark.asyncio
async def test_outbox_dispatch_lifecycle(async_db_session: AsyncSession):
    session = async_db_session

    ev = EventEnvelope.create(
        event_type=EventType.TOOL_CALL_STARTED,
        project_id="proj_1",
        campaign_id="camp_1",
        request_id="req_1",
        run_id="run_1",
        run_seq=1,
        payload_preview={"tool": "browser_qa"},
    )
    await LedgerService.record_event(session, ev)
    await session.commit()

    pending = await LedgerService.get_undispatched_outbox(session)
    assert len(pending) == 1

    outbox_id = pending[0].id
    await LedgerService.mark_outbox_dispatched(session, [outbox_id])
    await session.commit()

    remaining_pending = await LedgerService.get_undispatched_outbox(session)
    assert len(remaining_pending) == 0


@pytest.mark.asyncio
async def test_ledger_transaction_atomicity_on_rollback(async_db_session: AsyncSession):
    session = async_db_session

    ev = EventEnvelope.create(
        event_type=EventType.RUN_FAILED,
        project_id="proj_1",
        campaign_id="camp_1",
        request_id="req_1",
        run_id="run_1",
        run_seq=1,
        payload_preview={"error": "simulated abort"},
    )
    await LedgerService.record_event(session, ev)
    # Rollback explicitly without commit
    await session.rollback()

    run_events = await LedgerService.get_run_events(session, run_id="run_1")
    outbox_events = await LedgerService.get_undispatched_outbox(session)

    assert len(run_events) == 0
    assert len(outbox_events) == 0
