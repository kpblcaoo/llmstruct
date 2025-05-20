import aiohttp
import json
import logging
import os
from pathlib import Path
import requests
from typing import Dict, Optional
from dotenv import load_dotenv
import toml

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class LLMClient:
    """Client for Grok, Anthropic, and Ollama APIs."""
    def __init__(self, config_path: str = "llmstruct.toml"):
        load_dotenv()
        self.config = self._load_config(config_path)
        self.grok_api_key = os.getenv("GROK_API_KEY", self.config.get("api", {}).get("grok_api_key"))
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", self.config.get("api", {}).get("anthropic_api_key"))
        self.ollama_host = self.config.get("api", {}).get("ollama_host", "http://localhost:11434")
        self.model = self.config.get("api", {}).get("model", "mixtral")
        self.retry_count = self.config.get("api", {}).get("retry_count", 3)

    def _load_config(self, config_path: str) -> Dict:
        """Load llmstruct.toml or return empty dict."""
        config_path = Path(config_path)
        if config_path.exists():
            try:
                with config_path.open("r", encoding="utf-8") as f:
                    return toml.load(f)
            except Exception as e:
                logging.error(f"Failed to load {config_path}: {e}")
        return {}

    async def _request_grok(self, prompt: str, context: Dict) -> Optional[str]:
        """Async request to Grok API."""
        headers = {"Authorization": f"Bearer {self.grok_api_key}", "Content-Type": "application/json"}
        payload = {"model": "grok-3", "prompt": prompt, "context": context}
        async with aiohttp.ClientSession() as session:
            for _ in range(self.retry_count):
                try:
                    async with session.post("https://api.x.ai/v1/chat", headers=headers, json=payload) as resp:
                        if resp.status == 200:
                            return await resp.text()
                        logging.warning(f"Grok API error: {resp.status}")
                except Exception as e:
                    logging.error(f"Grok API failed: {e}")
        return None

    async def _request_anthropic(self, prompt: str, context: Dict) -> Optional[str]:
        """Async request to Anthropic API."""
        headers = {"x-api-key": self.anthropic_api_key, "Content-Type": "application/json"}
        payload = {"model": "claude-3-opus-20240229", "prompt": prompt, "max_tokens": 1000, "context": context}
        async with aiohttp.ClientSession() as session:
            for _ in range(self.retry_count):
                try:
                    async with session.post("https://api.anthropic.com/v1/complete", headers=headers, json=payload) as resp:
                        if resp.status == 200:
                            return await resp.text()
                        logging.warning(f"Anthropic API error: {resp.status}")
                except Exception as e:
                    logging.error(f"Anthropic API failed: {e}")
        return None

    def _request_ollama(self, prompt: str, context: Dict) -> Optional[str]:
        """Sync request to local/remote Ollama."""
        payload = {"model": self.model, "prompt": prompt, "context": context}
        for _ in range(self.retry_count):
            try:
                resp = requests.post(f"{self.ollama_host}/api/generate", json=payload, timeout=30)
                if resp.status_code == 200:
                    return resp.text
                logging.warning(f"Ollama error: {resp.status_code}")
            except Exception as e:
                logging.error(f"Ollama failed: {e}")
        return None

    async def query(self, prompt: str, context_path: str = "context.json", mode: str = "hybrid") -> Optional[str]:
        """Query LLMs based on mode (grok, anthropic, ollama, hybrid)."""
        context = self._load_context(context_path)
        if mode == "hybrid":
            # Try local Ollama first, fall back to external
            result = self._request_ollama(prompt, context)
            if result:
                return result
            logging.info("Falling back to external LLM in hybrid mode")
            result = await self._request_grok(prompt, context) or await self._request_anthropic(prompt, context)
        elif mode == "grok":
            result = await self._request_grok(prompt, context)
        elif mode == "anthropic":
            result = await self._request_anthropic(prompt, context)
        elif mode == "ollama":
            result = self._request_ollama(prompt, context)
        else:
            logging.error(f"Invalid mode: {mode}")
            return None
        if not result:
            logging.error("All LLM requests failed")
        return result

    def _load_context(self, context_path: str) -> Dict:
        """Load context from JSON file."""
        context_path = Path(context_path)
        if context_path.exists():
            try:
                with context_path.open("r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Failed to load {context_path}: {e}")
        return {}

if __name__ == "__main__":
    import asyncio
    client = LLMClient()
    prompt = "Analyze struct.json for llmstruct project."
    result = asyncio.run(client.query(prompt, mode="hybrid"))
    if result:
        print(result)