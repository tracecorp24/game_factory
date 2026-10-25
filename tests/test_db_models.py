"""
Unit tests for SQLAlchemy 2.0 database models, table registration, and schema constraints.
"""
import pytest
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine

from services.api.app.db.base import Base
import services.api.app.db.models  # Ensures all 46 models are loaded


EXPECTED_TABLES = {
    # Organizations
    "organizations",
    "users",
    "memberships",
    "workspaces",
    "projects",
    "campaigns",
    # Intelligence
    "source_registry",
    "source_sync_jobs",
    "raw_snapshots",
    "trend_observations",
    "trend_reports",
    # Game DNA
    "game_profiles",
    "game_profile_versions",
    "asset_rights",
    # Concepts
    "creative_hypotheses",
    "concept_boards",
    "concept_decisions",
    # Workflows
    "workflows",
    "workflow_versions",
    "requests",
    "runs",
    "run_manifests",
    # Ledger
    "run_events",
    "outbox_events",
    "audit_events",
    # Executions
    "node_executions",
    "attempts",
    "agent_sessions",
    "model_invocations",
    "usage_records",
    "price_catalog_versions",
    "cost_entries",
    "tool_calls",
    # Artifacts
    "artifacts",
    "artifact_lineage",
    "quality_gate_results",
    "evaluations",
    "human_reviews",
    # Experiments
    "experiments",
    "experiment_variants",
    "experiment_outcomes",
    # Prompts & Policies
    "prompt_templates",
    "prompt_versions",
    "model_policies",
    "context_bundles",
    # Analytics
    "analytics_rollups_hourly",
}


def test_all_expected_tables_present_in_metadata():
    actual_tables = set(Base.metadata.tables.keys())
    missing_tables = EXPECTED_TABLES - actual_tables
    assert not missing_tables, f"Missing tables in metadata: {missing_tables}"
    assert len(actual_tables) >= len(EXPECTED_TABLES)


@pytest.mark.asyncio
async def test_schema_ddl_creation_in_sqlite():
    """
    Validates that DDL for all 46 tables can be created cleanly in a live engine without any dialect/syntax errors.
    """
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Inspect created tables in SQLite
    async with engine.connect() as conn:
        tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
        assert len(tables) >= len(EXPECTED_TABLES)
        assert "run_events" in tables
        assert "outbox_events" in tables
        assert "attempts" in tables

    await engine.dispose()


def test_table_constraints_defined():
    # Verify UniqueConstraint on run_events (run_id, run_seq)
    run_events_table = Base.metadata.tables["run_events"]
    uqs = [c.name for c in run_events_table.constraints if hasattr(c, "columns")]
    assert "uq_run_events_run_id_seq" in uqs

    # Verify UniqueConstraint on attempts (node_execution_id, attempt_no)
    attempts_table = Base.metadata.tables["attempts"]
    attempt_uqs = [c.name for c in attempts_table.constraints if hasattr(c, "columns")]
    assert "uq_attempt_node_no" in attempt_uqs

    # Verify Composite Primary Key on artifact_lineage
    lineage_table = Base.metadata.tables["artifact_lineage"]
    pk_cols = [c.name for c in lineage_table.primary_key.columns]
    assert set(pk_cols) == {"parent_artifact_id", "child_artifact_id", "relation_type"}
