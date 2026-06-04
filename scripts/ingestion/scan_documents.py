#!/usr/bin/env python3
"""
scan_documents.py
Purpose: Dry-run scanner for the document ingestion pipeline.
Usage:
    python3 scripts/ingestion/scan_documents.py --dry-run
    python3 scripts/ingestion/scan_documents.py --limit 50
    python3 scripts/ingestion/scan_documents.py --apply
Output: logs/ingestion.log, stdout candidate list
Risk:   read-only by default; writes state only with --apply
"""

import argparse
import json
import hashlib
import os
from datetime import datetime
from pathlib import Path
from collections import Counter


def load_config() -> dict:
    """Load absolute paths from config/paths.conf with env expansion."""
    config = {}
    config_path = Path("/run/media/mpc/Expansion/_System_Snapshot_2026/Documents/LinuxBox-Vault/automation-scripts/config/paths.conf")
    if config_path.exists():
        with open(config_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    val = val.strip().strip('"')
                    val = os.path.expandvars(val)
                    config[key.strip()] = val
        # Resolve ${KEY} cross-references
        for _ in range(10):
            changed = False
            for key, val in list(config.items()):
                for k, v in config.items():
                    placeholder = f"${{{k}}}"
                    if placeholder in val:
                        val = val.replace(placeholder, v)
                        changed = True
                config[key] = val
            if not changed:
                break
    return config


def load_state(state_path: Path) -> dict:
    if state_path.exists():
        with open(state_path) as f:
            return json.load(f)
    return {}


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
    except Exception:
        return ""
    return h.hexdigest()


def scan_incoming(incoming_path: Path, state: dict, limit: int, extensions: set[str]) -> list[Path]:
    candidates = []
    for path in sorted(incoming_path.rglob("*")):
        if not path.is_file():
            continue
        if extensions and path.suffix.lower() not in extensions:
            continue
        # Skip if already processed (by SHA256 or by path)
        sha = file_hash(path)
        if sha and sha in state.get("by_hash", {}):
            continue
        if str(path) in state.get("by_path", {}):
            continue
        candidates.append(path)
        if limit > 0 and len(candidates) >= limit:
            break
    return candidates


def write_log(log_file: Path, level: str, message: str) -> None:
    ts = datetime.now().isoformat()
    line = f"[{ts}] [{level}] [scan_documents] {message}"
    print(line)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, "a") as f:
        f.write(line + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan incoming documents for ingestion")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without writing")
    parser.add_argument("--apply", action="store_true", help="Write state and logs (default is dry-run)")
    parser.add_argument("--limit", type=int, default=50, help="Max files to select (0 = unlimited)")
    parser.add_argument("--exts", default=".txt,.md", help="Comma-separated file extensions to include")
    args = parser.parse_args()

    if not args.apply:
        args.dry_run = True

    config = load_config()
    incoming = Path(config.get("INGESTION_INCOMING", "/home/mpc/Documents/LinuxBox-Vault/automation-scripts/imported-text-files"))
    log_file = Path(config.get("LOGS_DIR", "/run/media/mpc/Expansion/_System_Snapshot_2026/Documents/LinuxBox-Vault/automation-scripts/logs")) / "ingestion.log"
    state_path = Path(config.get("STATE_DIR", "/run/media/mpc/Expansion/_System_Snapshot_2026/Documents/LinuxBox-Vault/automation-scripts/state")) / "processed-files.json"

    write_log(log_file, "INFO", "START Scanning incoming documents")
    write_log(log_file, "INFO", f"Incoming path: {incoming}")
    write_log(log_file, "INFO", f"Limit: {args.limit}, Extensions: {args.exts}")

    state = load_state(state_path)
    extensions = {e.strip().lower() for e in args.exts.split(",")}

    if not incoming.exists():
        write_log(log_file, "WARN", f"Incoming path does not exist: {incoming}")
        write_log(log_file, "INFO", "END Scan complete (no folder)")
        return

    # Count total files
    total = sum(1 for p in incoming.rglob("*") if p.is_file() and p.suffix.lower() in extensions)
    already_processed = len(state.get("by_hash", {}))
    write_log(log_file, "INFO", f"Total matching files: {total}, Already processed: {already_processed}")

    candidates = scan_incoming(incoming, state, args.limit, extensions)
    write_log(log_file, "INFO", f"Candidates selected: {len(candidates)}")

    if candidates:
        print(f"\n=== Next {len(candidates)} files to process ===")
        for i, path in enumerate(candidates, 1):
            size = path.stat().st_size
            print(f"  {i}. {path} ({size} bytes)")
    else:
        print("No new files to process.")

    if args.dry_run:
        write_log(log_file, "INFO", "Dry-run mode — no state changes")
        write_log(log_file, "INFO", "END Scan complete")
        return

    # Apply mode: update state with candidate hashes so they won't be picked next time
    # (they'll be marked as "queued" and later updated to "processed" by process_one_file.py)
    state.setdefault("by_hash", {})
    state.setdefault("by_path", {})
    for path in candidates:
        sha = file_hash(path)
        entry = {
            "source_path": str(path),
            "sha256": sha,
            "queued_at": datetime.now().isoformat(),
            "status": "queued",
        }
        state["by_hash"][sha] = entry
        state["by_path"][str(path)] = sha

    state_path.parent.mkdir(parents=True, exist_ok=True)
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)

    write_log(log_file, "INFO", f"State updated: {len(candidates)} files queued")
    write_log(log_file, "INFO", "END Scan complete")


if __name__ == "__main__":
    main()
