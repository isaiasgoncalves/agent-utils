#!/usr/bin/env python3
"""Validate an Obsidian course vault before handing it over.

Checks, in order of how badly each one burns a learner:

  1. Canvas JSON parses, edge endpoints exist, `file` nodes resolve to real notes
  2. Wikilinks resolve to an existing note (the top cause of lost trust)
  3. Orphan notes — written but linked from nowhere, so unreachable
  4. Remaining TODO stubs
  5. Thin notes that are probably unfinished
  6. Word counts per folder, so you can see where the substance actually is

Wikilinks inside fenced code blocks and inline code are ignored, because
`[[0.1] * 1024]` in a Python snippet is not a link.

Exit code 1 if anything in categories 1-2 fails; 0 otherwise (warnings don't fail).

Usage
-----
python validate_vault.py "C:/vaults/My Course"
python validate_vault.py ./course --min-words 120 --quiet
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

# Windows consoles default to cp1252, which cannot encode the box-drawing and
# emoji characters below (or accented folder names). Force UTF-8 so the report
# never dies on its own output.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):  # pragma: no cover - exotic stdio
        pass

SKIP_DIRS = {".obsidian", ".git", ".trash", "node_modules", "__pycache__", ".venv"}

FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
# [[Target]] | [[Target|alias]] | [[Target\|alias]] | [[Target#Heading]] | ![[Embed]]
WIKILINK_RE = re.compile(r"!?\[\[([^\]\[#|\\]+)")
FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)


def nested_repo_roots(vault: Path) -> set[Path]:
    """Directories that are their own git repo — source material dropped inside
    the vault. Their contents are not course notes and shouldn't be validated."""
    roots = set()
    for git in vault.rglob(".git"):
        if git.parent != vault:
            roots.add(git.parent)
    return roots


def iter_files(vault: Path, suffixes: tuple[str, ...], excluded: set[Path]):
    for p in sorted(vault.rglob("*")):
        if not (p.is_file() and p.suffix in suffixes):
            continue
        rel_parts = p.relative_to(vault).parts
        if any(part in SKIP_DIRS for part in rel_parts):
            continue
        if any(root in p.parents for root in excluded):
            continue
        yield p


def is_template(path: Path, vault: Path) -> bool:
    """Template notes legitimately contain placeholder links like [[ ]]."""
    return any(re.fullmatch(r"(\d+\s*-\s*)?templates?", part, re.I)
               for part in path.relative_to(vault).parts[:-1])


