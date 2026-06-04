#!/usr/bin/env python3
"""
normalize_confidence.py
Purpose: Recalculate confidence scores using a soft-max style normalization
         across the batch, so scores reflect relative confidence rather than
         absolute self-reported numbers.
Usage:
    python3 scripts/ingestion/normalize_confidence.py [--dry-run]
Output: Updates sidecar frontmatter; logs/ingestion.log
Risk: writes-report
"""

import argparse
import json
import math
import os
import re
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
    line = f"[{ts}] [{level}] [normalize_confidence] {message}"
    print(line)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, "a") as f:
        f.write(line + "\n")


def softmax(scores: list[float]) -> list[float]:
    """Soft-max normalization. Maps raw scores to probabilities that sum to 1."""
    if not scores:
        return []
    exps = [math.exp(s) for s in scores]
    total = sum(exps)
    return [e / total for e in exps]


def sigmoid_scale(score: float, steepness: float = 5.0) -> float:
    """Sigmoid mapping that stretches mid-range scores more aggressively."""
    return 1.0 / (1.0 + math.exp(-steepness * (score - 0.5)))


def parse_frontmatter(path: Path) -> dict | None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
        if match:
            return json.loads(match.group(1))
    except Exception:
        pass
    return None


def write_frontmatter(path: Path, metadata: dict, body: str) -> None:
    yaml_text = json.dumps(metadata, indent=2)
    content = f"---\n{yaml_text}\n---\n{body}"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def extract_body(path: Path) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        match = re.search(r"^---\n.*?\n---(.*)", content, re.DOTALL)
        return match.group(1) if match else content
    except Exception:
        return ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize confidence scores in sidecars")
    parser.add_argument("--method", choices=["softmax", "sigmoid"], default="sigmoid", help="Normalization method")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    config = load_config()
    log_file = Path(config.get("LOGS_DIR", "/run/media/mpc/Expansion/_System_Snapshot_2026/Documents/LinuxBox-Vault/automation-scripts/logs")) / "ingestion.log"
    sidecars_dir = Path(config.get("INGESTION_SIDECARS", "/run/media/mpc/Expansion/_System_Snapshot_2026/Documents/LinuxBox-Vault/automation-scripts/sidecars"))

    write_log(log_file, "INFO", f"START Normalizing confidence ({args.method})")

    sidecars = list(sidecars_dir.glob("*.ai.md"))
    if len(sidecars) < 2:
        write_log(log_file, "INFO", "Not enough sidecars to normalize (need >= 2)")
        return

    # Gather raw scores
    raw_scores = []
    metadatas = []
    for sc in sidecars:
        md = parse_frontmatter(sc)
        if md:
            raw_scores.append(md.get("confidence", 0.5))
            metadatas.append((sc, md))

    if args.method == "softmax":
        new_scores = softmax(raw_scores)
    else:
        new_scores = [sigmoid_scale(s) for s in raw_scores]

    updated = 0
    for (sc, md), new_score in zip(metadatas, new_scores):
        old = md.get("confidence", 0.0)
        md["confidence"] = round(new_score, 3)
        md["confidence_method"] = args.method
        body = extract_body(sc)

        write_log(log_file, "INFO", f"{sc.name}: {old:.3f} -> {new_score:.3f}")

        if not args.dry_run:
            write_frontmatter(sc, md, body)
            updated += 1

    write_log(log_file, "INFO", f"Updated {updated} sidecars")
    write_log(log_file, "INFO", "END Normalization complete")


if __name__ == "__main__":
    main()
