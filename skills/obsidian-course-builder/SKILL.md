---
name: obsidian-course-builder
description: Builds a complete, months-long study course as an Obsidian vault — modules, hands-on lessons, atomic concept notes, labs, canvases, and curated external links. Use this skill whenever someone wants to learn a technical subject deeply and asks for a course, a curriculum, a study plan, a learning path, a step-by-step tutorial, structured study material, or wants an existing repo/book/docs/paper turned into something they can actually learn from. Trigger it even when they don't say the word "course" — phrases like "I want to really learn X", "help me study Y", "turn this codebase into a tutorial", "I have this repo but I can't learn from it", "monta um material de estudo", "quero aprender X de verdade", "trilha de aprendizado" all mean this skill. Strongest fit for programming, software architecture, Data Science, ML/AI and data engineering, but works for any technical subject.
---

# Obsidian Course Builder

## What this produces

A **vault** — a folder of interlinked Markdown notes that the learner opens in Obsidian and works through over weeks or months. Not a summary. Not a README. A course that carries someone from "I don't get this" to "I can build this and defend my decisions."

The output is a directory tree like this (numbered prefixes so Obsidian's file explorer sorts it correctly):

```
<Course Name>/
├── 00 - Start Here/          MOC, how-to-use, machine setup, study plan, visual map, glossary
├── 01..NN - Module folders/  Overview + 3-6 lessons + Lab per module
├── 08 - Cross-cutting/       Architecture, known bugs, testing, evaluation, going to production
├── 90 - References/          Tool index, curated external links
├── 91 - Concepts/            Atomic notes (one idea each), reusable across modules
├── 93 - Canvas/              Navigable .canvas boards
└── 99 - Templates/           Study-note template the learner fills in
```

Write everything in **the language the user is speaking**. Keep technical terms in English (embedding, chunking, commit, DataFrame) — translating them cuts the learner off from the documentation and StackOverflow answers they'll need.

## The pedagogy this encodes

These are not stylistic preferences; each one exists because it fixes a specific failure mode of technical material. Understanding *why* lets you adapt when a subject doesn't fit the mold.

**Analogy before code.** A learner facing unfamiliar syntax spends their working memory on parsing, leaving none for understanding. A concrete everyday analogy ("a container is a furnished apartment; the volume is the storage unit you rent separately") installs the mental model first, so the code becomes confirmation rather than discovery.

**Trade-offs, not facts.** Anyone can memorize that a project uses PostgreSQL. What makes someone employable is being able to say *why not SQLite, and what it cost*. Every lesson has a "Why this way?" table with the alternative and the price paid. This is the single highest-value section and the one most tutorials skip entirely.

**Deliberate breakage.** Reading working code teaches recognition; breaking it teaches understanding. Every lesson ends with 4-6 sabotage exercises — remove the healthcheck, use the wrong task type, set the overlap to zero — with a blank for the learner to write the symptom they observed. Writing down the symptom is what converts it into memory.

**Audit the source, don't worship it.** Real material has real bugs, dead code, stale docs. Finding them is not disrespect — it is the actual job. A dedicated "Known Bugs" note turns every defect into a graded exercise and teaches the learner to read code critically instead of assuming it's correct because it's published.

**Atomic concept notes.** Explaining BM25 inside a lesson buries it. A standalone note gets linked from four places, revisited, and extended. This is how a vault becomes a personal knowledge base instead of a linear document.

**Honest time estimates.** If the source says "7 weeks" and that's the time to *run* the code, say so and give the time to *learn* it. Padding is disrespectful; so is pretending mastery is fast.

**Build it yourself.** The learner creates their own project directory and types the code. The source repo is the answer key, not the starting point. Say this explicitly in the "How to use this vault" note, and give them the `diff` command to compare.

## Workflow

Work through these in order. Steps 1-3 are fast; the writing in step 5 is the bulk.

Two habits make the difference between finishing and not:

**Write every note to disk the moment you finish composing it.** Never hold a batch of notes in your head to write at the end. Building a vault is long work and long work gets interrupted — a limit, a timeout, a crash. If you write incrementally, an interruption costs you one note and you resume from the tree on disk. If you batch, it costs you everything.

**Read the reference files in stages, as each becomes relevant** — `source-audit.md` before auditing, `curriculum-design.md` before sequencing, `note-anatomy.md` before writing, `canvas-format.md` before the boards. Loading all four upfront buries the material you need right now under three files you need in an hour.

### 1. Establish the source and the destination

Ask only what you can't infer. Typically you need to know:

- **Source material**: a repo path, docs, PDFs, a book, a topic with no material, or a mix. If they point at a folder, read it — don't ask them to describe it.
- **Where the vault goes**: default to a sibling of the source material, or a folder they name.
- **Their starting level**: "I know Python, never touched Docker" changes the depth of Module 1 substantially.

If the material is a codebase, tell them upfront you'll audit it for defects — people are sometimes surprised, and they're always glad.

### 2. Read the source material properly

This is where the quality is won or lost. Superficial reading produces a course that paraphrases the README, which the learner could have done themselves.

For a codebase, read in this order and read **whole files**, not grep excerpts:
config → entry point → data models → services → API layer → orchestration → tests

You are looking for four things:
1. **What each piece does** — the raw material of the lessons
2. **Why it was built that way** — the trade-off tables
3. **Where it's wrong** — the bugs note
4. **What it's missing** — the exercises and capstone extensions

Read `references/source-audit.md` before auditing a codebase. It has the specific defect patterns worth hunting (methods called but never defined, config prefix mismatches, `await` on sync functions, silent fallbacks, dead code, stale docs) and how to report them without being sanctimonious.

For a topic with no source material, research first (WebSearch, official docs) and design the curriculum from the dependency graph of the concepts. Read `references/curriculum-design.md`.

### 3. Design the curriculum

Read `references/curriculum-design.md` for how to sequence modules, size lessons, and calibrate difficulty. The short version: 5-8 modules, each with an overview + 3-6 lessons + one lab, ordered so that every module only depends on earlier ones. Name modules after *capabilities gained*, not topics covered.

Show the user the module list and the estimated hours before writing. A two-minute correction here saves rewriting twenty notes.

**Size the course to what you will actually finish.** Four modules written in full beat seven left half-written — a learner can work through the first, and cannot work through the second. If the subject genuinely needs more, say so and offer to build the remaining modules in a second pass; a vault delivered in two halves is fine, a vault of stubs is not.

### 4. Scaffold

```bash
python <skill>/scripts/scaffold_vault.py "<vault path>" --modules "Module 1 name" "Module 2 name" ...
```

Creates the directory tree and placeholder files with correct frontmatter. Run `--help` for options. Doing this mechanically frees you to spend your effort on the writing.

### 5. Write the notes

Read `references/note-anatomy.md` — it has the full template for every note type with worked examples. That file is the specification; this section is the orientation.

Write in this order, because each stage informs the next:

1. **Module overviews** — forces you to commit to scope before writing details
2. **Lessons** — the bulk of the work
3. **Labs** — exercises that fall out naturally from what the lessons taught
4. **Concept notes** — extract whatever you found yourself explaining twice
5. **Cross-cutting notes** — architecture, bugs, testing, evaluation, production
6. **Start Here notes** — write the MOC and study plan *last*, when you know what's actually in the vault
7. **References** — tool index and curated links

The lesson skeleton, which is the heart of the format:

```markdown
# M2.1 · <Lesson title>

> [!abstract] 🎯 In one sentence
> The elevator-pitch version.

⏱️ ~3 h · 📄 Reference: `path/to/real/file.py`

## 🎪 The analogy
Everyday concrete situation that maps onto the concept.

## ⌨️ Hands-on
Numbered steps. Real code, commented line by line with `# 👈` marking
your annotations (so the learner knows what's yours vs. the original).

## 🏛️ Why this way?
| Decision | Alternative | Trade-off |

## ⚠️ Pitfalls
Symptom → cause → diagnosis table. Where people actually get stuck.

## 💥 Break it on purpose
4-6 numbered sabotages with blanks for observed symptoms.

## 📚 Go deeper
Essential (3-4 links) / Advanced (3-5 links), each with one line on why.

## ✅ Checklist
- [ ] Concrete, verifiable completion criteria

**Previous:** [[...]] · **Next:** [[...]]
```

Obsidian specifics you need: `[[wikilinks]]` resolve by filename anywhere in the vault, so filenames must be unique and stable. Inside tables, escape the alias pipe: `[[Note\|alias]]`. Callouts are `> [!tip]`, `> [!warning]`, `> [!danger]`, `> [!important]`, `> [!question]`, `> [!example]`, `> [!quote]`. Mermaid renders natively in ` ```mermaid ` fences — use it liberally for flows, sequences and timelines. LaTeX renders in `$...$` and `$$...$$`.

### 6. Build canvases

Read `references/canvas-format.md` for the JSON schema and layout conventions. Build 2-4 boards — typically one whole-system architecture board that doubles as navigation (with `file` nodes pointing at module overviews), plus one per major subsystem.

```bash
python <skill>/scripts/validate_vault.py "<vault path>"
```

Validates canvas JSON, checks that every `file` node resolves, finds broken wikilinks, and reports word counts. Run it before you hand anything over. Broken links in a vault are the fastest way to lose a learner's trust.

### 7. Hand over

Report: file count, word count, module list, and — if you audited a codebase — the defect table with severity. Give them the one command to get started. Mention any real limitation you hit (material you couldn't access, a section you kept thin) rather than letting them discover it.

## Adapting when the subject doesn't fit

The format was designed against a software codebase. Most of it generalizes, but be deliberate:

**Data Science / ML.** "Break it on purpose" becomes sabotage of *data and assumptions*: leak the target into the features, drop the stratification, train on unbalanced classes, remove the validation split. The trade-off tables cover model choice, metric choice, and sampling strategy. Add a cross-cutting note on **experiment reproducibility** (seeds, environment, data versioning) — it's the equivalent of the "going to production" note. Notebooks belong in a `94 - Notebooks/` folder, linked from the lessons, never as the lesson itself.

**Math-heavy subjects.** Keep the analogy section — it matters more, not less. "Break it on purpose" becomes *counter-examples*: violate a theorem's hypothesis and watch the conclusion fail. Derive at least one result by hand before showing the library call, the way the BM25 lesson computes scores manually before calling `_explain`.

**Tools with no source code** (a SaaS product, a methodology). Replace the code audit with a **limitations audit**: what the docs claim vs. what actually happens, undocumented edge cases, where the abstraction leaks. Labs become guided real usage with observations recorded.

**Non-technical subjects.** The scaffolding holds; the sabotage section becomes "test the boundaries" — apply the framework where it doesn't fit and articulate why it breaks.

The invariant across all of these: *the learner must produce something and must break something.* If a section can't do either, it's a reference note, not a lesson.

## Quality bar

The vault is done when a learner could:

- Follow it without you present
- Explain *why* each decision was made, not just what it was
- Find where they got something wrong when a lab fails
- Know what to study next when they finish

Before handing over, check honestly:

- [ ] Every lesson has a working analogy, real code, a trade-off table, and sabotages
- [ ] Every claim about the source material is verified — you read the file, you didn't infer it
- [ ] External links are current and each has a reason to exist
- [ ] `validate_vault.py` passes
- [ ] The study plan is honest about time
- [ ] Someone who finishes has something to show, not just notes to file

**The failure mode to fear**: a vault that is comprehensive, well-linked, beautifully formatted, and produces no change in what the learner can do. Depth of engagement beats breadth of coverage every time. Six modules the learner completes are worth more than twelve they abandon.

## Reference files

| File | Read it when |
|---|---|
| `references/note-anatomy.md` | Before writing any note — full templates for all 9 note types |
| `references/curriculum-design.md` | During step 3, and whenever a module feels wrongly sized |
| `references/source-audit.md` | Before auditing a codebase — defect patterns and how to report them |
| `references/canvas-format.md` | Before building canvases — JSON schema, colors, layout |

| Script | Purpose |
|---|---|
| `scripts/scaffold_vault.py` | Creates the folder tree and stub notes |
| `scripts/validate_vault.py` | Broken wikilinks, canvas JSON, file-node paths, word counts |
