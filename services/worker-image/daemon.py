"""
ComfyUI Daemon Supervisor and Hardware Health Monitor.
Controls ComfyUI headless server as a managed OS subprocess with automatic recovery,
VRAM monitoring, health pings, and clean process teardown.
"""
from __future__ import annotations

import atexit
import logging
import os
import platform
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import httpx

logger = logging.getLogger("comfy_daemon_supervisor")


class ComfyDaemonError(Exception):
    """Base exception for ComfyUI daemon supervisor errors."""
    pass


class ComfyDaemonSupervisor:
    """
    Manages the lifecycle of a headless ComfyUI server subprocess.
    """

    def __init__(
        self,
        comfy_dir: Optional[Union[str, Path]] = None,
        python_path: Optional[str] = None,
        host: str = "127.0.0.1",
        port: int = 8188,
        gpu_device: Optional[int] = None,
        vram_mode: str = "highvram",
        extra_args: Optional[List[str]] = None,
        auto_restart: bool = True,
        log_file: Optional[Union[str, Path]] = None,
    ):
        self.host = host
        self.port = port
        self.gpu_device = gpu_device
        self.vram_mode = vram_mode.lower()
        self.extra_args = extra_args or []
        self.auto_restart = auto_restart
        self.python_path = python_path or sys.executable
        self.log_file = log_file

        self.comfy_dir = self._resolve_comfy_dir(comfy_dir)
        self.main_py_path = self.comfy_dir / "main.py" if self.comfy_dir else None

        self.process: Optional[subprocess.Popen] = None
        self._start_time: Optional[float] = None
        self._log_handle = None

        # Clean up process on interpreter exit
        atexit.register(self.stop)

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    @property
    def ws_url(self) -> str:
        return f"ws://{self.host}:{self.port}"

    def _resolve_comfy_dir(self, comfy_dir: Optional[Union[str, Path]]) -> Optional[Path]:
        """Locates ComfyUI root directory."""
        if comfy_dir:
            p = Path(comfy_dir).resolve()
            if (p / "main.py").exists():
                return p

        # Check environment variable
        env_path = os.environ.get("COMFYUI_PATH")
        if env_path:
            p = Path(env_path).resolve()
            if (p / "main.py").exists():
                return p

        # Check standard locations relative to current workspace
        workspace_root = Path(__file__).resolve().parents[2]
        candidate = workspace_root / "ComfyUI"
        if (candidate / "main.py").exists():
            return candidate

        return None

    def build_command(self) -> List[str]:
        """Constructs CLI arguments for launching ComfyUI/main.py."""
        if not self.main_py_path:
            raise ComfyDaemonError("Cannot build launch command: ComfyUI main.py path is not resolved.")

        cmd = [
            str(self.python_path),
            str(self.main_py_path),
            "--listen", self.host,
            "--port", str(self.port),
        ]

        # VRAM mode argument
        if self.vram_mode == "highvram":
            cmd.append("--highvram")
        elif self.vram_mode == "lowvram":
            cmd.append("--lowvram")
        elif self.vram_mode == "normalvram":
            cmd.append("--normalvram")
        elif self.vram_mode == "cpu":
            cmd.append("--cpu")

        # GPU device selection
        if self.gpu_device is not None:
            cmd.extend(["--cuda-device", str(self.gpu_device)])

        # Additional user/environment arguments
        if self.extra_args:
            cmd.extend(self.extra_args)

        return cmd

    def is_running(self) -> bool:
        """Returns True if the managed subprocess is currently running."""
        if self.process is None:
            return False
        return self.process.poll() is None

    def start(self, wait_for_ready: bool = False, timeout_seconds: float = 30.0) -> None:
        """
        Launches the ComfyUI subprocess in the background.
        """
        if self.is_running():
            logger.info(f"ComfyUI daemon is already running (PID: {self.process.pid}).")
            if wait_for_ready:
                self.wait_until_ready(timeout_seconds)
            return

        cmd = self.build_command()
        logger.info(f"Starting ComfyUI daemon: {' '.join(cmd)}")

        stdout_dest = subprocess.DEVNULL
        stderr_dest = subprocess.DEVNULL

        if self.log_file:
            log_p = Path(self.log_file)
            log_p.parent.mkdir(parents=True, exist_ok=True)
            self._log_handle = open(log_p, "a", encoding="utf-8")
            stdout_dest = self._log_handle
            stderr_dest = self._log_handle

        try:
            # Create process with own process group for clean subtree termination
            if platform.system() == "Windows":
                creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
                self.process = subprocess.Popen(
                    cmd,
                    cwd=str(self.comfy_dir),
                    stdout=stdout_dest,
                    stderr=stderr_dest,
                    creationflags=creationflags,
                )
            else:
                self.process = subprocess.Popen(
                    cmd,
                    cwd=str(self.comfy_dir),
                    stdout=stdout_dest,
                    stderr=stderr_dest,
                    preexec_fn=os.setsid,
                )

            self._start_time = time.time()
            logger.info(f"ComfyUI daemon started with PID {self.process.pid}.")

            if wait_for_ready:
                self.wait_until_ready(timeout_seconds)

        except Exception as e:
            logger.error(f"Failed to launch ComfyUI daemon: {e}")
            self.stop()
            raise ComfyDaemonError(f"Could not start ComfyUI daemon: {e}") from e

    def stop(self, timeout_seconds: float = 10.0) -> None:
        """
        Gracefully terminates the ComfyUI process and its child processes,
        ensuring no orphan/zombie processes remain.
        """
        if self.process is None:
            return

        pid = self.process.pid
        logger.info(f"Stopping ComfyUI daemon (PID {pid})...")

        try:
            # Try terminating child processes via platform-specific tools if available
            if platform.system() == "Windows":
                # Use taskkill /T /F to cleanly kill the entire process tree on Windows
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(pid)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False,
                )
            else:
                # On Unix send SIGTERM to the process group
                try:
                    os.killpg(os.getpgid(pid), signal.SIGTERM)
                except Exception:
                    self.process.terminate()

            # Wait for exit
            try:
                self.process.wait(timeout=timeout_seconds)
            except subprocess.TimeoutExpired:
                logger.warning(f"Process {pid} did not exit in {timeout_seconds}s. Forcing kill.")
                if platform.system() == "Windows":
                    self.process.kill()
                else:
                    try:
                        os.killpg(os.getpgid(pid), signal.SIGKILL)
                    except Exception:
                        self.process.kill()
                self.process.wait(timeout=2.0)

        except Exception as e:
            logger.error(f"Error during ComfyUI process teardown: {e}")
        finally:
            self.process = None
            self._start_time = None
            if self._log_handle:
                try:
                    self._log_handle.close()
                except Exception:
                    pass
                self._log_handle = None
            logger.info("ComfyUI daemon stopped.")

    def restart(self, timeout_seconds: float = 10.0, wait_for_ready: bool = True) -> None:
        """Restarts the ComfyUI daemon process."""
        logger.info("Restarting ComfyUI daemon...")
        self.stop(timeout_seconds=timeout_seconds)
        self.start(wait_for_ready=wait_for_ready, timeout_seconds=timeout_seconds)

    def ping(self, timeout_seconds: float = 3.0) -> bool:
        """
        Sends an HTTP GET request to /system_stats to verify server health.
        """
        url = f"{self.base_url}/system_stats"
        try:
            with httpx.Client(timeout=timeout_seconds) as client:
                res = client.get(url)
                return res.status_code == 200
        except Exception:
            return False

    def get_system_stats(self, timeout_seconds: float = 5.0) -> Dict[str, Any]:
        """
        Fetches hardware utilization, VRAM stats, and system diagnostics from ComfyUI.
        """
        url = f"{self.base_url}/system_stats"
        try:
            with httpx.Client(timeout=timeout_seconds) as client:
                res = client.get(url)
                res.raise_for_status()
                return res.json()
        except Exception as e:
            raise ComfyDaemonError(f"Failed to fetch system stats from {url}: {e}") from e

    def wait_until_ready(self, timeout_seconds: float = 30.0, poll_interval: float = 0.5) -> bool:
        """
        Polls /system_stats until ComfyUI responds or timeout expires.
        """
        start = time.time()
        while time.time() - start < timeout_seconds:
            if self.process is not None and self.process.poll() is not None:
                raise ComfyDaemonError(
                    f"ComfyUI process exited prematurely with code {self.process.returncode}"
                )
            if self.ping(timeout_seconds=poll_interval):
                logger.info(f"ComfyUI server at {self.base_url} is ready.")
                return True
            time.sleep(poll_interval)

        raise TimeoutError(f"ComfyUI daemon failed to respond within {timeout_seconds} seconds.")

    def check_health(self, auto_recover: Optional[bool] = None) -> Dict[str, Any]:
        """
        Verifies health and optionally triggers auto-recovery if degraded.
        """
        should_recover = self.auto_restart if auto_recover is None else auto_recover
        alive = self.is_running()
        responsive = self.ping(timeout_seconds=2.0) if alive else False

        stats = None
        if responsive:
            try:
                stats = self.get_system_stats(timeout_seconds=2.0)
            except Exception:
                stats = None

        healthy = alive and responsive

        if not healthy and should_recover and self.main_py_path:
            logger.warning("ComfyUI daemon is unhealthy; initiating auto-recovery restart.")
            try:
                self.restart(wait_for_ready=False)
                alive = self.is_running()
            except Exception as e:
                logger.error(f"Auto-recovery restart failed: {e}")

        return {
            "healthy": healthy,
            "is_running": alive,
            "is_responsive": responsive,
            "pid": self.process.pid if self.process else None,
            "uptime_seconds": round(time.time() - self._start_time, 2) if self._start_time else 0.0,
            "system_stats": stats,
            "base_url": self.base_url,
        }

    def get_status(self) -> Dict[str, Any]:
        """Returns comprehensive status dictionary."""
        alive = self.is_running()
        return {
            "is_running": alive,
            "pid": self.process.pid if (self.process and alive) else None,
            "host": self.host,
            "port": self.port,
            "base_url": self.base_url,
            "ws_url": self.ws_url,
            "vram_mode": self.vram_mode,
            "gpu_device": self.gpu_device,
            "comfy_dir": str(self.comfy_dir) if self.comfy_dir else None,
            "uptime_seconds": round(time.time() - self._start_time, 2) if (self._start_time and alive) else 0.0,
        }

    def __enter__(self) -> "ComfyDaemonSupervisor":
        self.start(wait_for_ready=False)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()
