"""Command-line entry point for extracting structured text from the Dark Sun PDF."""

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
        "--pdf",
        type=Path,
        default=Path("tsr02400_-_ADD_Setting_-_Dark_Sun_Box_Set_Original.pdf"),
        help="Path to the source PDF.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("data/raw/pdf_manifest.json"),
        help="Where to write/read the manifest JSON.",
    )
    parser.add_argument(
        "--sections-dir",
        type=Path,
        default=Path("data/raw/sections"),
        help="Directory to write extracted section JSON files.",
    )
    parser.add_argument(
        "--min-level",
        type=int,
        default=2,
        help="Minimum TOC level to extract (default: 2).",
    )
    parser.add_argument(
        "--force-manifest",
        action="store_true",
        help="Regenerate the manifest even if it already exists.",
    )
    parser.add_argument(
        "--skip-extract",
        action="store_true",
        help="Only generate the manifest without extracting sections.",
    )
    return parser.parse_args()


def main() -> None:
    _add_repo_path()

    from tools.pdf_pipeline import extract_sections, generate_manifest, load_manifest

    args = parse_args()

    manifest_path = args.manifest
    if manifest_path.exists() and not args.force_manifest:
        manifest = load_manifest(manifest_path)
    else:
        manifest = generate_manifest(args.pdf, manifest_path)

    if args.skip_extract:
        return

    extract_sections(
        manifest,
        output_dir=args.sections_dir,
        min_level=args.min_level,
    )


if __name__ == "__main__":
    main()

