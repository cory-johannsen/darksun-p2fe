"""Transformer that converts raw section text into a journal-style document."""

from __future__ import annotations

import re
from typing import Iterable, List


def _normalize_text(pages: Iterable[dict]) -> str:
    chunks: List[str] = []
    for page in pages:
        text = page.get("text", "")
        text = text.replace("\r", "\n")
        text = re.sub(r"-\n\s*", "", text)
        chunks.append(text)
    combined = "\n".join(chunks)
    combined = re.sub(r"\n{3,}", "\n\n", combined)
    return combined.strip()


def _to_html(text: str) -> str:
    paragraphs = [para.strip() for para in re.split(r"\n{2,}", text) if para.strip()]
    if not paragraphs:
        return "<p></p>"
    return "\n".join(f"<p>{para}</p>" for para in paragraphs)


def transform(section_data: dict, config: dict | None = None) -> dict:
    config = config or {}
    pages = section_data.get("pages", [])
    text = _normalize_text(pages)
    html = _to_html(text)

    return {
        "entity_type": "journal",
        "slug": section_data.get("slug"),
        "title": section_data.get("title"),
        "content": html,
        "source_pages": [section_data.get("start_page"), section_data.get("end_page")],
        "metadata": {
            "parent_slugs": section_data.get("parent_slugs", []),
            "level": section_data.get("level"),
        },
    }

