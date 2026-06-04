#!/usr/bin/env python3
"""
register-scripts.py
Purpose: Scan the scripts/ folder and write a CSV registry of every automation script.
Usage: python3 scripts/script-registration/register-scripts.py
Output: data/script-registry.csv
Risk level: read-only
"""

import csv
import os
from datetime import datetime
from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def get_risk_level(filename: str) -> str:
    lower = filename.lower()
    if "delete" in lower or "remove" in lower or "rm -rf" in lower:
        return "dangerous"
    if "configure" in lower or "repair" in lower or "network-change" in lower:
        return "network-change"
    if "move" in lower or "archive" in lower:
        return "moves-files"
    if "write" in lower or "update" in lower or "convert" in lower:
        return "writes-report"
    if "check" in lower or "scan" in lower or "register" in lower:
        return "read-only"
    return "unknown"


def get_language(path: Path) -> str:
    ext = path.suffix.lower()
    return {
        ".sh": "bash",
        ".py": "python",
        ".js": "javascript",
        ".pl": "perl",
        ".rb": "ruby",
    }.get(ext, "unknown")


def scan_scripts(scripts_dir: Path) -> list[dict]:
    records = []
    for path in sorted(scripts_dir.rglob("*")):
        if path.is_file() and path.suffix in {".sh", ".py", ".js", ".pl", ".rb"}:
            rel_path = path.relative_to(scripts_dir.parent)
            stat = path.stat()
            records.append(
                {
                    "script_name": path.name,
                    "path": str(rel_path),
                    "language": get_language(path),
                    "purpose": "",
                    "risk_level": get_risk_level(path.name),
                    "inputs": "",
                    "outputs": "",
                    "run_command": f"./{rel_path}" if path.suffix == ".sh" else f"python3 {rel_path}",
                    "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                }
            )
    return records


def write_csv(records: list[dict], output_path: Path) -> None:
    fieldnames = [
        "script_name",
        "path",
        "language",
        "purpose",
        "risk_level",
        "inputs",
        "outputs",
        "run_command",
        "last_modified",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    print(f"Script registry written to {output_path} ({len(records)} scripts)")


def main() -> None:
    root = get_project_root()
    scripts_dir = root / "scripts"
    output_path = root / "data" / "script-registry.csv"
    records = scan_scripts(scripts_dir)
    write_csv(records, output_path)


if __name__ == "__main__":
    main()
