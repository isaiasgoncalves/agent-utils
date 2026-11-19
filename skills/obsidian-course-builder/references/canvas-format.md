# Canvas Format

Obsidian `.canvas` files are plain JSON. They're the highest-impact-per-effort artifact in the vault: a learner who is lost opens the architecture board and re-orients in ten seconds.

## Schema

```json
{
  "nodes": [
    {
      "id": "unique-string",
      "type": "text",
      "text": "# Markdown\n\nWorks here, including **bold** and tables.",
      "x": 0, "y": 0, "width": 320, "height": 160,
      "color": "4"
    },
    {
      "id": "note-ref",
      "type": "file",
      "file": "01 - Module/M1 - Overview.md",
      "x": 400, "y": 0, "width": 320, "height": 300
    },
    {
      "id": "grp",
      "type": "group",
      "label": "Group label",
      "x": -40, "y": -40, "width": 800, "height": 600,
      "color": "5"
    }
  ],
  "edges": [
    {
      "id": "e1",
      "fromNode": "unique-string", "fromSide": "right",
      "toNode": "note-ref",        "toSide": "left",
      "label": "optional"
    }
  ]
}
```

**Node types.** `text` (markdown card) · `file` (embeds a vault note — clickable, this is what makes the board navigable) · `group` (a labelled rectangle; place it *before* its members in the array so it renders behind them) · `link` (external URL).

**Sides** for edges: `top` `right` `bottom` `left`.

**Colors** are strings `"1"`–`"6"`: 1 red · 2 orange · 3 yellow · 4 green · 5 cyan · 6 purple. A hex value works too but the presets adapt to the user's theme, so prefer them.

**`file` paths are vault-root-relative**, using forward slashes, including the `.md` extension. A path that doesn't resolve renders as a blank card — this is the most common canvas defect, and `validate_vault.py` catches it.

## Colour convention

Consistency across boards means the learner reads colour without a legend:

| Colour | Meaning |
|---|---|
| 🔴 `"1"` | where it breaks · known bug · warning |
| 🟠 `"2"` | service layer · LLM · compute |
| 🟡 `"3"` | decision · routing · fusion |
| 🟢 `"4"` | data and storage working correctly |
| 🔵 `"5"` | infrastructure · orchestration · entry points |
| 🟣 `"6"` | meta: navigation, state, concepts |

Put the legend in the canvas index note, not on every board.

## Layout

Canvas coordinates grow **right and down**; negative values are fine and useful for centering. Nothing auto-lays-out, so plan a grid.

Workable defaults: cards 280-340 wide, 100-250 tall; 40px gutters; columns every ~360px; a title card at the top spanning the width.

Left-to-right for pipelines and data flow. Top-to-bottom for decision graphs and state machines. Keep the main path on one axis and put annotations off to the side, so the eye follows the flow without zigzagging.

A card's text can be substantial — full markdown tables render — but past ~250px of height the card competes with the diagram. When a card wants to be a document, make it a `file` node instead.

## Which boards to build

Two to four. More than four and none of them get opened.

**Architecture (always).** The whole system with every component, plus a strip of `file` nodes at the bottom linking to each module overview, chained left to right with edges. This board doubles as the vault's navigation and is the one people return to.

**One per major subsystem.** Whatever the course's spine is — the data pipeline, the request path, the state machine. Annotate these with the things a diagram can show and prose can't: where the semaphores are, what the timing actually is, which arrow is the bottleneck.

**The known-bugs overlay.** Rather than a separate board, mark the affected components red on the subsystem boards with the bug ID (`🐞 B4: await on sync method`). The learner sees the defect in its architectural context, which is where it makes sense.

## What makes a board worth opening

A canvas that restates the module list is wasted effort. Put on it what *only* a spatial layout can carry:

- **Timing on the arrows.** `~1.9 s` on the embedding call immediately shows where the latency lives.
- **Cost annotations.** "3 LLM calls on the happy path, 5 with one rewrite" beside the graph makes the trade-off concrete.
- **The bug markers.** In place, in context.
- **The thing that surprises.** If the bottleneck isn't where anyone expects, the board should say so out loud.

## Index note

Create `93 - Canvas/Canvas Index.md` listing the boards in a table (board / covers / open it when), the colour legend, and — this matters more than it sounds — an instruction to **redraw the diagram from memory before looking at yours**. What they can't draw is exactly what they haven't understood. If they have the Excalidraw plugin, freehand is better still.

## Validation

Always run before handing over:

```bash
python <skill>/scripts/validate_vault.py "<vault path>"
```

It parses every `.canvas`, checks that edge endpoints reference existing node ids, and resolves every `file` path. Broken canvases are silent failures — Obsidian renders a blank card rather than an error — so this check is the only thing standing between you and a board with holes in it.

## Editing by hand

Adding cards by hand is fine; just remember node ids must be unique within the file and every edge endpoint must exist. If a board gets complex, it's often faster to write a small Python script that emits the JSON than to hand-place forty cards — the coordinates are arithmetic.
