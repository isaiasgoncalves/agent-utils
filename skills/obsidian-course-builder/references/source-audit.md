# Source Audit

How to read a codebase critically and turn what's wrong with it into the best material in the course.

## Why this exists

Published code is assumed correct. That assumption is the single biggest obstacle to a learner reading code well — they hit something confusing, conclude they're the problem, and stop asking questions.

Auditing flips it. A vault that says *"this method is called four times and defined zero times; here's how to fix it, and here's the principle that lets it hide"* teaches three things at once: the technical fix, the reading skill, and the humility that all code has defects including their own.

It is also, bluntly, the highest-value section you can write. Anyone can paraphrase a README.

## Reading order

Read whole files, not grep hits. Grep finds the string; only reading the file tells you whether the string means what you assume.

1. `pyproject.toml` / `package.json` / lockfile — what's declared, what's declared *and never imported*
2. Config module — how settings are loaded, prefixes, defaults, validation
3. Entry point — startup order, what's constructed where, lifecycle
4. Data models and schemas — the shape of the domain
5. Services — the business logic
6. API / interface layer — how it's exposed
7. Orchestration — jobs, DAGs, schedulers
8. Tests — what's covered tells you what the author worried about
9. Docs / README — compare against everything above

Step 9 last, deliberately. Read the code first and the docs second, so you notice where they diverge instead of reading the code through the docs' framing.

## Defect patterns worth hunting

These recur across real projects. Each one is a good lesson.

### Called but never defined
`grep` for the method name across the repo. Zero definitions means every call site fails at runtime — and if the call sites have `try/except` fallbacks, the failure is invisible.

Check for this specifically when a project wraps a third-party SDK: wrappers drift from the library they wrap.

### Config prefix mismatch
Config classes declare an env prefix (`ENV_PREFIX="FOO__"`) and the `.env.example` uses a different one (`FOO_BAR=...`). The setting silently keeps its default. Diff every variable in the example file against every field in the config classes.

Symptom to look for downstream: a feature that "should be on" behaving as if it's off.

### `await` on something synchronous
An `async def` that awaits a plain function. `TypeError: object X can't be used in 'await' expression` — often swallowed by a broad `except` and re-raised as something domain-flavoured, which hides the real cause.

The reverse is worth flagging too: CPU-bound work called directly inside a coroutine, blocking the event loop. Correct form is `asyncio.to_thread(...)`.

### Signature mismatch at the call site
A factory or constructor called with a keyword it doesn't accept. Compare each `make_*`/factory invocation against its definition.

### Silent fallback
`try/except` that produces a plausible default. This is the most instructive defect of all, because it converts a fatal bug into *wrong behaviour that looks fine*. Trace what the system does when every fallback fires at once — sometimes the answer is "nothing works and nobody notices."

The fix is never "remove the fallback." It's "make the fallback emit a metric and an ERROR log."

### Field name drift
Code reads `record.get("section_name")` while the indexer writes `section_title`. The `.get()` default hides it. Cross-check every dictionary key read against where it's written.

### Non-deterministic IDs
Bulk inserts without an explicit `_id`. Re-running duplicates instead of upserting. Look for a deletion step that exists only to compensate.

### Check-then-act races
`if not exists(): create()` under concurrency. Usually harmless in dev with one worker, breaks with four. Check whether the code handles the "already exists" exception — if it does, that's a scar worth pointing out approvingly.

### Docs that drifted
README ports vs compose port mappings. Claimed versions vs pinned versions. Endpoint paths in a Makefile vs the router prefix. These cost learners hours and are trivially verifiable.

### Dead code
Prompts, functions, imports defined and never referenced. Confusing because the reader searches for the call site that doesn't exist. Worth listing — deleting it is a good first contribution.

### Missing return values
A response schema declares a field the service never populates. Downstream features that depend on it are broken end to end (a feedback endpoint that needs a `trace_id` that's always `null`, for example).

## Verifying before you claim

Every reported defect must be something you *read*, not inferred.

- Claiming a method doesn't exist? `grep -rn "def method_name"` across the repo and paste the empty result into your reasoning.
- Claiming a prefix mismatch? Show both the config field and the example line.
- Claiming a version discrepancy? Cite both files.

State the limit of your method explicitly in the note: this is a static reading at a given commit, library versions move, reproduce before applying. That framing is honest and it also turns the reader into a participant.

If you're unsure, write it as a question in the note rather than an assertion. "This looks like it would fail — reproduce it before applying the fix" is fine. A wrong bug claim costs the learner more than a missing one.

## Writing the bugs note

**Severity tiers**, in order:

| Tier | Meaning |
|---|---|
| 🔴 Blocking | the code doesn't run, or a whole feature is dead |
| 🟠 Serious | runs but produces wrong results silently |
| 🟡 Minor | inconsistencies, dead code, stale docs, tech debt |

**Per defect**, a compact table then the fix:

```markdown
### B1 · <One-line title>

| | |
|---|---|
| **Where** | `path/to/file.py` |
| **Symptom** | what the learner will observe |
| **Cause** | the actual mechanism |
| **Severity** | 🔴 / 🟠 / 🟡 |
| **Lesson** | [[the note where this is taught]] |

```python
# the corrected code
```
```

**Fix-order diagram.** A mermaid graph with rough time estimates, ending in "minimum path to a working system: B5 → B4 → B2 → B1, about an hour." That single line converts an intimidating list into a plan.

**The principles section.** The most valuable part. Group the defects by what they teach:

> **Silent fallback is worse than a crash.** A broad `except` with a plausible default turns a fatal bug into behaviour nobody notices. Every fallback should emit a metric and an ERROR log.
>
> **A wrapper that doesn't track its library becomes debt.** The abstraction over the SDK was created to make it swappable; what happened is it drifted out of sync. Abstract when you *are* switching, not in case you might.
>
> **`.get(key, default)` hides typos.** Convenient, dangerous. On critical fields, prefer direct access or schema validation.

**Contribute back.** End with a link to the project's issues page and a note that fixing these and opening a PR is a better portfolio item than most personal projects.

## Tone

Non-negotiable, and easy to get wrong.

The project author is usually generous — they published something useful for free. Write as a careful reader who found things, not as a critic scoring points.

| Avoid | Prefer |
|---|---|
| "this is sloppy" | "this breaks when N > 1 because…" |
| "obviously wrong" | "the call site and the definition disagree — here's both" |
| "the author didn't understand X" | "this is the v2 API; the pinned version is v3" |

Open the note by saying plainly that the audit is teaching material, not criticism, and that finding defects in working code is what the job actually consists of. Then, where the source does something genuinely clever — handling a race condition, choosing a non-obvious default for a good reason — **say so**. A note that only finds fault reads as an axe-grind and the learner discounts it.
