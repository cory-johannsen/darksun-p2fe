"""Command-line hook for running the raw-to-processed transformation pipeline."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _add_repo_path() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profiles",
        type=Path,
        default=Path("data/mappings/section_profiles.json"),
        help="Path to the section profile configuration JSON.",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=Path("data/raw/sections"),
        help="Directory containing raw section JSON files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/processed"),
        help="Directory to write processed data artifacts.",
    )
    return parser.parse_args()


def main() -> None:
    _add_repo_path()

    from tools.pdf_pipeline.transform import transform_all

    args = parse_args()
    transform_all(
        section_profiles=args.profiles,
        raw_sections_dir=args.raw_dir,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()

