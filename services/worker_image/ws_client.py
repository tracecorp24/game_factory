"""
ComfyUI WebSocket Progress Listener and Live Telemetry Client.
Connects to ComfyUI's /ws endpoint to stream step progress (KSampler 14/25), node state transitions,
preview frames, and errors into CreativeForge EventEnvelope streams and SSE Outbox.
"""
from __future__ import annotations

import asyncio
import base64
import json
import logging
import struct
import threading
import time
import uuid
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from packages.contracts.events import EventEnvelope, EventType

logger = logging.getLogger("comfy_ws_client")


class ComfyWebSocketError(Exception):
    """Base exception for ComfyUI WebSocket listener errors."""
    pass


class ComfyWebSocketListener:
    """
    WebSocket client that connects to ComfyUI `/ws?clientId=<client_id>`,
    receives execution progress & previews, and converts them to CreativeForge EventEnvelope instances.
    """

    def __init__(
        self,
        base_ws_url: str = "ws://127.0.0.1:8188",
        client_id: Optional[str] = None,
        project_id: str = "proj_default",
        campaign_id: str = "camp_default",
        request_id: str = "req_default",
        run_id: str = "run_default",
        on_event: Optional[Callable[[EventEnvelope], None]] = None,
        on_progress: Optional[Callable[[int, int, float, str], None]] = None,
    ):
        self.base_ws_url = base_ws_url.rstrip("/")
        self.client_id = client_id or str(uuid.uuid4())
        self.project_id = project_id
        self.campaign_id = campaign_id
        self.request_id = request_id
        self.run_id = run_id

        self.on_event = on_event
        self.on_progress = on_progress

        self._run_seq = 0
        self._is_running = False
        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._stop_event: Optional[asyncio.Event] = None
        self.captured_events: List[EventEnvelope] = []
        self._completed_prompts: Dict[str, bool] = {}
        self._prompt_errors: Dict[str, str] = {}

    @property
    def ws_endpoint(self) -> str:
        return f"{self.base_ws_url}/ws?clientId={self.client_id}"

    def _next_seq(self) -> int:
        self._run_seq += 1
        return self._run_seq

    def parse_raw_message(self, raw_msg: Union[str, bytes]) -> Tuple[str, Dict[str, Any]]:
        """
        Parses a raw WebSocket message received from ComfyUI.
        Handles both text (JSON) and binary (previews) frames.
        """
        # Binary frame (Preview image: 8-byte header followed by image payload)
        if isinstance(raw_msg, bytes):
            if len(raw_msg) >= 8:
                event_type_int, image_type_int = struct.unpack(">II", raw_msg[:8])
                image_bytes = raw_msg[8:]
                img_format = "jpeg" if image_type_int == 1 else "png"
                b64_str = base64.b64encode(image_bytes).decode("ascii")
                data = {
                    "event_type_code": event_type_int,
                    "image_format": img_format,
                    "preview_base64": b64_str,
                    "bytes_length": len(image_bytes),
                }
                return "preview", data
            return "binary_unknown", {"bytes_length": len(raw_msg)}

        # JSON text frame
        try:
            parsed = json.loads(raw_msg)
            msg_type = parsed.get("type", "unknown")
            msg_data = parsed.get("data", {})
            return msg_type, msg_data
        except Exception as e:
            logger.warning(f"Failed to parse WebSocket JSON message: {e}")
            return "unknown", {"raw": str(raw_msg)}

    def transform_to_envelope(
        self,
        event_name: str,
        data: Dict[str, Any],
        run_id: Optional[str] = None,
    ) -> EventEnvelope:
        """
        Translates ComfyUI events into standardized CreativeForge EventEnvelope instances.
        """
        active_run_id = run_id or self.run_id
        seq = self._next_seq()

        if event_name == "progress":
            val = data.get("value", 0)
            max_val = data.get("max", 1)
            pct = round((val / max_val) * 100, 1) if max_val > 0 else 0.0
            node_id = str(data.get("node", ""))
            prompt_id = data.get("prompt_id")

            payload = {
                "prompt_id": prompt_id,
                "node_id": node_id,
                "step": val,
                "total_steps": max_val,
                "percentage": pct,
            }
            return EventEnvelope.create(
                event_type=EventType.COMFY_STEP_PROGRESS,
                project_id=self.project_id,
                campaign_id=self.campaign_id,
                request_id=self.request_id,
                run_id=active_run_id,
                run_seq=seq,
                payload_preview=payload,
                node_execution_id=node_id,
                actor_type="worker",
                actor_id=f"comfy_{self.client_id[:8]}",
            )

        elif event_name == "preview":
            payload = {
                "image_format": data.get("image_format", "jpeg"),
                "bytes_length": data.get("bytes_length", 0),
                "preview_base64": data.get("preview_base64", ""),
            }
            return EventEnvelope.create(
                event_type=EventType.COMFY_PREVIEW_FRAME,
                project_id=self.project_id,
                campaign_id=self.campaign_id,
                request_id=self.request_id,
                run_id=active_run_id,
                run_seq=seq,
                payload_preview=payload,
                actor_type="worker",
                actor_id=f"comfy_{self.client_id[:8]}",
            )

        elif event_name == "executing":
            node_id = data.get("node")
            prompt_id = data.get("prompt_id")
            if node_id is not None:
                payload = {
                    "prompt_id": prompt_id,
                    "node_id": str(node_id),
                    "status": "executing",
                }
                return EventEnvelope.create(
                    event_type=EventType.NODE_STARTED,
                    project_id=self.project_id,
                    campaign_id=self.campaign_id,
                    request_id=self.request_id,
                    run_id=active_run_id,
                    run_seq=seq,
                    payload_preview=payload,
                    node_execution_id=str(node_id),
                    actor_type="worker",
                )
            else:
                # node == None signifies that the entire workflow prompt execution is finished!
                payload = {
                    "prompt_id": prompt_id,
                    "status": "completed",
                }
                return EventEnvelope.create(
                    event_type=EventType.RUN_COMPLETED,
                    project_id=self.project_id,
                    campaign_id=self.campaign_id,
                    request_id=self.request_id,
                    run_id=active_run_id,
                    run_seq=seq,
                    payload_preview=payload,
                    actor_type="worker",
                )

        elif event_name == "executed":
            node_id = str(data.get("node", ""))
            prompt_id = data.get("prompt_id")
            payload = {
                "prompt_id": prompt_id,
                "node_id": node_id,
                "output": data.get("output", {}),
            }
            return EventEnvelope.create(
                event_type=EventType.NODE_FINISHED,
                project_id=self.project_id,
                campaign_id=self.campaign_id,
                request_id=self.request_id,
                run_id=active_run_id,
                run_seq=seq,
                payload_preview=payload,
                node_execution_id=node_id,
                actor_type="worker",
            )

        elif event_name == "execution_error":
            node_id = str(data.get("node_id", ""))
            prompt_id = data.get("prompt_id")
            exc_msg = data.get("exception_message", "Unknown error")
            payload = {
                "prompt_id": prompt_id,
                "node_id": node_id,
                "node_type": data.get("node_type", ""),
                "exception_message": exc_msg,
                "traceback": data.get("traceback", []),
            }
            return EventEnvelope.create(
                event_type=EventType.NODE_FAILED,
                project_id=self.project_id,
                campaign_id=self.campaign_id,
                request_id=self.request_id,
                run_id=active_run_id,
                run_seq=seq,
                payload_preview=payload,
                node_execution_id=node_id,
                actor_type="worker",
            )

        elif event_name == "execution_start":
            prompt_id = data.get("prompt_id")
            payload = {"prompt_id": prompt_id, "status": "started"}
            return EventEnvelope.create(
                event_type=EventType.RUN_STARTED,
                project_id=self.project_id,
                campaign_id=self.campaign_id,
                request_id=self.request_id,
                run_id=active_run_id,
                run_seq=seq,
                payload_preview=payload,
                actor_type="worker",
            )

        # Default fallback event
        payload = {"event_name": event_name, **data}
        return EventEnvelope.create(
            event_type=EventType.SETTINGS_CHANGED,
            project_id=self.project_id,
            campaign_id=self.campaign_id,
            request_id=self.request_id,
            run_id=active_run_id,
            run_seq=seq,
            payload_preview=payload,
            actor_type="worker",
        )

    def handle_message(self, raw_msg: Union[str, bytes]) -> EventEnvelope:
        """
        Parses raw message, constructs EventEnvelope, dispatches callbacks, and saves in buffer.
        """
        msg_type, msg_data = self.parse_raw_message(raw_msg)
        envelope = self.transform_to_envelope(msg_type, msg_data)
        self.captured_events.append(envelope)

        prompt_id = msg_data.get("prompt_id")

        if msg_type == "progress":
            val = msg_data.get("value", 0)
            max_val = msg_data.get("max", 1)
            pct = round((val / max_val) * 100, 1) if max_val > 0 else 0.0
            node_id = str(msg_data.get("node", ""))
            if self.on_progress:
                try:
                    self.on_progress(val, max_val, pct, node_id)
                except Exception as e:
                    logger.warning(f"Error in on_progress callback: {e}")

        elif msg_type == "executing" and msg_data.get("node") is None:
            if prompt_id:
                self._completed_prompts[prompt_id] = True

        elif msg_type == "execution_error":
            if prompt_id:
                self._prompt_errors[prompt_id] = msg_data.get("exception_message", "Unknown execution error")

        if self.on_event:
            try:
                self.on_event(envelope)
            except Exception as e:
                logger.warning(f"Error in on_event callback: {e}")

        return envelope

    async def listen_async(self, target_prompt_id: Optional[str] = None, timeout_seconds: float = 60.0) -> None:
        """
        Asynchronously connects to ComfyUI WebSocket endpoint and listens for incoming events.
        Terminates when target_prompt_id finishes, errors, or timeout expires.
        """
        try:
            import aiohttp
        except ImportError:
            raise ComfyWebSocketError("aiohttp is required for async WebSocket connection.")

        url = self.ws_endpoint
        logger.info(f"Connecting to ComfyUI WebSocket at {url}...")

        start_time = time.time()

        async with aiohttp.ClientSession() as session:
            try:
                async with session.ws_connect(url) as ws:
                    logger.info("Connected to ComfyUI WebSocket.")
                    while not ws.closed:
                        if time.time() - start_time > timeout_seconds:
                            raise TimeoutError(f"WebSocket session timed out after {timeout_seconds}s")

                        try:
                            msg = await asyncio.wait_for(ws.receive(), timeout=1.0)
                        except asyncio.TimeoutError:
                            continue

                        if msg.type == aiohttp.WSMsgType.TEXT:
                            envelope = self.handle_message(msg.data)
                        elif msg.type == aiohttp.WSMsgType.BINARY:
                            envelope = self.handle_message(msg.data)
                        elif msg.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                            break

                        if target_prompt_id:
                            if self._completed_prompts.get(target_prompt_id):
                                logger.info(f"Target prompt {target_prompt_id} completed execution.")
                                break
                            if target_prompt_id in self._prompt_errors:
                                err = self._prompt_errors[target_prompt_id]
                                raise ComfyWebSocketError(f"ComfyUI prompt execution failed: {err}")

            except Exception as e:
                logger.error(f"WebSocket connection error: {e}")
                raise

    def start_background(self, target_prompt_id: Optional[str] = None, timeout_seconds: float = 60.0) -> None:
        """
        Starts the WebSocket listener in a separate background thread.
        """
        def _run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self._loop = loop
            try:
                loop.run_until_complete(self.listen_async(target_prompt_id, timeout_seconds))
            except Exception as e:
                logger.debug(f"Background WebSocket listener finished: {e}")
            finally:
                loop.close()

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()

    def wait_completion(self, prompt_id: str, timeout_seconds: float = 60.0, poll_interval: float = 0.2) -> bool:
        """
        Blocks until the given prompt_id finishes, fails, or timeout occurs.
        """
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            if self._completed_prompts.get(prompt_id):
                return True
            if prompt_id in self._prompt_errors:
                raise ComfyWebSocketError(f"Prompt {prompt_id} execution error: {self._prompt_errors[prompt_id]}")
            time.sleep(poll_interval)

        raise TimeoutError(f"Timed out waiting for prompt {prompt_id} completion after {timeout_seconds}s")
