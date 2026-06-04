#!/usr/bin/env python3
"""
route_to_vault.py
Purpose: Read an .ai.md sidecar, extract metadata, and copy both original + sidecar
         to the correct Obsidian vault subfolder based on AI classification.
Usage:
    python3 scripts/ingestion/route_to_vault.py <sidecar_path> [--dry-run]
Output: Files copied to vault; logs/ingestion.log
Risk: moves-files (copies, does not delete originals)
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
    line = f"[{ts}] [{level}] [route_to_vault] {message}"
    print(line)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, "a") as f:
        f.write(line + "\n")


def parse_frontmatter(sidecar_path: Path) -> dict:
    """Extract the JSON frontmatter from an .ai.md file."""
    try:
        with open(sidecar_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Find content between --- lines
        match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
        if match:
            return json.loads(match.group(1))
    except Exception:
        pass
    return {}


def determine_folder(metadata: dict, vault_base: Path) -> Path:
    """Map AI metadata to vault folder."""
    tags = [t.lower() for t in metadata.get("tags", [])]
    value = metadata.get("value", "")
    confidence = metadata.get("confidence", 0.0)

    # Business category routing based on tags
    business_tags = {
        "agency": ["agency", "client", "project", "contract", "invoice", "proposal"],
        "marketing": ["marketing", "seo", "social", "campaign", "lead", "advertising", "branding"],
        "data": ["data", "database", "csv", "spreadsheet", "analysis", "report", "cleaning"],
        "programming": ["python", "script", "code", "automation", "linux", "programming", "api", "docker"],
        "personal": ["personal", "family", "health", "finance", "house", "travel"],
    }

    for category, keywords in business_tags.items():
        if any(kw in tags for kw in keywords):
            return vault_base / category

    # Fallback based on value
    if value == "permanent":
        return vault_base / "reference"
    if value == "throwaway" or confidence < 0.4:
        return vault_base / "archive"

    return vault_base / "inbox"


def main() -> None:
    parser = argparse.ArgumentParser(description="Route processed files to Obsidian vault")
    parser.add_argument("sidecar_path", help="Path to the .ai.md sidecar file")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without copying")
    args = parser.parse_args()

    config = load_config()
    log_file = Path(config.get("LOGS_DIR", "/run/media/mpc/Expansion/_System_Snapshot_2026/Documents/LinuxBox-Vault/automation-scripts/logs")) / "ingestion.log"
    vault_base = Path(config.get("OBSIDIAN_VAULT", "/home/mpc/Documents/LinuxBox-Vault"))

    sidecar = Path(args.sidecar_path)
    if not sidecar.exists():
        write_log(log_file, "ERROR", f"Sidecar not found: {sidecar}")
        sys.exit(1)

    metadata = parse_frontmatter(sidecar)
    if not metadata:
        write_log(log_file, "ERROR", f"Could not parse frontmatter: {sidecar}")
        sys.exit(1)

    source_file = Path(metadata.get("source_file", ""))
    if not source_file.exists():
        write_log(log_file, "WARN", f"Original file missing: {source_file}")
        # Continue anyway; we can still route the sidecar

    target_folder = determine_folder(metadata, vault_base)
    write_log(log_file, "INFO", f"Routing to: {target_folder}")
    write_log(log_file, "INFO", f"Tags: {metadata.get('tags', [])}, Value: {metadata.get('value')}, Confidence: {metadata.get('confidence')}")

    if args.dry_run:
        write_log(log_file, "INFO", "Dry-run: would copy files to vault")
        print(f"  Original: {source_file} -> {target_folder / source_file.name}")
        print(f"  Sidecar:  {sidecar} -> {target_folder / sidecar.name}")
        return

    target_folder.mkdir(parents=True, exist_ok=True)

    if source_file.exists():
        shutil.copy2(source_file, target_folder / source_file.name)
        write_log(log_file, "INFO", f"Copied original: {source_file.name}")

    shutil.copy2(sidecar, target_folder / sidecar.name)
    write_log(log_file, "INFO", f"Copied sidecar: {sidecar.name}")
    write_log(log_file, "INFO", "Routing complete")


if __name__ == "__main__":
    main()
