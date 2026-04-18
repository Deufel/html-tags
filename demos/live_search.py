import marimo

__generated_with = "0.22.0"
app = marimo.App()


@app.cell
def _():
    return


@app.cell
def _():
    """Generic searchable documentation page generator.

    Takes a list of items — each a dict with {id, name, description (tag tree),
    searchable_text} — and produces a full-page HTML document with:
      • Color & Type app shell (header, nav, main, footer)
      • Theme/size/motion toggles (cycle through variants)
      • Live search + multi-tag filter
      • Per-item match counts rendered in the nav and as badges
      • data-show filtering + data-style:order reordering by relevance

    The generator knows nothing about Datastar attribute documentation specifically.
    Feed it any homogeneous list of items and you get a filtered docs page.
    """
    import sys; sys.path.insert(0, '/home/claude')
    import json
    import html_tags as h


    # ─── CSS stylesheet reference ────────────────────────────────────────────
    # Once Mike publishes his CDN this becomes a one-liner. For now we inline
    # a stylesheet link via a `css_href` parameter so the generator works both
    # offline (local file path) and online (CDN url).

    CDN_CSS = "https://cdn.jsdelivr.net/gh/Deufel/toolbox@latest/css/style.css"


    # ─── Search bar ──────────────────────────────────────────────────────────

    def _search_bar():
        """Sticky search bar — input + add-tag + clear.

        Signals used: $search (str), $tags (list[str]).
        """
        return h.form(
            {"class": "surface row",
             "style": "position: sticky; top: 0; z-index: 50; padding: 0.75rem 1.5rem; "
                      "align-items: center; border-bottom: 1px solid var(--border);",
             "data-on:submit__prevent":
                 "$search.trim() ? ($tags = [...$tags, $search.trim()], $search = '') : null"},
            h.input_({
                "type": "text",
                "placeholder": "Live search… (enter to add tag)",
                "data-bind": "search",
                "style": "flex: 1; min-width: 15rem; padding: 0.5em 0.75em; "
                         "border: 1px solid var(--border); border-radius: var(--cfg-radius); "
                         "background: var(--bg); color: inherit; font: inherit;",
            }),
            h.button({"type": "submit", "class": "btn pri"}, "Add tag"),
            h.button(
                {"type": "button", "class": "btn",
                 "data-on:click": "$tags = []; $search = ''"},
                "Clear",
            ),
        )


    # ─── Active-tags bar (rendered with real Datastar, no data-for needed) ───

    def _tag_debug_row():
        """Shows current tags and search — data-text handles the reactive display."""
        return h.div(
            {"class": "row", "style": "padding: 0.5rem 1.5rem; --space: -1; "
                                      "font-family: var(--font-mono); --type: -1; --contrast: 0.7;"},
            h.span("tags:"),
            h.code({"data-text": "JSON.stringify($tags)"}),
            h.span("search:"),
            h.code({"data-text": "$search || '(empty)'"}),
        )


    # ─── Item card ───────────────────────────────────────────────────────────

    def _item_card(item, match_signal, search_signal):
        """Render one item as a filterable, reorderable card.

        match_signal  — per-item signal holding the current match count (int).
        search_signal — per-item signal holding the searchable text (str).
        Uses data-show to hide zero-match items when a filter is active, and
        data-style:order to sort by relevance (higher matches float up).
        """
        has_filter = "($tags.length > 0 || $search.trim().length > 0)"
        return h.article(
            {"id": item["id"],
             "class": "surface stack",
             "style": "padding: 1rem 1.25rem; border-radius: var(--cfg-radius); "
                      "scroll-margin-top: 6rem; position: relative; --space: 0; "
                      "transition: order 0.4s ease, opacity 0.25s ease;",
             "data-signals": json.dumps({
                 search_signal: item["searchable"],
                 match_signal: 0,
             }),
             "data-effect":
                 f"${match_signal} = [...$tags, $search.trim()]"
                 f".filter(t => t.length > 0 && "
                 f"${search_signal}.toLowerCase().includes(t.toLowerCase())).length",
             "data-show":
                 f"!{has_filter} || ${match_signal} > 0",
             "data-style:order":
                 f"!{has_filter} ? 0 : -${match_signal}"},
            # Match-count badge (visible only while filtering)
            h.span(
                {"class": "badge inf",
                 "style": "position: absolute; top: 1rem; right: 1rem;",
                 "data-show": f"{has_filter} && ${match_signal} > 0",
                 "data-text": f"${match_signal}"},
            ),
            h.h3(h.code(item["name"])),
            h.div({"class": "stack", "style": "--space: -1; --contrast: 0.8;"},
                *item["body"],
            ),
        )


    # ─── Sidebar nav link ────────────────────────────────────────────────────

    def _nav_link(item, match_signal):
        """One sidenav entry. Shows match count when filtering, dims if zero."""
        has_filter = "($tags.length > 0 || $search.trim().length > 0)"
        return h.a(
            {"href": f"#{item['id']}",
             "class": "split",
             "style": "align-items: center; padding: 0.35em 0.75em; "
                      "border-radius: var(--cfg-radius); --contrast: 0.7;",
             "data-class:disabled":
                 f"{has_filter} && ${match_signal} === 0"},
            h.span(item["name"]),
            h.span(
                {"class": "badge inf",
                 "data-show": f"{has_filter}",
                 "data-text": f"${match_signal}"},
            ),
        )


    # ─── Header with theme/size/motion toggles ───────────────────────────────

    def _header(title, subtitle, repo_url=None):
        return h.header(
            {"id": "header", "class": "surface split",
             "style": "padding: 0.75rem 1.5rem; align-items: center;"},
            h.div({"class": "stack", "style": "--space: -2;"},
                h.h4(title),
                h.small({"style": "--contrast: 0.6;"}, subtitle),
            ),
            h.div({"class": "row", "style": "align-items: center;"},
                (h.a({"href": repo_url, "style": "--contrast: 0.7;"}, "github")
                 if repo_url else None),
                h.button(
                    {"class": "btn",
                     "data-on:click": "$_motion = ($_motion + 1) % $_motions.length",
                     "title": "Cycle motion"},
                    "motion: ",
                    h.span({"data-text": "$_motions[$_motion]"}),
                ),
                h.button(
                    {"class": "btn",
                     "data-on:click": "$_theme = ($_theme + 1) % $_themes.length",
                     "title": "Cycle theme"},
                    "theme: ",
                    h.span({"data-text": "$_themes[$_theme] || 'system'"}),
                ),
                h.button(
                    {"class": "btn",
                     "data-on:click": "$_size = ($_size + 1) % $_sizes.length",
                     "title": "Cycle size"},
                    "size: ",
                    h.span({"data-text": "$_sizes[$_size]"}),
                ),
            ),
        )


    # ─── Main generator ──────────────────────────────────────────────────────

    def search_doc(title, subtitle, items, repo_url=None, css_href=CDN_CSS):
        """Build a full searchable documentation page.

        Parameters
        ----------
        title : str
            Page title shown in the header.
        subtitle : str
            Subtitle below the title.
        items : list[dict]
            Each item must have:
              id          str   — URL fragment + signal suffix (alnum/underscore)
              name        str   — display name (rendered in <code> in card + plain in nav)
              searchable  str   — space-separated keywords used for matching
              body        iterable[tag|str] — card contents (description, code blocks…)
        repo_url : str | None
            Optional link shown in header.
        css_href : str
            URL to the Color & Type stylesheet. Defaults to Mike's CDN.
        """
        # Per-item match-count signals. Item ids may contain hyphens (e.g.
        # "data-attr"), but JS identifiers can't — so we sanitize to underscores
        # for the signal names. The DOM id stays as-is so fragment links work.
        def safe_id(item): return item["id"].replace("-", "_")
        def match_sig(item): return f"_match_{safe_id(item)}"
        def search_sig(item): return f"_search_{safe_id(item)}"

        # Root signals (theme/size/motion + search state) go on <body>
        body_signals = {
            "search": "", "tags": [],
            "_theme": 0, "_themes": ["light", "dark", None],
            "_size": 1,  "_sizes": ["sm", "md", "lg"],
            "_motion": 1, "_motions": ["off", "on", "debug"],
        }
        body_attrs = {
            "class": "app",
            "data-signals": json.dumps(body_signals),
            "data-attr:data-ui-theme":  "$_themes[$_theme]",
            "data-attr:data-ui-size":   "$_sizes[$_size]",
            "data-attr:data-ui-motion": "$_motions[$_motion]",
        }

        # Sidebar
        nav = h.nav(
            {"id": "nav", "class": "surface stack",
             "style": "padding: 1rem; --space: -1; min-width: 14rem; "
                      "overflow-y: auto;"},
            h.small("Reference"),
            *[_nav_link(item, match_sig(item)) for item in items],
        )

        # Main column
        main = h.div(
            {"id": "main", "class": "stack",
             "style": "padding: 1.5rem; max-width: 900px; --space: 1;"},
            _search_bar(),
            _tag_debug_row(),
            # Items live in a flex container so data-style:order reorders them.
            h.div(
                {"class": "stack",
                 "style": "display: flex; flex-direction: column; gap: var(--s);"},
                *[_item_card(item, match_sig(item), search_sig(item)) for item in items],
            ),
        )

        aside = h.aside(
            {"id": "aside", "class": "surface stack",
             "style": "padding: 1rem; --space: 0; min-width: 14rem;"},
            h.small("Live state"),
            h.code({"data-text": "'theme: ' + ($_themes[$_theme] || 'system')"}),
            h.code({"data-text": "'size:  ' + $_sizes[$_size]"}),
            h.code({"data-text": "'motion:' + $_motions[$_motion]"}),
            h.hr(),
            h.small("Filter"),
            h.code({"data-text": "'tags:  ' + $tags.length"}),
            h.code({"data-text": "'query: ' + ($search || '∅')"}),
        )

        footer = h.footer(
            {"id": "footer", "class": "surface split",
             "style": "padding: 0.5rem 1.5rem; align-items: center;"},
            h.small({"style": "--contrast: 0.5;"}, title),
            h.small({"style": "--contrast: 0.5;"},
                    f"{len(items)} items · search + filter + reorder via Datastar"),
        )

        return h.html_doc(
            h.head(
                h.meta(charset="utf-8"),
                h.meta(name="viewport", content="width=device-width, initial-scale=1"),
                h.title(title),
                h.Favicon("📚"),
                h.link(rel="stylesheet", href=css_href),
                h.Datastar(),
            ),
            h.body(
                body_attrs,
                _header(title, subtitle, repo_url),
                nav,
                main,
                aside,
                footer,
            ),
        )

    return


if __name__ == "__main__":
    app.run()
