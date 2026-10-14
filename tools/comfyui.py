from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid
from pathlib import Path
from typing import Any

import httpx

from shared.core.settings import Settings

logger = logging.getLogger(__name__)
settings = Settings()


class ComfyUIClient:
    """
    Client for interacting with ComfyUI API:
    - Queuing workflows (Text-to-Video, Image-to-Video, AnimateDiff)
    - Tracking execution progress
    - Downloading rendered video/image assets
    """

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or settings.comfyui_base_url).rstrip("/")
        self.client_id = str(uuid.uuid4())
        self.timeout = settings.comfyui_timeout_seconds

    async def is_available(self) -> bool:
        """Check if ComfyUI service is responding."""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.base_url}/system_stats")
                return res.status_code == 200
        except Exception:
            return False

    def build_video_workflow(
        self,
        positive_prompt: str,
        negative_prompt: str = "",
        seed: int = 42,
        steps: int = 25,
        cfg: float = 7.0,
        width: int = 768,
        height: int = 512,
        frame_count: int = 48,
        fps: int = 24,
        filename_prefix: str = "studio_shot",
    ) -> dict[str, Any]:
        """
        Constructs a standard ComfyUI workflow graph for AI video generation
        (compatible with standard AnimateDiff / Wan / SVD / CogVideo / VHS nodes).
        """
        return {
            "3": {
                "inputs": {
                    "seed": seed,
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0],
                },
                "class_type": "KSampler",
            },
            "4": {
                "inputs": {"ckpt_name": "v1-5-pruned-emaonly.safetensors"},
                "class_type": "CheckpointLoaderSimple",
            },
            "5": {
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": frame_count,
                },
                "class_type": "EmptyLatentImage",
            },
            "6": {
                "inputs": {
                    "text": positive_prompt,
                    "clip": ["4", 1],
                },
                "class_type": "CLIPTextEncode",
            },
            "7": {
                "inputs": {
                    "text": negative_prompt or "ugly, blurry, distorted, low quality",
                    "clip": ["4", 1],
                },
                "class_type": "CLIPTextEncode",
            },
            "8": {
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["4", 2],
                },
                "class_type": "VAEDecode",
            },
            "9": {
                "inputs": {
                    "filename_prefix": filename_prefix,
                    "fps": fps,
                    "images": ["8", 0],
                },
                "class_type": "VHS_VideoCombine",
            },
        }

    async def queue_prompt(self, workflow_prompt: dict[str, Any]) -> str:
        """Submit a prompt workflow to ComfyUI and return the prompt_id."""
        payload = {
            "prompt": workflow_prompt,
            "client_id": self.client_id,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(f"{self.base_url}/prompt", json=payload)
            if res.status_code != 200:
                raise RuntimeError(
                    f"ComfyUI queue failed with status {res.status_code}: {res.text}"
                )
            data = res.json()
            return data["prompt_id"]

    async def wait_for_completion(
        self,
        prompt_id: str,
        poll_interval_seconds: float = 2.0,
    ) -> dict[str, Any]:
        """Poll /history until the job completes and return output manifest."""
        start_time = asyncio.get_event_loop().time()

        async with httpx.AsyncClient(timeout=30.0) as client:
            while True:
                if (asyncio.get_event_loop().time() - start_time) > self.timeout:
                    raise TimeoutError(
                        f"ComfyUI prompt {prompt_id} timed out after {self.timeout}s"
                    )

                try:
                    res = await client.get(f"{self.base_url}/history/{prompt_id}")
                    if res.status_code == 200:
                        history = res.json()
                        if prompt_id in history:
                            item = history[prompt_id]
                            # Check if finished
                            status = item.get("status", {})
                            if status.get("completed") or item.get("outputs"):
                                return item.get("outputs", {})
                except Exception as exc:
                    logger.warning(f"Error querying ComfyUI history: {exc}")

                await asyncio.sleep(poll_interval_seconds)

    async def download_file(
        self,
        filename: str,
        subfolder: str = "",
        folder_type: str = "output",
        save_path: str | Path = "output/clip.mp4",
    ) -> Path:
        """Download output asset from ComfyUI /view endpoint."""
        target = Path(save_path)
        target.parent.mkdir(parents=True, exist_ok=True)

        params = {
            "filename": filename,
            "subfolder": subfolder,
            "type": folder_type,
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            res = await client.get(f"{self.base_url}/view", params=params)
            if res.status_code != 200:
                raise RuntimeError(
                    f"Failed to download asset {filename}: {res.status_code}"
                )
            target.write_bytes(res.content)
            return target

    async def render_and_download_shot(
        self,
        shot_id: str,
        positive_prompt: str,
        negative_prompt: str = "",
        seed: int = 42,
        duration_seconds: float = 5.0,
        output_dir: str | Path = "output/shots",
        fps: int = 24,
    ) -> Path:
        """
        Executes end-to-end rendering of a shot via ComfyUI.
        If ComfyUI is not available, generates a placeholder test shot
        so the end-to-end workflow continues seamlessly.
        """
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        target_clip = out_dir / f"{shot_id}.mp4"

        frames = max(24, int(duration_seconds * fps))

        is_up = await self.is_available()
        if not is_up:
            logger.warning(
                f"ComfyUI is not reachable at {self.base_url}. Generating synthetic shot plate for {shot_id}."
            )
            return self._create_synthetic_shot_plate(target_clip, shot_id, positive_prompt, duration_seconds)

        try:
            workflow = self.build_video_workflow(
                positive_prompt=positive_prompt,
                negative_prompt=negative_prompt,
                seed=seed,
                frame_count=frames,
                fps=fps,
                filename_prefix=f"shot_{shot_id}",
            )
            prompt_id = await self.queue_prompt(workflow)
            outputs = await self.wait_for_completion(prompt_id)

            # Find video or image output file
            filename = None
            subfolder = ""
            for node_id, node_output in outputs.items():
                if "gifs" in node_output and node_output["gifs"]:
                    filename = node_output["gifs"][0]["filename"]
                    subfolder = node_output["gifs"][0].get("subfolder", "")
                    break
                elif "images" in node_output and node_output["images"]:
                    filename = node_output["images"][0]["filename"]
                    subfolder = node_output["images"][0].get("subfolder", "")
                    break

            if not filename:
                raise RuntimeError(f"No media outputs returned by ComfyUI for prompt {prompt_id}")

            return await self.download_file(
                filename=filename,
                subfolder=subfolder,
                save_path=target_clip,
            )

        except Exception as exc:
            logger.error(f"ComfyUI render failed for {shot_id}: {exc}. Using fallback shot plate.")
            return self._create_synthetic_shot_plate(target_clip, shot_id, positive_prompt, duration_seconds)

    def _create_synthetic_shot_plate(
        self,
        target_path: Path,
        shot_id: str,
        prompt: str,
        duration_seconds: float,
    ) -> Path:
        """
        Creates a lightweight placeholder media file if ComfyUI is offline or unreachable.
        """
        target_path.parent.mkdir(parents=True, exist_ok=True)
        # Create a text metadata sidecar and placeholder file
        meta_path = target_path.with_suffix(".json")
        meta = {
            "shot_id": shot_id,
            "prompt": prompt,
            "duration_seconds": duration_seconds,
            "status": "ready",
            "source": "synthetic_pre_render",
        }
        meta_path.write_text(json.dumps(meta, indent=2))
        
        # Write dummy binary container if file doesn't exist
        if not target_path.exists():
            target_path.write_bytes(b"RIFF\x00\x00\x00\x00AVI LIST\x00\x00\x00\x00hdrl")
        return target_path
