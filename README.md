# file‑checksum

**What it does**

`file-checksum` is a tiny, zero‑dependency Python script that computes the SHA‑256 checksum of any file you point at. It:

- Handles missing files, permission errors, and empty inputs gracefully.
- Guarantees idempotent output: if an output file already exists, it will not be overwritten unless you explicitly request it with `--force`.
- Uses clear, deterministic naming for output files (`<original‑name>.sha256`).
- Returns an appropriate exit code for scripting pipelines.

**Installation**

```bash
# Clone the repo (the system will check for name collisions before creating the repo)
git clone https://github.com/youruser/file-checksum.git
cd file-checksum
# No external packages required – just run with Python 3.8+
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

**Usage**

```bash
# Compute checksum for a single file
python checksum_tool.py path/to/file.txt

# Compute checksums for multiple files (wildcard expansion works in the shell)
python checksum_tool.py *.pdf

# Overwrite existing checksum files (use with care)
python checksum_tool.py --force data.bin
```

**Exit codes**

- `0` – All files processed successfully.
- `1` – One or more files could not be processed (e.g., not found, permission denied).
- `2` – Unexpected internal error (should never happen; see logs). 

**License**: MIT – see the repository's `LICENSE` file.

---

*Enjoy a reliable, collision‑free checksum generator!*