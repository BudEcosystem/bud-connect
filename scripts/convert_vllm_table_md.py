#!/usr/bin/env python3
import json
import re
import sys
from typing import Any, Dict, List


# --- Helpers ---
LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
BACKTICK_RE = re.compile(r"`([^`]*)`")
CHECKS = {"✅︎", " ", "  ", ""}


def clean_cell(s: str) -> str:
    """Clean markdown formatting from table cell."""
    s = s.strip()
    # Strip markdown links -> keep link text
    s = LINK_RE.sub(r"\1", s)
    # Strip backticks
    s = BACKTICK_RE.sub(r"\1", s)
    # Remove trailing "etc." artifacts
    s = re.sub(r"\betc\.\s*$", "", s, flags=re.IGNORECASE).strip()
    return s


def is_divider(line: str) -> bool:
    """Check if line is a markdown table divider."""
    # e.g., |-----|-----| or :---:
    core = line.strip().strip("|").strip()
    if not core:
        return False
    return all(set(part.strip()) <= set("-:") and part.strip() for part in core.split("|"))


def split_row(line: str) -> List[str]:
    """Split markdown table row into cells."""
    # Split markdown row while keeping empty cells
    parts = [p.strip() for p in line.strip().strip("|").split("|")]
    return parts


def to_bool(cell: str) -> bool:
    """Convert cell content to boolean based on check marks."""
    cell = cell.strip()
    return cell in CHECKS if cell else False


def parse_examples(cell: str) -> List[str]:
    """Parse comma-separated example list from cell."""
    cell = clean_cell(cell)
    if not cell:
        return []
    # Split by comma, trim each, drop empties, strip trailing etc.
    parts = [re.sub(r"\betc\.?$", "", p.strip(), flags=re.IGNORECASE).strip() for p in cell.split(",")]
    return [p for p in parts if p]


# --- Read input ---
data = sys.stdin.read()

# Collect lines that look like table rows
lines = [ln for ln in data.splitlines() if "|" in ln.strip()]

if not lines:
    print("[]")
    sys.exit(0)

# Find header row (first non-divider with pipes)
header = None
body_lines = []
for i, ln in enumerate(lines):
    if is_divider(ln):
        continue
    header = ln
    # next line should be divider; skip it if present
    body_lines = lines[i + 2 :] if i + 1 < len(lines) and is_divider(lines[i + 1]) else lines[i + 1 :]
    break

# Normalize headers
if header is None:
    print("[]")
    sys.exit(0)

raw_headers = [clean_cell(h) for h in split_row(header)]
# Map/standardize expected header names
header_map = {}
for h in raw_headers:
    key = h
    # Normalize a few known variants
    key = key.replace("Example HF Models", "examples")
    key = key.replace("Architecture", "architecture")
    key = key.replace("Models", "models")
    key = key.replace("LoRA", "lora")
    key = key.replace("PP", "pp")
    header_map[h] = key

rows = []
for ln in body_lines:
    if not ln.strip():
        continue
    if is_divider(ln):
        continue
    cells = split_row(ln)
    # Skip if row is clearly not matching header width
    if len(cells) < len(raw_headers):
        # pad missing cells
        cells += [""] * (len(raw_headers) - len(cells))
    elif len(cells) > len(raw_headers):
        # collapse extras into last cell
        cells = cells[: len(raw_headers) - 1] + [" | ".join(cells[len(raw_headers) - 1 :])]

    obj: Dict[str, Any] = {}
    for h, c in zip(raw_headers, cells):
        key = header_map[h]
        val = clean_cell(c)
        if key == "lora" or key == "pp":
            obj[key] = to_bool(val)
        elif key == "examples":
            obj[key] = parse_examples(val)
        else:
            obj[key] = val
    rows.append(obj)

print(json.dumps(rows, ensure_ascii=False, indent=2))
