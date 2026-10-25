try:
    from .image_worker import ImageWorker
except (ImportError, ValueError):
    from image_worker import ImageWorker

__all__ = ["ImageWorker"]
