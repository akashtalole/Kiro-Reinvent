#!/usr/bin/env python3
"""Lint Agent Skills folders: name == folder, lowercase-hyphenated, <= 64 chars; description <= 1024 chars
and says when to use it; every relative link in SKILL.md exists; scripts compile.

  check_skills.py [skills_dir]   (default: .kiro/skills next to this lab)
"""
from __future__ import annotations

import py_compile
import re
import sys
from pathlib import Path

import yaml

NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def lint(skill_dir: Path) -> list[str]:
    errs = []
    md = skill_dir / "SKILL.md"
    if not md.exists():
        return [f"{skill_dir.name}: missing SKILL.md"]
    text = md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return [f"{skill_dir.name}: SKILL.md has no front matter"]
    meta = yaml.safe_load(text.split("---")[1]) or {}
    name, desc = str(meta.get("name", "")), str(meta.get("description", ""))
    if name != skill_dir.name:
        errs.append(f"{skill_dir.name}: name '{name}' must equal the folder name")
    if not NAME.match(name) or len(name) > 64:
        errs.append(f"{skill_dir.name}: name must be lowercase-hyphenated and <= 64 chars")
    if not desc or len(desc) > 1024:
        errs.append(f"{skill_dir.name}: description must be 1..1024 chars (is {len(desc)})")
    if "use when" not in desc.lower():
        errs.append(f"{skill_dir.name}: description should say when to use it ('Use when ...')")
    for link in re.findall(r"\]\(([^)#\s]+)\)", text):
        if not link.startswith(("http://", "https://")) and not (skill_dir / link).exists():
            errs.append(f"{skill_dir.name}: broken link {link}")
    for script in skill_dir.glob("scripts/*.py"):
        try:
            py_compile.compile(str(script), doraise=True)
        except py_compile.PyCompileError as e:
            errs.append(f"{skill_dir.name}: {script.name} does not compile: {e.msg}")
    return errs


if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / ".kiro" / "skills"
    dirs = sorted(p for p in root.iterdir() if p.is_dir())
    problems = [e for d in dirs for e in lint(d)]
    print("\n".join(problems) if problems else f"ok: {len(dirs)} skills pass")
    sys.exit(1 if problems else 0)
