"""
Standalone Event Relay Worker CLI Daemon.
CreativeForge Intelligence Studio v3.0 - Module M06 / M11.
"""

import asyncio
import logging
from services.worker_event_relay.relay import event_relay_worker

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("worker_event_relay.runner")


async def main():
    logger.info("Starting Event Relay Worker daemon...")
    try:
        await event_relay_worker.start()
    except (KeyboardInterrupt, asyncio.CancelledError):
        event_relay_worker.stop()
        logger.info("Relay daemon shut down cleanly.")


if __name__ == "__main__":
    asyncio.run(main())
