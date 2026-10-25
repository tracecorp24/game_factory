"""ComfyUI Deep Hybrid Integration schema (presets, versions, model catalog)

Revision ID: 0002_comfy_hybrid_schema
Revises: 0001_initial_schema
Create Date: 2026-10-25 18:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0002_comfy_hybrid_schema"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    # 1. comfy_presets
    if "comfy_presets" not in existing_tables:
        op.create_table(
            "comfy_presets",
            sa.Column("id", sa.String(length=64), primary_key=True, nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("category", sa.String(length=64), nullable=False),
            sa.Column("description", sa.String(length=1024), nullable=False, server_default=""),
            sa.Column("is_builtin", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("active_version", sa.String(length=32), nullable=False, server_default="1.0.0"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index("ix_comfy_presets_category", "comfy_presets", ["category"], unique=False)
        op.create_index("ix_comfy_presets_is_builtin", "comfy_presets", ["is_builtin"], unique=False)

    # 2. comfy_preset_versions
    if "comfy_preset_versions" not in existing_tables:
        op.create_table(
            "comfy_preset_versions",
            sa.Column("id", sa.String(length=64), primary_key=True, nullable=False),
            sa.Column("preset_id", sa.String(length=64), sa.ForeignKey("comfy_presets.id", ondelete="CASCADE"), nullable=False),
            sa.Column("version", sa.String(length=32), nullable=False),
            sa.Column("workflow_json", sa.JSON(), nullable=False),
            sa.Column("exposed_variables", sa.JSON(), nullable=False),
            sa.Column("checksum", sa.String(length=128), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.UniqueConstraint("preset_id", "version", name="uq_comfy_preset_version"),
        )
        op.create_index("ix_comfy_preset_versions_preset_id", "comfy_preset_versions", ["preset_id"], unique=False)

    # 3. comfy_models
    if "comfy_models" not in existing_tables:
        op.create_table(
            "comfy_models",
            sa.Column("id", sa.String(length=64), primary_key=True, nullable=False),
            sa.Column("filename", sa.String(length=255), nullable=False),
            sa.Column("model_type", sa.String(length=32), nullable=False),
            sa.Column("sha256", sa.String(length=128), nullable=False),
            sa.Column("is_downloaded", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("size_bytes", sa.BigInteger(), nullable=False, server_default="0"),
            sa.Column("vram_requirement_mb", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("local_path", sa.String(length=1024), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index("ix_comfy_models_type", "comfy_models", ["model_type"], unique=False)
        op.create_index("ix_comfy_models_filename", "comfy_models", ["filename"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "comfy_models" in existing_tables:
        op.drop_table("comfy_models")
    if "comfy_preset_versions" in existing_tables:
        op.drop_table("comfy_preset_versions")
    if "comfy_presets" in existing_tables:
        op.drop_table("comfy_presets")
