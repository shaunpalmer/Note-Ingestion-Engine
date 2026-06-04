# Local Automation Stack

A small, reliable automation system for a local Linux (Fedora/Ubuntu) setup.

## Goal

Turn the machine into a working assistant by using small, testable scripts that:
- Log every action clearly
- Organise files and Obsidian resources
- Support local AI / Ollama workflows
- Register scripts so we know what exists, what each does, and how to run it

## Structure

```
local-automation-stack/
├── README.md
├── config/
│   └── paths.conf
├── logs/
│   └── automation.log
├── reports/
├── data/
│   ├── script-registry.csv
│   ├── storage-table.csv
│   └── resource-inventory.csv
├── inbox/
├── archive/
├── review/
└── scripts/
    ├── runners/
    ├── log/
    ├── network/
    ├── obsidian/
    ├── storage-table/
    └── script-registration/
```

## Core Principles

1. **Single Responsibility** — Each script does one job only.
2. **Runner Scripts Chain Smaller Scripts** — A runner calls child scripts in order.
3. **Logs Tell the Truth** — Every script writes useful logs with timestamps.
4. **Never Delete Automatically** — Mark files for human review, do not delete.
5. **Dry-run First** — Any script that moves, renames, or modifies files supports `--dry-run`.

## Modules

| Module | Purpose |
|--------|---------|
| `log` | Reusable logging pattern all scripts can use |
| `network` | Read-only network status checks |
| `obsidian` | Scan inbox, convert text, prepare sidecar notes |
| `storage-table` | Inventory useful files into a CSV table |
| `script-registration` | Registry of every script: purpose, risk, how to run |

## Usage

Run a module script manually:

```bash
./scripts/log/write-log.sh INFO "my-script" "Something happened"
```

Inspect logs:

```bash
tail -f logs/automation.log
```

## Risk Levels

- `read-only` — No changes to files or system
- `writes-log` — Appends to log files only
- `writes-report` — Creates reports in `reports/`
- `moves-files` — Moves files between `inbox/`, `archive/`, `review/`
- `modifies-system` — Changes system config
- `network-change` — Alters routes or interfaces
- `dangerous` — Destructive operations (not used here)

## Design Mantra

> Scripts do tasks. Libraries hold reusable logic. The runner controls the workflow. Logs tell the truth. Reports make it readable. The human approves risky actions.
