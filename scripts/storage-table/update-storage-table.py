#!/usr/bin/env python3
"""
update-storage-table.py
Purpose: Scan selected folders and write a CSV inventory of useful files.
Usage: python3 scripts/storage-table/update-storage-table.py [--dry-run]
Output: data/storage-table.csv
Risk level: read-only
"""

import argparse
import csv
import os
from datetime import datetime
from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def load_config(root: Path) -> dict:
    config = {}
    config_path = root / "config" / "paths.conf"
    if config_path.exists():
        with open(config_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    val = val.strip().strip('"')
                    val = os.path.expandvars(val)  # expand ${HOME} etc.
                    config[key.strip()] = val
        # Second pass: resolve ${KEY} references to other config values
        for _ in range(10):  # prevent infinite loops
            changed = False
            for key, val in config.items():
                for k, v in config.items():
                    placeholder = f"${{{k}}}"
                    if placeholder in val:
                        val = val.replace(placeholder, v)
                        changed = True
                config[key] = val
            if not changed:
                break
    return config


def scan_paths(paths: list[Path]) -> list[dict]:
    records = []
    record_id = 1
    for base_path in paths:
        if not base_path.exists():
            print(f"Warning: path does not exist: {base_path}")
            continue
        for path in sorted(base_path.rglob("*")):
            if path.is_file():
                stat = path.stat()
                records.append(
                    {
                        "id": record_id,
                        "filename": path.name,
                        "path": str(path),
                        "extension": path.suffix.lower(),
                        "size_bytes": stat.st_size,
                        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "category": guess_category(path),
                        "status": "active",
                        "notes": "",
                    }
                )
                record_id += 1
    return records


def guess_category(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in {".pdf"}:
        return "pdf"
    if ext in {".md", ".txt", ".rst"}:
        return "text"
    if ext in {".sh", ".py", ".js", ".pl", ".rb"}:
        return "script"
    if ext in {".csv", ".tsv"}:
        return "data"
    if ext in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
        return "image"
    if ext in {".mp4", ".mkv", ".avi", ".mov"}:
        return "video"
    if ext in {".zip", ".tar", ".gz", ".bz2", ".7z"}:
        return "archive"
    return "other"


def write_csv(records: list[dict], output_path: Path) -> None:
    fieldnames = [
        "id",
        "filename",
        "path",
        "extension",
        "size_bytes",
        "modified_at",
        "category",
        "status",
        "notes",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    print(f"Storage table written to {output_path} ({len(records)} files)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Update storage table CSV")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without writing")
    args = parser.parse_args()

    root = get_project_root()
    config = load_config(root)

    raw_paths = config.get("STORAGE_PATHS", "/home/mpc/Documents /home/mpc/Downloads /home/mpc/automation")
    paths = [Path(p) for p in raw_paths.split()]

    records = scan_paths(paths)

    if args.dry_run:
        print(f"Dry-run: would write {len(records)} records to {root / 'data' / 'storage-table.csv'}")
        for r in records[:5]:
            print(f"  - {r['path']} ({r['category']}, {r['size_bytes']} bytes)")
        if len(records) > 5:
            print(f"  ... and {len(records) - 5} more")
        return

    output_path = root / "data" / "storage-table.csv"
    write_csv(records, output_path)


if __name__ == "__main__":
    main()
