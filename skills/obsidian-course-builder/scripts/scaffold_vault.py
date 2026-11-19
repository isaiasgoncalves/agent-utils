#!/usr/bin/env python3
"""Scaffold an Obsidian course vault: folders + stub notes with correct frontmatter.

The point is to get the mechanical part out of the way in one command so the
effort goes into the writing. Every stub carries a TODO marker; validate_vault.py
reports how many are left, which doubles as a progress indicator.

Examples
--------
python scaffold_vault.py "C:/vaults/PyTorch Course" \\
    --modules "Tensors and autograd" "Building models" "Training loops" \\
    --lang pt

python scaffold_vault.py ./ml-course --modules A B C --lessons 4 --no-crosscutting
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

# Windows consoles default to cp1252 and choke on accented vault names.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):  # pragma: no cover
        pass

# --------------------------------------------------------------------------- #
# Localised section titles. Add a language by adding a key.
# --------------------------------------------------------------------------- #
STRINGS = {
    "pt": {
        "start": "00 - Comece Aqui",
        "cross": "08 - Transversais",
        "refs": "90 - Referências",
        "concepts": "91 - Conceitos",
        "canvas": "93 - Canvas",
        "templates": "99 - Templates",
        "module": "Modulo",
        "overview": "Visão Geral",
        "lab": "Laboratório",
        "lesson": "Aula",
        "start_notes": [
            "Início do Curso",
            "Como usar este vault",
            "Setup da Máquina",
            "Plano de Estudos",
            "Trilha Visual do Curso",
            "Glossário",
        ],
        "cross_notes": [
            "Arquitetura - Princípios e Padrões",
            "Bugs Conhecidos do Material",
            "Estratégia de Testes",
            "Avaliação e Métricas",
            "Do Laptop para Produção",
        ],
        "ref_notes": ["Índice de Ferramentas", "Links Externos Selecionados"],
        "canvas_notes": ["Índice de Canvas"],
        "template_notes": ["Template - Nota de Estudo"],
        "todo": "> [!warning] TODO\n> Nota ainda não escrita.",
    },
    "en": {
        "start": "00 - Start Here",
        "cross": "08 - Cross-cutting",
        "refs": "90 - References",
        "concepts": "91 - Concepts",
        "canvas": "93 - Canvas",
        "templates": "99 - Templates",
        "module": "Module",
        "overview": "Overview",
        "lab": "Lab",
        "lesson": "Lesson",
        "start_notes": [
            "Start Here",
            "How to Use This Vault",
            "Machine Setup",
            "Study Plan",
            "Visual Course Map",
            "Glossary",
        ],
        "cross_notes": [
            "Architecture - Principles and Patterns",
            "Known Bugs in the Source",
            "Testing Strategy",
            "Evaluation and Metrics",
            "From Laptop to Production",
        ],
        "ref_notes": ["Tool Index", "Curated External Links"],
        "canvas_notes": ["Canvas Index"],
        "template_notes": ["Study Note Template"],
        "todo": "> [!warning] TODO\n> Note not written yet.",
    },
}

# Windows forbids these in filenames; Obsidian dislikes '#', '^', '[', ']', '|' in links.
_ILLEGAL = re.compile(r'[<>:"/\\|?*#^\[\]]')


def safe_filename(name: str) -> str:
    """Strip characters that break Windows paths or Obsidian wikilinks."""
    cleaned = _ILLEGAL.sub("", name).strip().rstrip(".")
    return re.sub(r"\s+", " ", cleaned) or "untitled"


def slugify(name: str) -> str:
    """ASCII kebab-case, for tags."""
    norm = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", norm.lower()).strip("-") or "course"


def write(path: Path, body: str, force: bool) -> bool:
    """Write a note unless it already exists. Returns True if written."""
    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return True


def note(tags: list[str], title: str, todo: str, extra_fm: dict | None = None) -> str:
    fm = ["---", f"tags: [{', '.join(tags)}]"]
    for k, v in (extra_fm or {}).items():
        fm.append(f"{k}: {json.dumps(v) if isinstance(v, str) else str(v).lower()}")
    fm.append("---")
    return "\n".join(fm) + f"\n\n# {title}\n\n{todo}\n"


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Scaffold an Obsidian course vault.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("vault", help="Path to the vault directory (created if missing)")
    ap.add_argument("--modules", nargs="+", required=True,
                    help="Module names, in learning order")
    ap.add_argument("--lessons", type=int, default=4,
                    help="Lesson stubs per module (default: 4)")
    ap.add_argument("--lang", default="pt", choices=sorted(STRINGS),
                    help="Language for folder and note names (default: pt)")
    ap.add_argument("--slug", default=None,
                    help="Tag slug; derived from the vault folder name if omitted")
    ap.add_argument("--no-crosscutting", action="store_true",
                    help="Skip the cross-cutting notes folder")
    ap.add_argument("--force", action="store_true",
                    help="Overwrite existing notes (default: skip them)")
    args = ap.parse_args()

    if not 1 <= args.lessons <= 12:
        print("error: --lessons must be between 1 and 12", file=sys.stderr)
        return 2
    if len(args.modules) > 20:
        print("error: more than 20 modules is almost certainly two courses",
              file=sys.stderr)
        return 2

    s = STRINGS[args.lang]
    vault = Path(args.vault).expanduser().resolve()
    slug = args.slug or slugify(vault.name)
    tag = f"course/{slug}"
    todo = s["todo"]

    created, skipped = 0, 0

    def emit(path: Path, body: str) -> None:
        nonlocal created, skipped
        if write(path, body, args.force):
            created += 1
        else:
            skipped += 1

    # --- fixed folders -----------------------------------------------------
    for key, notes, kind in (
        ("start", s["start_notes"], "moc"),
        ("refs", s["ref_notes"], "reference"),
        ("canvas", s["canvas_notes"], "moc"),
        ("templates", s["template_notes"], "template"),
    ):
        for n in notes:
            emit(vault / s[key] / f"{safe_filename(n)}.md",
                 note([tag, kind], n, todo))

    if not args.no_crosscutting:
        for n in s["cross_notes"]:
            emit(vault / s["cross"] / f"{safe_filename(n)}.md",
                 note([tag, "cross-cutting"], n, todo))

    (vault / s["concepts"]).mkdir(parents=True, exist_ok=True)
    (vault / s["canvas"]).mkdir(parents=True, exist_ok=True)

    # --- modules -----------------------------------------------------------
    for i, raw in enumerate(args.modules, start=1):
        name = safe_filename(raw)
        folder = vault / f"{i:02d} - {s['module']} {i} - {name}"

        emit(folder / f"M{i} - {s['overview']}.md",
             note([tag, "module", f"module/{i}"], f"M{i} · {raw}", todo,
                  {"module": i, "done": False}))

        for j in range(1, args.lessons + 1):
            emit(folder / f"M{i}.{j} - {s['lesson']} {j}.md",
                 note([tag, "lesson", f"module/{i}"], f"M{i}.{j} · TODO", todo))

        emit(folder / f"M{i} - {s['lab']}.md",
             note([tag, "lab", f"module/{i}"], f"M{i} · {s['lab']}", todo))

    print(f"Vault scaffolded at: {vault}")
    print(f"  modules: {len(args.modules)}  lessons/module: {args.lessons}  tag: {tag}")
    print(f"  notes created: {created}   skipped (already existed): {skipped}")
    print("\nNext: write the module overviews first, then the lessons.")
    print("      Run validate_vault.py before handing the vault over.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
