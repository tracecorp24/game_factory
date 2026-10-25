"""
Integration tests for Alembic migrations.
Ensures alembic upgrade head and downgrade base work cleanly.
"""
import os
from pathlib import Path
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_alembic_migration_upgrade_and_downgrade(tmp_path: Path):
    db_file = tmp_path / "test_migration.db"
    db_url = f"sqlite:///{db_file.as_posix()}"

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)

    # 1. Run upgrade head
    command.upgrade(alembic_cfg, "head")

    # 2. Inspect created tables
    engine = create_engine(db_url)
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    assert "run_events" in tables
    assert "outbox_events" in tables
    assert "organizations" in tables
    assert "artifacts" in tables
    assert len(tables) >= 38, f"Expected at least 38 tables, got {len(tables)}"

    # 3. Run downgrade base
    command.downgrade(alembic_cfg, "base")

    inspector_after = inspect(engine)
    tables_after = inspector_after.get_table_names()
    assert "run_events" not in tables_after

    engine.dispose()
