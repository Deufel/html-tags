import marimo

__generated_with = "0.22.0"
app = marimo.App()


@app.cell
def _():
    """Flashcard deck demo.

    Shows off the SVG-wrapping-HTML-via-foreignObject pattern:
    - SVG provides decorative paper-like borders, corner flourishes, and the
      flip-animation coordinate space.
    - foreignObject embeds real HTML: typography, a <textarea> for the user's
      guess, buttons, etc.
    - Datastar (signals + data-* attributes) handles the interactivity.

    Everything renders as a single self-contained HTML file.
    """
    import sys
    import json
    import html_tags as h

    """Flashcard deck demo.

    Shows off the SVG-wrapping-HTML-via-foreignObject pattern:
    - SVG provides decorative paper-like borders, corner flourishes, and the
      flip-animation coordinate space.
    - foreignObject embeds real HTML: typography, a <textarea> for the user's
      guess, buttons, etc.
    - Datastar (signals + data-* attributes) handles the interactivity.

    Everything renders as a single self-contained HTML file.
    """
    import sys; sys.path.insert(0, '/home/claude')
    import json
    import html_tags as h

    # ── Deck content ─────────────────────────────────────────────────────────
    CARDS = [
        {"q": "What is a closure?",
         "a": "A function plus the variables it captured from its defining scope."},
        {"q": "What does `data-on:click` do in Datastar?",
         "a": "Attaches a click event handler that evaluates a Datastar expression."},
        {"q": "Why does <circle/> self-close in SVG but <input> doesn't in HTML?",
         "a": "SVG uses XML rules (self-closing void elements); HTML uses its own void-element list without self-closing."},
        {"q": "What is referential transparency?",
         "a": "A function is referentially transparent if replacing it with its return value never changes program behavior."},
    ]

    # ── SVG decoration: a single reusable corner flourish ────────────────────
    def corner(x, y, rotate=0):
        """A decorative L-shaped corner stroke."""
        return h.g(transform=f"translate({x},{y}) rotate({rotate})")(
            h.path(d="M 0 20 L 0 0 L 20 0",
                   stroke="currentColor", fill="none",
                   **{"stroke-width": "2", "stroke-linecap": "round"}),
            h.circle(cx="0", cy="0", r="3", fill="currentColor"),
        )

    # ── The card component ───────────────────────────────────────────────────
    def card(index, q, a):
        """One flashcard. SVG shell + foreignObject HTML content."""
        sig = f"card{index}"   # per-card signal namespace

        # The HTML that lives inside the foreignObject
        inner = h.div(
            {"style": "height:100%; box-sizing:border-box; display:flex; "
                      "flex-direction:column; padding:1.5rem; "
                      "font-family:system-ui, sans-serif;"},
            # Front face (question + answer input)
            h.div(
                {"data-show": f"!${sig}_flipped",
                 "style": "flex:1; display:flex; flex-direction:column; gap:1rem;"},
                h.div({"style": "font-size:0.75rem; color:#888; letter-spacing:0.1em;"},
                      f"QUESTION {index+1} / {len(CARDS)}"),
                h.div({"style": "font-size:1.25rem; font-weight:500; line-height:1.4;"}, q),
                h.textarea(
                    {"data-bind": f"{sig}_guess",
                     "placeholder": "Type your answer, then flip…",
                     "style": "flex:1; border:1px solid #ddd; border-radius:6px; "
                              "padding:0.75rem; font:inherit; resize:none; outline:none;"},
                ),
                h.button(
                    {"data-on:click": f"${sig}_flipped = true",
                     "style": "padding:0.6rem; border:none; border-radius:6px; "
                              "background:#1a1a1a; color:white; font:inherit; cursor:pointer;"},
                    "Reveal answer ↓",
                ),
            ),
            # Back face (answer + self-grade)
            h.div(
                {"data-show": f"${sig}_flipped",
                 "style": "flex:1; display:flex; flex-direction:column; gap:0.75rem;"},
                h.div({"style": "font-size:0.75rem; color:#888; letter-spacing:0.1em;"},
                      "YOUR ANSWER"),
                h.div({"data-text": f"${sig}_guess || '(no answer)'",
                       "style": "padding:0.5rem 0.75rem; background:#f4f4f4; "
                                "border-radius:6px; min-height:2rem; color:#555;"}),
                h.div({"style": "font-size:0.75rem; color:#888; letter-spacing:0.1em;"},
                      "CORRECT ANSWER"),
                h.div({"style": "padding:0.5rem 0.75rem; background:#eef7ee; "
                                "border-radius:6px; line-height:1.4;"}, a),
                h.div({"style": "display:flex; gap:0.5rem; margin-top:auto;"},
                    h.button(
                        {"data-on:click": f"${sig}_flipped = false; ${sig}_guess = ''; $current = ($current + 1) % {len(CARDS)}",
                         "style": "flex:1; padding:0.6rem; border:1px solid #c33; "
                                  "background:white; color:#c33; border-radius:6px; "
                                  "font:inherit; cursor:pointer;"},
                        "Missed it ✗"),
                    h.button(
                        {"data-on:click": f"${sig}_flipped = false; ${sig}_guess = ''; $current = ($current + 1) % {len(CARDS)}; $score++",
                         "style": "flex:1; padding:0.6rem; border:none; "
                                  "background:#2a7; color:white; border-radius:6px; "
                                  "font:inherit; cursor:pointer;"},
                        "Got it ✓"),
                ),
            ),
        )

        # The SVG shell — decorative corners + paper background
        return h.svg(
            {"viewBox": "0 0 400 300",
             "data-show": f"$current == {index}",
             "style": "width:400px; height:300px; color:#1a1a1a; "
                      "filter:drop-shadow(0 8px 24px rgba(0,0,0,0.1));"},
            # Paper background with subtle gradient
            h.defs(
                h.linearGradient(id=f"paper{index}", x1="0", y1="0", x2="0", y2="1")(
                    h.stop({"offset": "0%", "stop-color": "#fdfdfb"}),
                    h.stop({"offset": "100%", "stop-color": "#f5f3ee"}),
                ),
            ),
            h.rect(x="0", y="0", width="400", height="300", rx="12",
                   fill=f"url(#paper{index})", stroke="#e5e2da", **{"stroke-width": "1"}),
            # Corner flourishes at each corner
            corner(16, 16, 0),
            corner(384, 16, 90),
            corner(384, 284, 180),
            corner(16, 284, 270),
            # The HTML content
            h.foreignObject(inner, x="0", y="0", width="400", height="300"),
        )

    # ── Assemble the deck ────────────────────────────────────────────────────
    # Initial signals: one flip + guess per card, plus global current/score
    init_signals = {"current": 0, "score": 0}
    for i in range(len(CARDS)):
        init_signals[f"card{i}_flipped"] = False
        init_signals[f"card{i}_guess"]   = ""

    deck = h.div(
        {"data-signals": json.dumps(init_signals),
         "style": "display:flex; flex-direction:column; align-items:center; gap:1.5rem;"},
        h.div({"style": "font-size:0.875rem; color:#666;"},
            "Score: ", h.span({"data-text": "$score", "style": "font-weight:600;"}),
            " / ", str(len(CARDS)),
        ),
        h.div({"style": "position:relative;"},
            *[card(i, c["q"], c["a"]) for i, c in enumerate(CARDS)],
        ),
    )

    # ── Full page ────────────────────────────────────────────────────────────
    page = h.html_doc(
        h.head(
            h.meta(charset="utf-8"),
            h.title("Flashcard Deck"),
            h.Favicon("📇"),
            h.Datastar(),
            h.style("""
                body { margin:0; padding:3rem 1rem; background:#fafaf7;
                       font-family:system-ui, sans-serif; min-height:100vh; }
                button:hover { opacity:0.9; }
                textarea:focus { border-color:#999; }
            """),
        ),
        h.body(deck),
    )

    return h, page


@app.cell
def _():
    return


@app.cell
def _(page):
    from pathlib import Path

    # Resolves to the same directory as the notebook file
    output_path = Path(__file__).parent / "flashcards.html"

    with open(output_path, 'w') as f:
        f.write(str(page))

    print(f"Wrote {output_path}")
    print(f"File size: {len(str(page))} chars")
    return


@app.cell
def _(h):
    h.Datastar()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
