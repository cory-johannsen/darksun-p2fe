"""Transformer that maps Dark Sun race sections to PF2E ancestry records."""

from __future__ import annotations

import re
from typing import Dict, Iterable, List, Tuple


def _normalize_text(pages: Iterable[dict]) -> str:
    chunks: List[str] = []
    for page in pages:
        text = page.get("text", "")
        text = text.replace("\r", "\n")
        # repair hyphenated line breaks
        text = re.sub(r"-\n\s*", "", text)
        chunks.append(text)
    combined = "\n".join(chunks)
    combined = re.sub(r"\n{3,}", "\n\n", combined)
    return combined


def _find_entity_windows(text: str, mapping: List[dict]) -> Dict[str, Tuple[int, int]]:
    aliases_map = {
        entity["name"]: {alias.lower() for alias in entity.get("aliases", []) + [entity["name"]]}
        for entity in mapping
    }
    heading_map = {entity["name"]: entity.get("heading") for entity in mapping}

    # Split text into paragraphs while keeping start indices
    paragraphs: List[Tuple[int, str]] = []
    cursor = 0
    for match in re.finditer(r"\n{2,}", text):
        chunk = text[cursor:match.start()]
        paragraphs.append((cursor, chunk))
        cursor = match.end()
    paragraphs.append((cursor, text[cursor:]))

    positions: List[Tuple[str, int]] = []
    found_names: set[str] = set()
    for start_idx, paragraph in paragraphs:
        lines = [line.strip() for line in paragraph.splitlines() if line.strip()]
        if not lines:
            continue
        heading = lines[0].lower()
        for name, aliases in aliases_map.items():
            target_heading = heading_map.get(name)
            if target_heading and heading == target_heading.lower():
                positions.append((name, start_idx))
                found_names.add(name)
                break
            if heading in aliases:
                positions.append((name, start_idx))
                found_names.add(name)
                break

    # Ensure every entity has a recorded position.
    text_lower = text.lower()

    def locate(alias: str | None) -> int | None:
        if not alias:
            return None
        alias_lower = alias.lower()
        candidates: List[int] = []
        for match in re.finditer(rf"\n{re.escape(alias_lower)}\n", text_lower):
            candidates.append(match.start() + 1)
        if not candidates:
            for match in re.finditer(rf"(?:^|\n){re.escape(alias_lower)}\b", text_lower):
                offset = 1 if match.group(0).startswith("\n") else 0
                candidates.append(match.start() + offset)
        if not candidates:
            match = re.search(rf"\b{re.escape(alias_lower)}\b", text_lower)
            if match:
                candidates.append(match.start())
        return min(candidates) if candidates else None

    for entity in mapping:
        name = entity["name"]
        if name in found_names:
            continue
        heading_hint = heading_map.get(name)
        aliases = entity.get("aliases", []) + [name]
        search_values = [heading_hint] + aliases if heading_hint else aliases
        entity_pos = None
        for alias in search_values:
            match_pos = locate(alias)
            if match_pos is not None:
                entity_pos = match_pos if entity_pos is None else min(entity_pos, match_pos)
                if heading_hint and alias == heading_hint:
                    break
        if entity_pos is not None:
            positions.append((name, entity_pos))

    positions.sort(key=lambda item: item[1])

    windows: Dict[str, Tuple[int, int]] = {}
    for idx, (name, start) in enumerate(positions):
        end = len(text)
        if idx + 1 < len(positions):
            end = positions[idx + 1][1]
        windows[name] = (start, end)

    return windows


ABILITY_MAP = {
    "str": "strength",
    "dex": "dexterity",
    "con": "constitution",
    "int": "intelligence",
    "wis": "wisdom",
    "cha": "charisma",
}


def _ability_boosts(mods: Dict[str, int]) -> List[str]:
    positives = sorted(
        ((score, value) for score, value in mods.items() if value > 0),
        key=lambda item: (-item[1], item[0]),
    )
    boosts = [ABILITY_MAP[score] for score, _ in positives[:2]]
    if len(boosts) < 2:
        boosts.append("free")
    elif len(boosts) == 2 and all(score != "free" for score in boosts):
        boosts.append("free")
    return boosts


def _ability_flaws(mods: Dict[str, int]) -> List[str]:
    negatives = [(score, value) for score, value in mods.items() if value < 0]
    if not negatives:
        return []
    min_penalty = min(value for _, value in negatives)
    flaws = [ABILITY_MAP[score] for score, value in negatives if value == min_penalty]
    return flaws


def transform(section_data: dict, config: dict) -> dict:
    pages = section_data.get("pages", [])
    text = _normalize_text(pages)
    entities = config.get("entities", [])

    windows = _find_entity_windows(text, entities)

    processed = []
    for entity in entities:
        name = entity["name"]
        ability_mods: Dict[str, int] = {
            key.lower(): value for key, value in entity.get("ability_mods", {}).items()
        }
        start, end = windows.get(name, (0, 0))
        excerpt = text[start:end].strip()
        description = re.sub(r"\s+", " ", excerpt)

        processed.append(
            {
                "name": name,
                "slug": entity.get("slug"),
                "source_section": section_data.get("title"),
                "source_pages": [section_data.get("start_page"), section_data.get("end_page")],
                "description": description,
                "pf2e": {
                    "size": entity.get("size", "medium"),
                    "hit_points": entity.get("hit_points", 8),
                    "speed": entity.get("speed", 25),
                    "languages": entity.get("languages", []),
                    "traits": entity.get("traits", []),
                    "boosts": _ability_boosts(ability_mods),
                    "flaws": _ability_flaws(ability_mods),
                    "ability_mods": ability_mods,
                    "heritages": entity.get("heritages", []),
                    "additional_features": entity.get("features", []),
                },
                "metadata": {
                    "aliases": entity.get("aliases", []),
                    "notes": entity.get("notes"),
                },
            }
        )

    return {"entities": processed, "entity_type": "ancestry"}

