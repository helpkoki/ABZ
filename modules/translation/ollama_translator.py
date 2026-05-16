"""
modules/translation/ollama_translator.py
=========================================
Translator module using Ollama (local LLM).
Requires Ollama running on your PC: https://ollama.com
And the model pulled:  ollama pull llama3.2

Install:  pip install requests
"""

from __future__ import annotations
import logging
import requests

from core.interfaces import BaseTranslator

logger = logging.getLogger(__name__)


class OllamaTranslator(BaseTranslator):
    """
    Sends each text string to a locally-running Ollama model for translation.

    Config options (translator_options in config.yaml):
      model    : Ollama model name, e.g. "llama3.2"
      base_url : Ollama server URL, default "http://localhost:11434"
      timeout  : request timeout in seconds
    """

    # Prompt designed to keep the LLM focused on translation only
    SYSTEM_PROMPT = (
        "You are a professional manga translator. "
        "Translate the given text to {target_lang}. "
        "Return ONLY the translated text — no explanations, no quotes, no extra words. "
        "Keep the tone natural for a manga/comic. "
        "If the text is already in {target_lang}, return it unchanged."
    )

    def __init__(
        self,
        model:    str = "llama3.2",
        base_url: str = "http://localhost:11434",
        timeout:  int = 30,
        **kwargs,
    ):
        self.model    = model
        self.base_url = base_url.rstrip("/")
        self.timeout  = timeout

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        if not text.strip():
            return text

        system = self.SYSTEM_PROMPT.format(target_lang=target_lang)
        user_prompt = f"Translate this manga text:\n\n{text}"

        payload = {
            "model": self.model,
            "prompt": user_prompt,
            "system": system,
            "stream": False,
        }

        try:
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            result = resp.json().get("response", "").strip()
            logger.debug(f"[Ollama] '{text}' → '{result}'")
            return result

        except requests.exceptions.ConnectionError:
            logger.error("[Ollama] Cannot connect. Is Ollama running? (ollama serve)")
            return text   # fall back to original text so pipeline doesn't crash
        except requests.exceptions.Timeout:
            logger.error(f"[Ollama] Request timed out after {self.timeout}s")
            return text
        except Exception as e:
            logger.error(f"[Ollama] Unexpected error: {e}")
            return text
