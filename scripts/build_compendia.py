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
        "--journals-dir",
        type=Path,
        default=Path("data/processed/journals"),
        help="Directory containing processed journal JSON files.",
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

    from tools.pdf_pipeline import build_ancestry_pack, build_journal_pack

    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    ancestry_output = args.output_dir / "dark-sun-ancestries.db"
    build_ancestry_pack(args.ancestries, ancestry_output)

    if args.journals_dir.exists():
        journal_output = args.output_dir / "dark-sun-rules.db"
        build_journal_pack(args.journals_dir, journal_output)
    else:
        print(f"Warning: Journal directory {args.journals_dir} does not exist; skipping journal pack.")


if __name__ == "__main__":
    main()

