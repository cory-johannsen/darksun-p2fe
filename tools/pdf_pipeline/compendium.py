"""Utilities for turning processed data into Foundry VTT compendia."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Iterable, List


def _paragraphs_to_html(paragraphs: Iterable[str]) -> str:
    blocks: List[str] = []
    for paragraph in paragraphs:
        text = paragraph.strip()
        if not text:
            continue
        blocks.append(f"<p>{text}</p>")
    return "\n".join(blocks)


def _description_to_html(description: str) -> str:
    chunks = [chunk.strip() for chunk in description.split("\n")]
    paragraphs: List[str] = []
    buffer: List[str] = []
    for line in chunks:
        if not line:
            if buffer:
                paragraphs.append(" ".join(buffer))
                buffer = []
            continue
        buffer.append(line)
    if buffer:
        paragraphs.append(" ".join(buffer))
    return _paragraphs_to_html(paragraphs)


def _build_boosts(boosts: List[str]) -> dict:
    entries = {}
    for idx, boost_value in enumerate(boosts):
        entries[str(idx)] = {"value": [boost_value] if boost_value != "free" else ["free"]}
    return entries


def _build_flaws(flaws: List[str]) -> dict:
    return {str(idx): {"value": [flaw]} for idx, flaw in enumerate(flaws)}


def build_ancestry_pack(processed_path: Path, output_path: Path) -> Path:
    """Create a Foundry-ready ancestry pack from processed ancestry data."""

    processed = json.loads(processed_path.read_text(encoding="utf-8"))
    entities = processed.get("data", {}).get("entities", [])

    entries = []
    for entity in entities:
        pf2e = entity.get("pf2e", {})
        description_html = _description_to_html(entity.get("description", ""))
        boosts = pf2e.get("boosts", [])
        flaws = pf2e.get("flaws", [])

        entry = {
            "_id": uuid.uuid4().hex,
            "name": entity["name"],
            "type": "ancestry",
            "img": "systems/pf2e/icons/default-icons/ancestry.svg",
            "system": {
                "description": {"value": description_html},
                "hp": pf2e.get("hit_points", 8),
                "size": {"value": pf2e.get("size", "medium")},
                "reach": {"value": 5},
                "speed": {"value": pf2e.get("speed", 25), "otherSpeeds": []},
                "boosts": _build_boosts(boosts),
                "flaws": _build_flaws(flaws),
                "languages": {
                    "value": pf2e.get("languages", []),
                    "custom": "",
                },
                "traits": {
                    "value": pf2e.get("traits", []),
                    "rarity": "uncommon",
                    "custom": "",
                },
                "vision": {"value": "normal"},
                "heritages": pf2e.get("heritages", []),
                "additionalFeatures": pf2e.get("additional_features", []),
            },
            "effects": [],
            "flags": {},
            "source": {"value": entity.get("source_section", "Dark Sun")},
        }
        entries.append(entry)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "\n".join(json.dumps(entry, ensure_ascii=False) for entry in entries),
        encoding="utf-8",
    )
    return output_path
