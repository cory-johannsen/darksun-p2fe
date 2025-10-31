"""Utilities for generating and loading PDF manifests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

import fitz

from .models import Manifest, Section, TocEntry, slugify


def _normalize_toc(toc: Iterable[Iterable[int | str]]) -> List[TocEntry]:
    entries: List[TocEntry] = []
    for raw in toc:
        if len(raw) != 3:
            continue
        level, title, page = raw
        if not isinstance(level, int) or not isinstance(title, str) or not isinstance(page, int):
            continue
        entries.append(TocEntry(level=level, title=title.strip(), page=page))
    return entries


def _build_sections(entries: List[TocEntry], page_count: int) -> List[Section]:
    sections: List[Section] = []
    stack: List[Section] = []

    for idx, entry in enumerate(entries):
        next_page = entries[idx + 1].page if idx + 1 < len(entries) else page_count + 1
        section = Section(
            title=entry.title,
            level=entry.level,
            start_page=entry.page,
            end_page=max(entry.page, next_page - 1),
            slug=slugify(entry.title),
        )

        while stack and stack[-1].level >= section.level:
            stack.pop()

        if stack:
            stack[-1].children.append(section)
        else:
            sections.append(section)

        stack.append(section)

    def _propagate_end_pages(node: Section) -> None:
        for child in node.children:
            _propagate_end_pages(child)
        if node.children:
            node.end_page = max(node.end_page, node.children[-1].end_page)

    for section in sections:
        _propagate_end_pages(section)

    return sections


def generate_manifest(pdf_path: Path, output_path: Path | None = None) -> Manifest:
    """Create a manifest JSON that outlines the PDF structure."""

    pdf_path = pdf_path.expanduser().resolve()
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    with fitz.open(pdf_path) as doc:
        toc = _normalize_toc(doc.get_toc(simple=True))
        sections = _build_sections(toc, doc.page_count)
        manifest = Manifest(
            pdf_path=str(pdf_path),
            page_count=doc.page_count,
            sections=sections,
        )

    if output_path is not None:
        output_path = output_path.expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(manifest.model_dump(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    return manifest


def load_manifest(path: Path) -> Manifest:
    """Load a previously generated manifest JSON file."""

    data = json.loads(path.read_text(encoding="utf-8"))
    return Manifest.model_validate(data)

