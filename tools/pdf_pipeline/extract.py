"""Section extraction utilities for the Dark Sun parsing pipeline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Iterator, List, Sequence, Tuple

import fitz

from .models import Manifest, Section


def _iter_sections(
    sections: Sequence[Section],
    parent_chain: Tuple[str, ...] = (),
) -> Iterator[Tuple[Section, Tuple[str, ...]]]:
    for section in sections:
        chain = parent_chain + (section.slug,)
        yield section, parent_chain
        if section.children:
            yield from _iter_sections(section.children, chain)


def _serialize_blocks(blocks: Iterable[tuple]) -> List[dict]:
    serialized = []
    for block in blocks:
        if len(block) < 5:
            continue
        x0, y0, x1, y1, text = block[:5]
        attrs = {}
        if len(block) >= 6:
            attrs["number"] = block[5]
        if len(block) >= 7:
            attrs["type"] = block[6]
        serialized.append(
            {
                "bbox": [x0, y0, x1, y1],
                "text": text.strip(),
                **attrs,
            }
        )
    return serialized


def extract_sections(
    manifest: Manifest,
    *,
    output_dir: Path,
    min_level: int = 2,
    include_blocks: bool = True,
) -> List[Path]:
    """Extract section text (and blocks) according to a manifest."""

    output_dir = output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = Path(manifest.pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    written_files: List[Path] = []

    with fitz.open(pdf_path) as doc:
        for section, parents in _iter_sections(manifest.sections):
            if section.level < min_level:
                continue

            pages = []
            for page_number in section.page_span:
                page = doc[page_number - 1]
                page_entry = {
                    "page_number": page_number,
                    "text": page.get_text("text"),
                }
                if include_blocks:
                    page_entry["blocks"] = _serialize_blocks(page.get_text("blocks"))
                pages.append(page_entry)

            data = {
                "title": section.title,
                "slug": section.slug,
                "level": section.level,
                "start_page": section.start_page,
                "end_page": section.end_page,
                "parent_slugs": list(parents),
                "pages": pages,
            }

            filename = f"{section.level:02d}-{section.start_page:03d}-{section.slug}.json"
            output_path = output_dir / filename
            output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            written_files.append(output_path)

    return written_files