def strip_code(text: str) -> str:
    return INLINE_CODE_RE.sub("`", FENCE_RE.sub("", text))


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("vault", help="Path to the vault directory")
    ap.add_argument("--min-words", type=int, default=100,
                    help="Notes below this word count are flagged as thin (default: 100)")
    ap.add_argument("--quiet", action="store_true", help="Errors and warnings only")
    ap.add_argument("--exclude", nargs="*", default=[], metavar="GLOB",
                    help="Extra directories to skip (nested git repos are skipped "
                         "automatically)")
    args = ap.parse_args()

    vault = Path(args.vault).expanduser().resolve()
    if not vault.is_dir():
        print(f"error: not a directory: {vault}", file=sys.stderr)
        return 2

    excluded = nested_repo_roots(vault)
    for extra in args.exclude:
        excluded.update(q.resolve() for q in vault.glob(extra) if q.is_dir())

    md = list(iter_files(vault, (".md",), excluded))
    canvases = list(iter_files(vault, (".canvas",), excluded))
    if not md:
        print(f"error: no .md files found under {vault}", file=sys.stderr)
        return 2

    # Obsidian resolves links by basename anywhere in the vault, and also by
    # full relative path. Index both.
    by_name: dict[str, Path] = {}
    for p in md + canvases:
        by_name.setdefault(p.stem, p)
        by_name.setdefault(p.name, p)
        rel = p.relative_to(vault).as_posix()
        by_name.setdefault(rel, p)
        by_name.setdefault(rel.rsplit(".", 1)[0], p)

    errors: list[str] = []
    warnings: list[str] = []

    # ---- 1. canvases ------------------------------------------------------
    canvas_report = []
    for c in canvases:
        rel = c.relative_to(vault).as_posix()
        try:
            data = json.loads(read(c))
        except json.JSONDecodeError as e:
            errors.append(f"[canvas] {rel}: invalid JSON — {e}")
            continue

        nodes = data.get("nodes", [])
        edges = data.get("edges", [])
        ids = {n.get("id") for n in nodes}

        dupes = len(nodes) - len(ids)
        if dupes > 0:
            errors.append(f"[canvas] {rel}: {dupes} duplicate node id(s)")

        for e in edges:
            for side in ("fromNode", "toNode"):
                if e.get(side) not in ids:
                    errors.append(
                        f"[canvas] {rel}: edge {e.get('id','?')} → "
                        f"{side}={e.get(side)!r} does not exist")

        missing_files = 0
        for n in nodes:
            if n.get("type") == "file":
                target = (vault / n.get("file", "")).resolve()
                if not target.exists():
                    errors.append(f"[canvas] {rel}: file node → {n.get('file')!r} not found")
                    missing_files += 1
        canvas_report.append((rel, len(nodes), len(edges), missing_files))

    # ---- 2/3/4/5. notes ---------------------------------------------------
    linked_to: set[Path] = set()
    broken: dict[str, list[str]] = defaultdict(list)
    todos: list[str] = []
    thin: list[tuple[str, int]] = []
    words_by_folder: dict[str, int] = defaultdict(int)
    total_words = 0

    for p in md:
        rel = p.relative_to(vault).as_posix()
        folder = p.relative_to(vault).parts[0] if len(p.relative_to(vault).parts) > 1 else "."
        raw = read(p)
        body = FRONTMATTER_RE.sub("", raw)
        n_words = len(body.split())
        words_by_folder[folder] += n_words
        total_words += n_words

        if "TODO" in body and n_words < 60:
            todos.append(rel)
        elif n_words < args.min_words:
            thin.append((rel, n_words))

        template = is_template(p, vault)
        for target in WIKILINK_RE.findall(strip_code(raw)):
            t = target.strip()
            if not t:
                continue
            hit = by_name.get(t)
            if hit is None:
                if not template:  # placeholders in templates are intentional
                    broken[t].append(rel)
            else:
                linked_to.add(hit)

    for target, sources in sorted(broken.items()):
        shown = ", ".join(sorted(set(sources))[:3])
        more = f" (+{len(set(sources)) - 3} more)" if len(set(sources)) > 3 else ""
        errors.append(f"[link] [[{target}]] does not exist — referenced in {shown}{more}")

    orphans = [p.relative_to(vault).as_posix() for p in md
               if p not in linked_to and p.stem.lower() not in
               {"start here", "início do curso", "readme", "index"}]

    # ---- report -----------------------------------------------------------
    print(f"\n{'=' * 62}\n  VAULT: {vault.name}\n{'=' * 62}")
    print(f"  {len(md)} notes · {len(canvases)} canvases · {total_words:,} words")

    if not args.quiet and words_by_folder:
        print("\n  Words per folder")
        for folder, n in sorted(words_by_folder.items()):
            bar = "█" * max(1, round(28 * n / max(words_by_folder.values())))
            print(f"    {folder[:34]:<34} {n:>7,}  {bar}")

    if not args.quiet and canvas_report:
        print("\n  Canvases")
        for rel, n_nodes, n_edges, miss in canvas_report:
            flag = f"  ⚠ {miss} broken file node(s)" if miss else "  ok"
            print(f"    {rel[:44]:<44} {n_nodes:>3} nodes {n_edges:>3} edges{flag}")

    if errors:
        print(f"\n  ❌ ERRORS ({len(errors)})")
        for e in errors[:40]:
            print(f"    {e}")
        if len(errors) > 40:
            print(f"    ... and {len(errors) - 40} more")

    if todos:
        warnings.append(f"{len(todos)} note(s) still stubs: " + ", ".join(todos[:6])
                        + (" ..." if len(todos) > 6 else ""))
    if thin:
        warnings.append(f"{len(thin)} note(s) under {args.min_words} words: "
                        + ", ".join(f"{r} ({n}w)" for r, n in thin[:6])
                        + (" ..." if len(thin) > 6 else ""))
    if orphans:
        warnings.append(f"{len(orphans)} note(s) linked from nowhere: "
                        + ", ".join(orphans[:6]) + (" ..." if len(orphans) > 6 else ""))

    if warnings and not args.quiet:
        print(f"\n  ⚠️  WARNINGS ({len(warnings)})")
        for w in warnings:
            print(f"    {w}")

    if not errors:
        print("\n  ✅ No broken links or canvas errors.")
    print()
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
