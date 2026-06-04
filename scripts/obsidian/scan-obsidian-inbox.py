#!/usr/bin/env python3
"""
scan-obsidian-inbox.py
Purpose: Scan the Obsidian inbox folder and report file types found.
Usage: python3 scripts/obsidian/scan-obsidian-inbox.py [--dry-run]
Output: logs/obsidian.log
Risk level: read-only
"""

import argparse
import os
from datetime import datetime
from pathlib import Path
from collections import Counter


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


def scan_inbox(inbox_path: Path, log_file: Path) -> dict:
    stats = Counter()
    files = []

    if not inbox_path.exists():
        write_log(log_file, "WARN", f"Inbox path does not exist: {inbox_path}")
        return {"stats": stats, "files": files}

    for path in sorted(inbox_path.rglob("*")):
        if path.is_file():
            ext = path.suffix.lower()
            stats[ext] += 1
            files.append(path)

    return {"stats": stats, "files": files}


def write_log(log_file: Path, level: str, message: str) -> None:
    ts = datetime.now().isoformat()
    line = f"[{ts}] [{level}] [scan-obsidian-inbox] {message}"
    print(line)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, "a") as f:
        f.write(line + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan Obsidian inbox")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without writing")
    args = parser.parse_args()

    root = get_project_root()
    config = load_config(root)
    inbox_path = Path(config.get("OBSIDIAN_INBOX", str(root / "inbox")))
    log_file = root / "logs" / "obsidian.log"

    write_log(log_file, "INFO", "START Scanning Obsidian inbox")
    write_log(log_file, "INFO", f"Inbox path: {inbox_path}")

    result = scan_inbox(inbox_path, log_file)
    stats = result["stats"]
    files = result["files"]

    write_log(log_file, "INFO", f"Found {len(files)} files in inbox")

    if stats:
        write_log(log_file, "INFO", "File type breakdown:")
        for ext, count in sorted(stats.items()):
            ext_label = ext if ext else "(no extension)"
            write_log(log_file, "INFO", f"  {ext_label}: {count}")
    else:
        write_log(log_file, "INFO", "No files found")

    if args.dry_run:
        write_log(log_file, "INFO", "Dry-run mode — no changes made")

    write_log(log_file, "INFO", "END Completed successfully")


if __name__ == "__main__":
    main()
