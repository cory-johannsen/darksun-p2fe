"""Run automated checks against processed Dark Sun datasets."""

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
        help="Path to the processed ancestry dataset.",
    )
    parser.add_argument(
        "--journals-dir",
        type=Path,
        default=Path("data/processed/journals"),
        help="Directory containing processed journal entries.",
    )
    return parser.parse_args()


def main() -> None:
    _add_repo_path()

    from tools.pdf_pipeline.validators import validate_ancestries, validate_journals

    args = parse_args()
    issues = []
    issues.extend(validate_ancestries(args.ancestries))
    issues.extend(validate_journals(args.journals_dir))
    if issues:
        print("Validation issues detected:")
        for issue in issues:
            print(f" - {issue}")
        sys.exit(1)
    print("All datasets passed validation.")


if __name__ == "__main__":
    main()

