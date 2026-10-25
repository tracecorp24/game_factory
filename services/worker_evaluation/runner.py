"""
Standalone Evaluation Worker CLI Runner.
CreativeForge Intelligence Studio v3.0 - Module M07.
"""

import asyncio
import logging
import sys
from services.worker_evaluation.gates.base import GateExecutionContext
from services.worker_evaluation.pipeline import QualityGatePipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("worker_evaluation.runner")


async def main():
    logger.info("Initializing CreativeForge Worker-Evaluation (7 Quality Gates)...")
    pipeline = QualityGatePipeline()

    sample_context = GateExecutionContext(
        artifact={
            "artifact_id": "art_sample_001",
            "run_id": "run_demo_01",
            "type": "image",
            "storage_ref": "data/storage/sample.png",
            "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "bytes": 1024 * 500,
            "media_meta": {
                "width": 1080,
                "height": 1920,
                "format": "PNG",
                "cta_text": "Play Now",
                "contrast_ratio": 5.2,
            },
        },
        creative_hypothesis={
            "intended_hook": "Tap the matching gem before time runs out!",
            "creative_mechanism": "Match-3 color chain puzzle",
        },
    )

    report = await pipeline.run(sample_context)
    logger.info(f"Evaluation finished: Verdict={report.overall_verdict.value}, Score={report.overall_score}/5.0")
    print(report.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
