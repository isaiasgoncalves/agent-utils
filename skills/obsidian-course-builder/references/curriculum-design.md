# Curriculum Design

How to turn a subject into a sequence someone can actually walk.

## Contents

1. [The dependency graph](#1-the-dependency-graph)
2. [Sizing modules and lessons](#2-sizing-modules-and-lessons)
3. [Naming](#3-naming)
4. [Ordering heuristics](#4-ordering-heuristics)
5. [Time estimates that aren't lies](#5-time-estimates-that-arent-lies)
6. [Designing from a codebase](#6-designing-from-a-codebase)
7. [Designing from a topic with no material](#7-designing-from-a-topic-with-no-material)
8. [Designing from mixed sources](#8-designing-from-mixed-sources)
9. [Calibrating to the learner](#9-calibrating-to-the-learner)
10. [Data Science specifics](#10-data-science-specifics)

---

## 1. The dependency graph

Before deciding on modules, list the concepts the subject requires and draw the arrows: *X must be understood before Y.* The module sequence is a topological sort of that graph.

Two failure modes this prevents:

**Forward references.** A lesson that says "we'll cover this later" is a lesson that will confuse someone. If you find yourself writing that, the ordering is wrong — either move the lesson or move the dependency.

**Premature abstraction.** Teaching the framework before the problem it solves. The learner memorizes API calls with no idea why they exist. Always: problem → naive solution → why it fails → the real solution.

When two branches are genuinely independent, say so explicitly in the study plan — some learners will want to parallelize or skip.

## 2. Sizing modules and lessons

| Unit | Target | Signal it's wrong |
|---|---|---|
| Course | 5-8 modules | fewer: probably a tutorial; more: probably two courses |
| Module | 3-6 lessons + 1 lab | one lesson: fold it elsewhere; eight: split the module |
| Lesson | 2-4 h, 200-450 lines | under 1 h: merge; over 5 h: split |
| Lab | 5-8 exercises, ~4 h | — |

A lesson is one *coherent capability*: "make an HTTP client that survives a flaky API" is a lesson. "HTTP" is a module. "The `httpx` timeout parameter" is a paragraph.

If a lesson keeps growing, look for the seam. Usually there are two capabilities hiding in it — often "how it works" and "how it fails."

## 3. Naming

Name modules after **what the learner can do afterwards**, not what is covered.

| Weak | Strong |
|---|---|
| "Docker and Compose" | "Infrastructure — the factory floor" |
| "Introduction to embeddings" | "Chunking and hybrid search — the semantic layer" |
| "Pandas basics" | "From raw file to trustworthy DataFrame" |
| "Testing" | "Proving it works before someone else finds out it doesn't" |

The strong versions do two things: they tell the learner why to care, and they force *you* to be honest about whether the module delivers a capability at all. A module you can't name this way is probably a grab-bag.

Lesson names can be plainer — they live under a module that already set the frame — but keep them concrete: "Retry, rate limit and XML" beats "Working with the API."

## 4. Ordering heuristics

**Foundations before intelligence.** In any AI/data course, the boring plumbing (storage, retrieval, pipelines) comes before the model. Learners want to skip to the model; the ones who do build systems that hallucinate and can't be debugged. Say this out loud in the first module — the reason is more persuasive than the rule.

**Interpretable before opaque.** Keyword search before vector search. Linear regression before gradient boosting. Rules before learned behaviour. The learner needs a baseline they can reason about before they meet one they can't.

**Manual before framework.** Compute the metric by hand once. Write the retry loop before using `tenacity`. Build the pipeline before importing `sklearn.pipeline`. Then show the library and the learner understands what it's saving them.

**Working before optimal.** Get end-to-end early, even if crude. A learner with a working system has a place to put every subsequent improvement. A learner still assembling components after six weeks quits.

**Observability before scale.** You can't optimize what you can't measure, and the module on measurement usually reveals that the bottleneck isn't where anyone assumed.

## 5. Time estimates that aren't lies

Course materials systematically underestimate because they measure *reading and running*, not *learning*.

Per lesson, realistic budget:

| Activity | Time |
|---|---|
| Read the concept | 0.5-1 h |
| Type the code, hit errors, fix them | 1.5-3 h |
| Lab and sabotage | 1-2 h |
| Active recall (write it in your own words) | 0.5 h |

So a 3-hour lesson is 3 hours of *the learner's engaged work*, not 3 hours of your writing. Sum honestly, then present pace options:

| Pace | h/week | Duration |
|---|---|---|
| Sustainable (recommended) | 6-8 | full |
| Intense | 15 | half |
| Weekends only | 4 | double |

If the source material claims a shorter timeline, address it directly rather than silently disagreeing. Explain the arithmetic. Learners trust honesty about difficulty far more than optimism, and an underestimate that makes them feel slow is how people quit.

## 6. Designing from a codebase

The repository's own structure is a *hint*, not the curriculum. Common divergences worth making:

- **A "week" in the source is often two modules.** Look for where a chapter introduces two unrelated capabilities.
- **Cross-cutting concerns are scattered.** Testing, config, error handling appear everywhere in code and deserve their own notes.
- **The source's ordering may be chronological, not pedagogical.** It shows what was built when, not what should be learned first.

Map the codebase to modules by tracing the **data flow**, not the folder structure: where does data enter, what transforms it, where does it rest, how is it served, what watches it. That flow is almost always the right module sequence, because it's the order in which a learner can test each piece.

Then, for each module, decide what the learner **builds from scratch** versus **reads and understands**. Building everything takes forever; reading everything teaches nothing. A good split: they build the core abstraction of each module by hand, and read the surrounding infrastructure.

## 7. Designing from a topic with no material

Research first. Read the official documentation's own table of contents — maintainers have usually thought hard about ordering. Look at 2-3 well-regarded courses or books and note where they *agree* on sequence; that consensus is signal.

Then design backwards from a capstone. Decide what the learner will have built at the end — something concrete and demonstrable — and work out the prerequisite chain. This guarantees every module earns its place, because you can point at what it contributes to the final artifact.

Write the code examples yourself and **run them**. Fabricated code in a course is worse than no course; the learner loses hours to an error you invented. If you cannot run something, say so in the note.

For external links, prefer official docs and original papers over blog posts. Blog posts rot fastest and are the most likely to be wrong.

## 8. Designing from mixed sources

When the user supplies a repo *and* a book *and* their own notes, the risk is a vault that reads like three courses stapled together.

Resolve it by picking one **spine** — usually the codebase, because code gives concrete deliverables — and treating everything else as depth. The book becomes "Go deeper" links and concept-note material. Their notes become a starting point for the study-note template and reveal what they already care about.

Where sources disagree, that's gold: a `> [!question]` callout laying out both positions and asking the learner to decide teaches more than either source alone.

## 9. Calibrating to the learner

Ask what they already know; it changes the depth of early modules by a factor of three.

| They say | Adjust |
|---|---|
| "I know Python, never used Docker" | Module 1 doubles in depth; skip Python basics entirely |
| "I'm a data scientist moving to engineering" | Compress the modeling, expand testing, deployment, APIs |
| "I've built RAG before, want to do it properly" | Compress the basics, expand evaluation and production |
| "Complete beginner" | Add a module 0 on the language and tooling; expect double the time |

When unsure, write for someone competent in the adjacent area but new to this one, and put the true fundamentals in concept notes they can skip. That's the widest audience without patronizing anyone.

## 10. Data Science specifics

The format needs real adaptation here, because the failure modes are different.

**The module sequence is usually:** the question and the data → cleaning and validation → exploration → features → baseline model → evaluation and error analysis → improvement → deployment and monitoring.

Note where evaluation sits: **before** improvement. This is deliberate and it's the opposite of how most people work. A learner who improves before measuring learns nothing from the improvement.

**Sabotage becomes assumption-breaking**, and it's more valuable here than anywhere:

- Leak the target into a feature and watch validation accuracy hit 0.99
- Remove stratification and watch the metric become unstable across seeds
- Fit the scaler on the full dataset before splitting, and measure the optimism
- Train on class-imbalanced data with accuracy as the metric
- Shuffle a time-series split
- Drop the random seed and rerun five times

Each of these produces a *plausible wrong result* — which is exactly the danger in real work, and why doing it deliberately once is worth more than a warning in prose.

**Add a cross-cutting note on reproducibility**: seeds, environment pinning, data versioning, notebook hygiene, what to commit. This is the DS equivalent of "going to production."

**Notebooks**: keep them in `94 - Notebooks/`, linked from the lessons as artifacts to run — never as the lesson body. A notebook is a lab bench, not a textbook. The reasoning lives in the note; the execution lives in the notebook.

**Datasets**: name them, link them, and state the size. If a dataset needs a download that takes twenty minutes, say so in the module overview so the learner starts it before reading.
