import asyncio
import json
import logging
import os
from pathlib import Path
from typing import List, Optional

import aiohttp
from dotenv import load_dotenv

try:
    if not load_dotenv():
        logging.warning("No .env file found or failed to parse .env")
except Exception as e:
    logging.error(f"Failed to parse .env file: {e}")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("docs/hybrid_log.md", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)


class LLMClient:
    def __init__(self, ollama_host: str = None):
        """Initialize LLMClient with optional Ollama host."""
        self.grok_api_key = os.getenv("GROK_API_KEY")
        logging.info(f"Grok API key: {self.grok_api_key}")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.ollama_host = ollama_host or os.getenv(
            "OLLAMA_HOST", "http://localhost:11434"
        )
        self.retry_count = int(os.getenv("RETRY_COUNT", 3))

    async def query(
        self,
        prompt: str,
        context_path: str = None,
        mode: str = "hybrid",
        model: Optional[str] = None,
        artifact_ids: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Query LLMs with prompt, context, and optional model."""
        logging.info(f"Querying in {mode} mode with prompt: {prompt}")

        # Load context from file if provided
        context = {}
        if context_path and Path(context_path).exists():
            try:
                with Path(context_path).open("r", encoding="utf-8") as f:
                    context = json.load(f)
            except Exception as e:
                logging.error(f"Failed to load context from {context_path}: {e}")
                return None

        # Handle artifact_ids
        artifact_context = ""
        if artifact_ids:
            artifact_context = f"Artifacts included: {', '.join(artifact_ids)}"

        # Combine prompt with context
        full_prompt = f"{prompt}\n\nContext:\n{json.dumps(context, indent=2)}\n{artifact_context}".strip()

        # Select query method based on mode
        for attempt in range(self.retry_count):
            try:
                if mode == "grok":
                    return await self._query_grok(full_prompt)
                elif mode == "anthropic":
                    return await self._query_anthropic(full_prompt)
                elif mode == "ollama":
                    return await self._query_ollama(full_prompt, model or "mixtral")
                elif mode == "hybrid":
                    return await self._query_hybrid(full_prompt, model)
                else:
                    logging.error(f"Unsupported mode: {mode}")
                    return None
            except Exception as e:
                logging.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == self.retry_count - 1:
                    logging.error("All retries failed")
                    return None
                await asyncio.sleep(1)

    async def _query_grok(self, prompt: str) -> Optional[str]:
        """Query Grok API."""
        if not self.grok_api_key:
            logging.error("GROK_API_KEY not set")
            return None
        url = "https://api.x.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.grok_api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "grok-3",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4096,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    logging.info("Grok query successful")
                    return (
                        result.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "")
                    )
                else:
                    logging.error(f"Grok API error: {response.status}")
                    return None

    async def _query_anthropic(self, prompt: str) -> Optional[str]:
        """Query Anthropic API."""
        if not self.anthropic_api_key:
            logging.error("ANTHROPIC_API_KEY not set")
            return None
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        data = {
            "model": "claude-3-opus-20240229",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4096,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    logging.info("Anthropic query successful")
                    return result.get("content", [{}])[0].get("text", "")
                else:
                    logging.error(f"Anthropic API error: {response.status}")
                    return None

    async def _query_ollama(self, prompt: str, model: str) -> Optional[str]:
        """Query Ollama API with specified model."""
        url = f"{self.ollama_host.rstrip('/')}/api/generate"
        data = {"model": model, "prompt": prompt, "stream": False}
        async with aiohttp.ClientSession() as session:
            logging.debug(f"Sending request to Ollama: url={url}, data={data}")
            async with session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    logging.info(f"Ollama query successful with model {model}")
                    return result.get("response", "")
                else:
                    logging.error(f"Ollama API error: {response.status}")
                    return None

    async def _query_hybrid(
        self, prompt: str, model: Optional[str] = None
    ) -> Optional[str]:
        """Query multiple LLMs and combine results."""
        tasks = [
            self._query_grok(prompt),
            self._query_anthropic(prompt),
            self._query_ollama(prompt, model or "mixtral"),
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        valid_results = [r for r in results if r and not isinstance(r, Exception)]
        logging.info(
            f"Hybrid query completed with {len(valid_results)} valid responses"
        )
        return "\n".join(valid_results) if valid_results else None
