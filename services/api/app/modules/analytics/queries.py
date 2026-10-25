"""
SQL query definitions and PostgreSQL rollup queries for Analytics Engine.
CreativeForge Intelligence Studio v3.0 - Module M12.
"""

from typing import Dict, List, Optional

SQL_HOURLY_ROLLUP_CREATE = """
CREATE TABLE IF NOT EXISTS analytics_rollups_hourly (
    project_id VARCHAR(64) NOT NULL,
    hour TIMESTAMP WITH TIME ZONE NOT NULL,
    dimensions JSONB NOT NULL DEFAULT '{}'::jsonb,
    aggregate_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    watermark_seq BIGINT NOT NULL DEFAULT 0,
    PRIMARY KEY (project_id, hour, dimensions)
);
CREATE INDEX IF NOT EXISTS idx_analytics_rollups_time ON analytics_rollups_hourly (hour, project_id);
"""

SQL_OVERVIEW_KPI_QUERY = """
WITH run_stats AS (
    SELECT
        COUNT(*) AS total_runs,
        COUNT(*) FILTER (WHERE state = 'completed') AS completed_runs,
        COUNT(*) FILTER (WHERE state = 'failed') AS failed_runs,
        COUNT(*) FILTER (WHERE state = 'cancelled') AS cancelled_runs,
        COUNT(*) FILTER (WHERE state IN ('completed', 'failed', 'cancelled')) AS terminal_runs
    FROM runs
    WHERE (:project_id IS NULL OR project_id = :project_id)
      AND (:date_from IS NULL OR started_at >= :date_from)
      AND (:date_to IS NULL OR started_at <= :date_to)
),
artifact_stats AS (
    SELECT
        COUNT(*) AS total_artifacts,
        COUNT(*) FILTER (WHERE state = 'approved') AS approved_artifacts
    FROM artifacts a
    JOIN runs r ON a.run_id = r.id
    WHERE (:project_id IS NULL OR r.project_id = :project_id)
),
cost_stats AS (
    SELECT
        COALESCE(SUM(amount), 0.0) AS total_known_spend
    FROM cost_entries ce
    WHERE status IN ('actual', 'reconciled')
),
invocation_stats AS (
    SELECT
        COUNT(*) AS total_invocations,
        COUNT(*) FILTER (WHERE cost_kind IS NULL OR amount IS NULL) AS unpriced_invocations
    FROM model_invocations mi
    LEFT JOIN cost_entries ce ON ce.invocation_id = mi.id
)
SELECT
    r.total_runs,
    r.completed_runs,
    r.failed_runs,
    r.cancelled_runs,
    r.terminal_runs,
    CASE 
        WHEN r.terminal_runs > 0 THEN ROUND((r.completed_runs::numeric / r.terminal_runs::numeric), 4)
        ELSE NULL 
    END AS run_success_rate,
    a.total_artifacts,
    a.approved_artifacts,
    c.total_known_spend,
    CASE
        WHEN a.approved_artifacts > 0 THEN ROUND((c.total_known_spend::numeric / a.approved_artifacts::numeric), 4)
        ELSE NULL
    END AS cost_per_approved_artifact,
    i.unpriced_invocations,
    CASE
        WHEN i.total_invocations > 0 THEN ROUND((i.unpriced_invocations::numeric / i.total_invocations::numeric), 4)
        ELSE NULL
    END AS unpriced_call_ratio
FROM run_stats r, artifact_stats a, cost_stats c, invocation_stats i;
"""
