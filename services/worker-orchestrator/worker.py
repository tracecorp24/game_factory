"""Temporal worker service runner for CreativeForge orchestrator."""

from __future__ import annotations

import asyncio
import logging
import os
import sys

from .activities import execute_node_activity
from .workflow import CreativePipelineWorkflow

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("worker_orchestrator.worker")


async def run_worker() -> None:
    """Connects to Temporal cluster and runs the activity/workflow worker."""
    temporal_host = os.getenv("TEMPORAL_HOST", "localhost:7233")
    temporal_namespace = os.getenv("TEMPORAL_NAMESPACE", "default")
    task_queue = os.getenv("TEMPORAL_TASK_QUEUE", "creativeforge-pipeline-queue")

    try:
        from temporalio.client import Client
        from temporalio.worker import Worker
    except ImportError:
        logger.error("temporalio is required to run the worker daemon. Install with 'pip install temporalio'.")
        sys.exit(1)

    logger.info("Connecting to Temporal server at %s (namespace: %s)...", temporal_host, temporal_namespace)
    client = await Client.connect(temporal_host, namespace=temporal_namespace)

    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=[CreativePipelineWorkflow],
        activities=[execute_node_activity],
    )

    logger.info("Worker started successfully on task queue '%s'. Awaiting pipeline jobs...", task_queue)
    await worker.run()


if __name__ == "__main__":
    asyncio.run(run_worker())
