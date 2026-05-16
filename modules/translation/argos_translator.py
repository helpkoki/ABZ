"""
modules/translation/argos_translator.py
========================================
Translator module using Argos Translate — fully offline, no API key needed.
Smaller/faster than Ollama but less accurate for nuanced manga dialogue.

Install:
  pip install argostranslate
  Then download a language package once (see __init__ below).
"""

from __future__ import annotations
import logging

from core.interfaces import BaseTranslator

logger = logging.getLogger(__name__)


class ArgosTranslator(BaseTranslator):
    """
    Uses Argos Translate for fully-offline translation.
    Language packages must be installed once before use.

    Quick setup (run once in a Python shell):
        import argostranslate.package
        argostranslate.package.update_package_index()
        pkgs = argostranslate.package.get_available_packages()
        pkg = next(p for p in pkgs if p.from_code == "id" and p.to_code == "en")
        argostranslate.package.install_from_path(pkg.download())
    """

    def __init__(self, **kwargs):
        pass

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        if not text.strip():
            return text
        try:
            import argostranslate.translate
            return argostranslate.translate.translate(text, source_lang, target_lang)
        except Exception as e:
            logger.error(f"[Argos] Translation failed: {e}")
            return text
