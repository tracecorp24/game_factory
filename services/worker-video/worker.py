try:
    from .video_worker import VideoWorker
except (ImportError, ValueError):
    from video_worker import VideoWorker

__all__ = ["VideoWorker"]
