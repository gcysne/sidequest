#!/usr/bin/env python3
"""Validate knowledge/devices/**/device.yaml and the skill folders (run by CI; run it before opening a pull request)."""
import re, sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
errors = []
seen_rules = {}
for f in sorted((ROOT / "knowledge" / "devices").glob("**/device.yaml")):
    rel = f.parent.relative_to(ROOT / "knowledge" / "devices").as_posix()
    try:
        d = yaml.safe_load(f.read_text()) or {}
    except yaml.YAMLError as e:
        errors.append(f"{f}: invalid YAML: {e}"); continue
    for k in ("id", "name", "match", "maintainers"):
        if not d.get(k):
            errors.append(f"{rel}/device.yaml: missing '{k}'")
    if d.get("id") and d["id"] != rel:
        errors.append(f"{rel}/device.yaml: id '{d['id']}' must equal the folder path '{rel}'")
    if not re.fullmatch(r"[a-z0-9-]+/[a-z0-9-]+", rel):
        errors.append(f"{rel}: device folders are knowledge/devices/<vendor>/<model>, lower case with hyphens")
    if not (f.parent / "README.md").exists():
        errors.append(f"{rel}: README.md missing")
    for rule in d.get("match") or []:
        if not isinstance(rule, dict) or not rule:
            errors.append(f"{rel}: each match rule must be a non-empty mapping of DMI fields"); continue
        key = tuple(sorted((k, str(v).lower()) for k, v in rule.items()))
        if key in seen_rules:
            errors.append(f"{rel}: match rule {rule} duplicates {seen_rules[key]}")
        seen_rules[key] = rel
for s in sorted((ROOT / "skills").iterdir()):
    if not s.is_dir():
        continue
    sk = s / "SKILL.md"
    if not sk.exists():
        errors.append(f"skills/{s.name}: SKILL.md missing"); continue
    m = re.match(r"---\n(.*?)\n---\n", sk.read_text(), re.S)
    meta = yaml.safe_load(m.group(1)) if m else {}
    if not meta or meta.get("name") != s.name or not meta.get("description"):
        errors.append(f"skills/{s.name}/SKILL.md: front matter needs name: {s.name} and a description")
# Device, OS and stack knowledge lives under knowledge/ (moved there before 0.1.0): no paths to the old top-level
# folders outside it. Inside knowledge/, short relative paths (devices, os and stacks subfolders) are fine.
OLD_LAYOUT = re.compile(r"(?<![A-Za-z0-9_.\-])(?<!/sys/)(?<!knowledge/)(devices|os|stacks)/")
SKIP = {".git", "node_modules", "knowledge", "dist", "build"}
for f in sorted(ROOT.rglob("*")):
    rel = f.relative_to(ROOT)
    if not f.is_file() or SKIP & set(rel.parts) or f.suffix in (".png", ".jpg", ".onnx", ".zip", ".lock"):
        continue
    try:
        text = f.read_text()
    except (UnicodeDecodeError, OSError):
        continue
    for n, line in enumerate(text.splitlines(), 1):
        if OLD_LAYOUT.search(line):
            errors.append(f"{rel}:{n}: path to the old layout (use knowledge/devices/, knowledge/os/, knowledge/stacks/)")
print("\n".join(errors) or "devices, skills and knowledge paths OK")
sys.exit(1 if errors else 0)
