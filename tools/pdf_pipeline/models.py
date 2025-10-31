"""Shared data models used by the PDF parsing pipeline."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


def slugify(title: str) -> str:
    """Generate a filesystem-safe slug from a heading title."""

    keep = []
    for ch in title.lower():
        if ch.isalnum():
            keep.append(ch)
        elif ch in {" ", ":", "-", "_"}:
            keep.append("-")
    slug = "".join(keep).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "section"


class TocEntry(BaseModel):
    level: int
    title: str
    page: int = Field(..., ge=1)

    model_config = ConfigDict(extra="forbid")


class Section(BaseModel):
    title: str
    level: int
    start_page: int = Field(..., ge=1)
    end_page: int = Field(..., ge=1)
    slug: str
    children: List["Section"] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")

    @property
    def page_span(self) -> range:
        return range(self.start_page, self.end_page + 1)

    def find_child(self, title: str) -> Optional["Section"]:
        for child in self.children:
            if child.title == title:
                return child
        return None


class Manifest(BaseModel):
    pdf_path: str
    page_count: int
    sections: List[Section]

    model_config = ConfigDict(extra="forbid")

