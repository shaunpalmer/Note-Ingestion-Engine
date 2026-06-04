#!/usr/bin/env python3
"""
archive_low_value.py
Purpose: Scan sidecars and archive files with low confidence or throwaway value.
Usage:
    python3 scripts/ingestion/archive_low_value.py [--dry-run] [--confidence-threshold 0.4]
Output: logs/ingestion.log
Risk: moves-files (copies to archive/, does not delete originals)
"""

import argparse
import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path


def load_config() -> dict:
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


def write_log(log_file: Path, level: str, message: str) -> None:
    ts = datetime.now().isoformat()
    line = f"[{ts}] [{level}] [archive_low_value] {message}"
    print(line)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, "a") as f:
        f.write(line + "\n")


def parse_frontmatter(sidecar_path: Path) -> dict:
    try:
        with open(sidecar_path, "r", encoding="utf-8") as f:
            content = f.read()
        match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
        if match:
            return json.loads(match.group(1))
    except Exception:
        pass
    return {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Archive low-value sidecars")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--confidence-threshold", type=float, default=0.4, help="Archive if confidence below this")
    args = parser.parse_args()

    config = load_config()
    log_file = Path(config.get("LOGS_DIR", "/run/media/mpc/Expansion/_System_Snapshot_2026/Documents/LinuxBox-Vault/automation-scripts/logs")) / "ingestion.log"
    sidecars_dir = Path(config.get("INGESTION_SIDECARS", "/run/media/mpc/Expansion/_System_Snapshot_2026/Documents/LinuxBox-Vault/automation-scripts/sidecars"))
    archive_dir = Path(config.get("ARCHIVE_DIR", "/run/media/mpc/Expansion/_System_Snapshot_2026/Documents/LinuxBox-Vault/automation-scripts/archive"))

    write_log(log_file, "INFO", "START Archiving low-value sidecars")

    archived = 0
    for sidecar in sorted(sidecars_dir.glob("*.ai.md")):
        metadata = parse_frontmatter(sidecar)
        if not metadata:
            continue

        value = metadata.get("value", "")
        confidence = metadata.get("confidence", 1.0)

        should_archive = (value == "throwaway") or (confidence < args.confidence_threshold)

        if should_archive:
            write_log(log_file, "INFO", f"Archiving {sidecar.name} (value={value}, confidence={confidence})")
            if args.dry_run:
                print(f"  Dry-run: would archive {sidecar.name}")
                continue

            archive_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(sidecar, archive_dir / sidecar.name)
            archived += 1

    write_log(log_file, "INFO", f"Archived {archived} files")
    write_log(log_file, "INFO", "END Archive complete")


if __name__ == "__main__":
    main()
