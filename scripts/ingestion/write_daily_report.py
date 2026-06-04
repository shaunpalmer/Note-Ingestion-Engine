#!/usr/bin/env python3
"""
write_daily_report.py
Purpose: Generate a Markdown daily report from the ingestion logs and state file.
Usage:
    python3 scripts/ingestion/write_daily_report.py [--date YYYY-MM-DD]
Output: reports/YYYY-MM-DD-ingestion-report.md
Risk: writes-report
"""

import argparse
import json
import os
from datetime import datetime, date
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


def load_state(state_path: Path) -> dict:
    if state_path.exists():
        with open(state_path) as f:
            return json.load(f)
    return {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Write daily ingestion report")
    parser.add_argument("--date", default=date.today().isoformat(), help="Report date")
    args = parser.parse_args()

    config = load_config()
    state_path = Path(config.get("STATE_DIR", "/run/media/mpc/Expansion/_System_Snapshot_2026/Documents/LinuxBox-Vault/automation-scripts/state")) / "processed-files.json"
    reports_dir = Path(config.get("REPORTS_DIR", "/run/media/mpc/Expansion/_System_Snapshot_2026/Documents/LinuxBox-Vault/automation-scripts/reports"))
    model = config.get("OLLAMA_MODEL", "qwen2.5-coder:7b")

    state = load_state(state_path)
    entries = list(state.get("by_hash", {}).values())

    # Filter to report date
    report_date = args.date
    today_entries = [e for e in entries if e.get("processed_at", "").startswith(report_date)]

    processed = len(today_entries)
    successful = sum(1 for e in today_entries if e.get("status") == "processed")
    failed = processed - successful

    useful = [e for e in today_entries if e.get("value") == "useful"]
    permanent = [e for e in today_entries if e.get("value") == "permanent"]
    throwaway = [e for e in today_entries if e.get("value") == "throwaway"]

    report_path = reports_dir / f"{report_date}-ingestion-report.md"
    reports_dir.mkdir(parents=True, exist_ok=True)

    lines = [
        f"# Daily Ingestion Report — {report_date}",
        "",
        f"- **Processed:** {processed}",
        f"- **Successful:** {successful}",
        f"- **Failed:** {failed}",
        f"- **Model:** {model}",
        "",
        "## By Value",
        f"- **Useful:** {len(useful)}",
        f"- **Permanent:** {len(permanent)}",
        f"- **Throwaway:** {len(throwaway)}",
        "",
        "## Useful Files",
    ]
    for e in useful:
        name = Path(e.get("source_path", "unknown")).name
        lines.append(f"- [[{name}]] — {e.get('confidence', 0)} confidence")

    if permanent:
        lines.append("")
        lines.append("## Permanent / Reference")
        for e in permanent:
            name = Path(e.get("source_path", "unknown")).name
            lines.append(f"- [[{name}]]")

    if throwaway:
        lines.append("")
        lines.append("## Throwaway / Archive Candidates")
        for e in throwaway:
            name = Path(e.get("source_path", "unknown")).name
            lines.append(f"- {name}")

    lines.append("")
    lines.append("---")
    lines.append(f"*Report generated at {datetime.now().isoformat()}*")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Report written: {report_path}")


if __name__ == "__main__":
    main()
