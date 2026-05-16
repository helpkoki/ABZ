"""
modules/translation/deepl_translator.py
========================================
Translator module using the DeepL API.
Requires a (free-tier) API key from https://www.deepl.com/pro-api

Install:  pip install deepl
"""

from __future__ import annotations
import logging

from core.interfaces import BaseTranslator

logger = logging.getLogger(__name__)


class DeepLTranslator(BaseTranslator):
    """
    Uses the official DeepL Python SDK.

    Config options:
      api_key : your DeepL API key (free tier: 500k chars/month)
    """

    def __init__(self, api_key: str = "", **kwargs):
        self.api_key = api_key
        self._client = None

    def _get_client(self):
        if self._client is None:
            import deepl
            self._client = deepl.Translator(self.api_key)
        return self._client

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        if not text.strip():
            return text
        try:
            client = self._get_client()
            src = None if source_lang == "auto" else source_lang.upper()
            result = client.translate_text(text, source_lang=src, target_lang=target_lang.upper())
            return result.text
        except Exception as e:
            logger.error(f"[DeepL] Translation failed: {e}")
            return text
