"""
config.py
Purpose: Centralized configuration loading with caching.
Reads from config/paths.conf once and exposes typed accessors.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path


# ---------------------------------------------------------------------------
# Config Loading
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def load_config() -> dict[str, str]:
    """Load and cache configuration from paths.conf.

    Returns a dict of absolute paths. Cross-references like ${KEY}
    are resolved in a second pass.
    """
    config_path = Path("/run/media/mpc/Expansion/_System_Snapshot_2026/Documents/LinuxBox-Vault/automation-scripts/config/paths.conf")
    config: dict[str, str] = {}

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            val = val.strip().strip('"')
            val = os.path.expandvars(val)  # Expand ${HOME}
            config[key] = val

    # Resolve ${KEY} cross-references (up to 10 iterations to prevent infinite loops)
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


# ---------------------------------------------------------------------------
# Typed Accessors
# ---------------------------------------------------------------------------

def get_project_root() -> Path:
    return Path(load_config()["PROJECT_ROOT"])


def get_logs_dir() -> Path:
    return Path(load_config()["LOGS_DIR"])


def get_state_dir() -> Path:
    return Path(load_config()["STATE_DIR"])


def get_sidecars_dir() -> Path:
    return Path(load_config()["INGESTION_SIDECARS"])


def get_incoming_dir() -> Path:
    return Path(load_config()["INGESTION_INCOMING"])


def get_vault_path() -> Path:
    return Path(load_config()["OBSIDIAN_VAULT"])


def get_ollama_config() -> dict[str, str]:
    cfg = load_config()
    return {
        "host": cfg.get("OLLAMA_HOST", "http://127.0.0.1:11434"),
        "model": cfg.get("OLLAMA_MODEL", "qwen2.5-coder:7b"),
        "fallback": cfg.get("OLLAMA_FALLBACK_MODEL", "mistral"),
    }


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_WORDS_FOR_LLM = 6000
CONFIDENCE_THRESHOLD = 0.4
MAX_TITLE_LENGTH = 100
MAX_SUMMARY_LENGTH = 800
MAX_TAGS = 15
