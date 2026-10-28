#!/usr/bin/env python3
"""Validate devices/**/device.yaml and the skill folders (run by CI; run it before opening a pull request)."""
import re, sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
errors = []
seen_rules = {}
for f in sorted((ROOT / "devices").glob("**/device.yaml")):
    rel = f.parent.relative_to(ROOT / "devices").as_posix()
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
        errors.append(f"{rel}: device folders are devices/<vendor>/<model>, lower case with hyphens")
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
print("\n".join(errors) or "devices and skills OK")
sys.exit(1 if errors else 0)
