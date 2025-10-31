"""Generate Foundry VTT compendium packs from processed datasets."""

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
        "--ancestries",
        type=Path,
        default=Path("data/processed/ancestries.json"),
        help="Processed ancestry dataset to convert.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("packs"),
        help="Directory to write compendium pack files.",
    )
    return parser.parse_args()


def main() -> None:
    _add_repo_path()

    from tools.pdf_pipeline import build_ancestry_pack

    args = parse_args()
    output_path = args.output_dir / "dark-sun-ancestries.db"
    build_ancestry_pack(args.ancestries, output_path)


if __name__ == "__main__":
    main()

