#!/usr/bin/env python3
"""file-checksum – compute SHA‑256 digests for files.

Features aligned with TopherBot's preferences:
- Robust error handling (FileNotFound, PermissionError, etc.)
- Idempotent output: does not clobber existing *.sha256 files unless ``--force`` is used.
- Clear naming: output file is ``<input>.sha256``.
- Detailed, machine‑readable exit codes.
"""

import argparse
import hashlib
import os
import sys
from pathlib import Path

# ----------- Constants (clear naming) -----------
OUTPUT_SUFFIX = ".sha256"
EXIT_SUCCESS = 0
EXIT_PARTIAL_FAILURE = 1
EXIT_UNEXPECTED = 2

# ----------- Helper functions -----------
def compute_sha256(file_path: Path) -> str:
    """Return the hex SHA‑256 digest of *file_path*.

    Reads the file in 64 KiB chunks to stay memory‑efficient.
    Raises ``FileNotFoundError`` or ``PermissionError`` as appropriate.
    """
    hasher = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def write_digest(output_path: Path, digest: str, force: bool) -> None:
    """Write *digest* to *output_path*.

    If the file exists and ``force`` is ``False``, the function raises
    ``FileExistsError`` to avoid silent overwrites (preventing name collisions).
    """
    if output_path.exists() and not force:
        raise FileExistsError(f"Output file '{output_path}' already exists. Use --force to overwrite.")
    # Use ``write_text`` which creates the file atomically on most platforms.
    output_path.write_text(digest + "\n", encoding="utf-8")


def process_file(input_path: Path, *, force: bool) -> int:
    """Process a single file and return an exit‑code indicator.

    Returns ``0`` on success, ``1`` on recoverable error, ``2`` on unexpected error.
    """
    try:
        if not input_path.is_file():
            raise FileNotFoundError(f"'{input_path}' is not a regular file.")
        digest = compute_sha256(input_path)
        output_path = input_path.with_name(input_path.name + OUTPUT_SUFFIX)
        write_digest(output_path, digest, force)
        print(f"{input_path} -> {output_path}")
        return EXIT_SUCCESS
    except (FileNotFoundError, PermissionError) as e:
        print(f"Error processing '{input_path}': {e}", file=sys.stderr)
        return EXIT_PARTIAL_FAILURE
    except FileExistsError as e:
        print(f"Collision error: {e}", file=sys.stderr)
        return EXIT_PARTIAL_FAILURE
    except Exception as e:  # Catch‑all for unexpected bugs – we log and return a distinct code.
        print(f"Unexpected error on '{input_path}': {e}", file=sys.stderr)
        return EXIT_UNEXPECTED

# ----------- Main entry point -----------
def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="file-checksum",
        description="Compute SHA‑256 checksums for files with idempotent output and robust error handling.",
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="One or more paths to files whose checksum will be calculated.",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Overwrite existing *.sha256 files (use with caution).",
    )
    args = parser.parse_args(argv)

    overall_status = EXIT_SUCCESS
    for path_str in args.files:
        path = Path(path_str).expanduser().resolve()
        status = process_file(path, force=args.force)
        if status == EXIT_UNEXPECTED:
            overall_status = EXIT_UNEXPECTED
            break  # Fatal – abort further processing.
        elif status == EXIT_PARTIAL_FAILURE and overall_status != EXIT_UNEXPECTED:
            overall_status = EXIT_PARTIAL_FAILURE
    sys.exit(overall_status)


if __name__ == "__main__":
    main()
