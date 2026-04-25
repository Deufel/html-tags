import marimo

__generated_with = "0.22.0"
app = marimo.App()

with app.setup:
    from html import escape

    from a_tags import mk_tag, render, html_doc, Safe, Datastar, MeCSS, Pointer, Highlight, Color_type_css, Favicon, is_tag

    head = mk_tag("head")
    body = mk_tag("body")
    title = mk_tag("title")
    iframe = mk_tag("iframe")
    div = mk_tag("div")
    svg = mk_tag("svg")
    style = mk_tag("style")
    polyline = mk_tag("polyline")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    return


@app.class_definition
class Show:
    def __init__(self, content): self.content = content if is_tag(content) else Safe(str(content))
    def _repr_html_(self):
        doc = html_doc(
            head(title("test"), Favicon("🧪"), Color_type_css(), MeCSS(), Pointer(), Highlight(), Datastar()),
            body(self.content))
        return render(iframe(srcdoc=str(doc), style="width:stretch;height:stretch;border:0"))


@app.function
def sparkline(
    values,  # list of vales to plot in a svg 
):
    "returns a dimensionless lien chart, resizable without line width distortion"
    pts = list(enumerate(values)) if not isinstance(values[0], tuple) else values
    xs, ys = zip(*pts)
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    sx = lambda x: (x - x0) / (x1 - x0) * 100 if x1 != x0 else 50
    sy = lambda y: 100 - (y - y0) / (y1 - y0) * 100 if y1 != y0 else 50
    coords = " ".join(f"{sx(x):.2f},{sy(y):.2f}" for x, y in pts)
    return svg(
        polyline(points=coords, fill="none", stroke="var(--bg)",
                 style="--color: 0.5; vector-effect: non-scaling-stroke",
                 stroke_width="2", stroke_linecap="round", stroke_linejoin="round"),
        viewBox="0 0 100 100",
        preserveAspectRatio="none",
        cls="sparkline",
    )


@app.cell
def _():
    import random
    data = [random.randint(10, 100) for _ in range(20)]
    return (data,)


@app.function
def chart_card(chart, *, height="130px"):
    css = f"""
    me {{ padding: var(--s); border-radius: var(--cfg-radius);
          height: {height}; aspect-ratio:2 ; display: grid; resize: both;}}
    me > svg {{ width: stretch; height: stretch; }}
    """
    return div(cls="card surface", style="--hue-shift: 45; resize: both")(
        style(css),
        chart,  # no figure wrapper
    )


@app.cell
def _(data):
    Show(chart_card(sparkline(data)))
    return


@app.function
def card_size_resize(content, *, min_h="100px", min_w="200px"):
    """Resizable container for flexible layouts (dialogs, expandable panels).
    Content stretches to fill; use preserveAspectRatio="none" in SVGs."""
    css = f"""
    me {{ padding: var(--s); border-radius: var(--cfg-radius);
          min-height: {min_h}; min-width: {min_w};
          height: stretch; width: stretch;
          resize: both; overflow: hidden;
          display: grid; }}
    me > svg {{ width: stretch; height: stretch; }}
    """
    return div(cls="card surface")(
        style(css),
        content,
    )


@app.cell
def _(data):
    Show(
        div(
        card_aspect_resize(sparkline(data))
        )
    )
    return


@app.function
def card_aspect_resize(content, *, ratio="3/2", base_h="150px"):
    css = f"""
    me {{
        padding: var(--s);
        border-radius: var(--cfg-radius);
        height: {base_h};
        aspect-ratio: {ratio};
        resize: both;
        overflow: hidden;
        display: grid;
    }}
    me > svg {{ width: stretch; height: stretch; }}
    """
    return div(cls="card surface")(style(css), content)


@app.cell
def _():
    # testing Not ready yet


    def _sankey(flows, *, gap=2.0):
        """
        Sankey with explicit 1:1 throughput node handling.
        Every node (including perfect passthrough intermediates) is fully respected
        in both positioning and flow ordering. This eliminates flows crossing over
        intermediate nodes.
        """
        from collections import defaultdict

        nodes = set()
        out_edges = defaultdict(list)
        in_edges = defaultdict(list)
        max_val = max((v for _, _, v in flows), default=1)

        for s, d, v in flows:
            nodes.add(s)
            nodes.add(d)
            out_edges[s].append((d, v))
            in_edges[d].append((s, v))

        # === EXPLICIT 1:1 THROUGHPUT HANDLING ===
        totals = {}
        for n in nodes:
            in_total = sum(v for _, v in in_edges[n])
            out_total = sum(v for _, v in out_edges[n])
            if not in_edges[n]:           # pure source
                totals[n] = out_total or 1
            elif not out_edges[n]:        # pure sink
                totals[n] = in_total or 1
            else:                         # intermediate (including 1:1)
                # For 1:1 nodes we still use the actual flow amount that passes through
                totals[n] = max(in_total, out_total) or 1

        # X-positions
        x_pos = {}
        sources = [n for n in nodes if not in_edges[n]]
        sinks   = [n for n in nodes if not out_edges[n]]
        for s in sources: x_pos[s] = 4.0
        for s in sinks:   x_pos[s] = 96.0

        intermediates = [n for n in nodes if n not in x_pos]
        for _ in range(40):
            for n in intermediates:
                weighted = sum(x_pos.get(s, 50) * v for s, v in in_edges[n] if s in x_pos)
                weighted += sum(x_pos.get(d, 50) * v for d, v in out_edges[n] if d in x_pos)
                weight = sum(v for s, v in in_edges[n] if s in x_pos) + \
                         sum(v for d, v in out_edges[n] if d in x_pos)
                if weight > 0:
                    x_pos[n] = weighted / weight

        # Y-positions (iterative centering)
        scale_y = (100 - gap * (len(nodes) - 1)) / sum(totals.values())
        y_center = {n: 50.0 for n in nodes}

        for _ in range(250):
            new_y = {}
            for n in nodes:
                weighted = weight = 0.0
                # 1:1 nodes get equal pull from in + out
                for s, v in in_edges[n]:
                    if s in y_center:
                        weighted += y_center[s] * v
                        weight += v
                for d, v in out_edges[n]:
                    if d in y_center:
                        weighted += y_center[d] * v
                        weight += v
                new_y[n] = weighted / weight if weight > 0 else y_center[n]
            y_center = new_y

        # Column grouping
        columns = defaultdict(list)
        for n in nodes:
            columns[round(x_pos[n], 3)].append(n)

        final_y = {}
        for col_nodes in columns.values():
            def sort_key(n):
                # Stronger 1:1-aware key: average position from ALL connected nodes
                total_w = 0.0
                weighted = 0.0
                for s, v in in_edges[n]:
                    if s in y_center:
                        weighted += y_center[s] * v
                        total_w += v
                for d, v in out_edges[n]:
                    if d in y_center:
                        weighted += y_center[d] * v
                        total_w += v
                avg = weighted / total_w if total_w > 0 else y_center.get(n, 50)
                return (avg, -totals[n], str(n))   # larger nodes preferred in ties

            col_nodes.sort(key=sort_key)

            # Pack column
            current_y = 0.0
            col_pos = {}
            for n in col_nodes:
                h = totals[n] * scale_y
                col_pos[n] = current_y + h / 2
                current_y += h + gap

            col_total = current_y - gap
            offset = 50 - col_total / 2

            for n in col_nodes:
                final_y[n] = col_pos[n] + offset - totals[n] * scale_y / 2

        # Global centering
        mins = [final_y[n] for n in nodes]
        maxs = [final_y[n] + totals[n] * scale_y for n in nodes]
        offset = 50 - (min(mins) + max(maxs)) / 2
        for n in nodes:
            final_y[n] += offset

        # ====================== SVG ======================
        node_w = 5.2
        svg_parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" preserveAspectRatio="none">']

        # Critical: flows sorted by FINAL source y-position (this prevents crossing over 1:1 nodes)
        sorted_flows = sorted(flows, key=lambda f: (final_y.get(f[0], 50), -f[2], str(f[0]), str(f[1])))

        link_offset_src = {n: 0.0 for n in nodes}
        link_offset_dst = {n: 0.0 for n in nodes}

        for s, d, v in sorted_flows:
            x0, x1 = x_pos[s], x_pos[d]
            h = v * scale_y
            y0 = final_y[s] + link_offset_src[s] + h / 2
            y1 = final_y[d] + link_offset_dst[d] + h / 2

            link_offset_src[s] += h
            link_offset_dst[d] += h

            color = 0.12 + 0.68 * (v / max_val)
            dx = (x1 - x0) * 0.35

            path = (
                f'M {x0 + node_w/2:.2f},{y0 - h/2:.2f} '
                f'C {x0 + dx:.2f},{y0 - h/2:.2f} {x1 - dx:.2f},{y1 - h/2:.2f} {x1 - node_w/2:.2f},{y1 - h/2:.2f} '
                f'L {x1 - node_w/2:.2f},{y1 + h/2:.2f} '
                f'C {x1 - dx:.2f},{y1 + h/2:.2f} {x0 + dx:.2f},{y0 + h/2:.2f} {x0 + node_w/2:.2f},{y0 + h/2:.2f} Z'
            )
            svg_parts.append(f'<path d="{path}" fill="var(--bg)" style="--color: {color:.3f}"/>')

        # Nodes on top
        for n in nodes:
            h = totals[n] * scale_y
            x = x_pos[n] - node_w / 2
            svg_parts.append(
                f'<rect x="{x:.2f}" y="{final_y[n]:.2f}" width="{node_w:.2f}" height="{h:.2f}" rx="0.8" '
                f'fill="var(--bg)" stroke="#0a0a0a" stroke-width="0.45" style="--color: 0.58"/>'
            )

        svg_parts.append('</svg>')

        return div(cls="sankey-centered")(
            style("me, me svg { width: 100%; height: 100%; display: block; }"),
            Safe('\n'.join(svg_parts))
        )

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## thing
    """)
    return


@app.cell
def _():
    """Resume page built from composable html_tags components.

    Each component is a small function returning a tag tree. Component-owned
    styles live in a scoped `Style("me { ... }")` block at the top of the
    returned `Div`, per the colorNtype convention.

    Global CSS (cascade layers, color/type/space formulas, .surface/.btn/.tag,
    layout primitives like .split/.cluster/.stack) is loaded separately via
    `Color_type_css()` — components reference those classes and tokens
    (`--s`, `--type`, `--border`, `--Border`, `--cfg-radius`) without redefining
    them.
    """

    from html_tags import (
        # core
        tag, mk_tag, render, html_doc, Safe,
        # extras
        Datastar, MeCSS, Pointer, Color_type_css, Favicon, Layout,
    )

    # ── element constructors ────────────────────────────────────────────────
    # (mk_tag is auto-called by __getattr__ on the package; listing here for clarity)
    Div      = mk_tag('div')
    Span     = mk_tag('span')
    Section  = mk_tag('section')
    Article  = mk_tag('article')
    Header   = mk_tag('header')
    H1       = mk_tag('h1')
    H2       = mk_tag('h2')
    H3       = mk_tag('h3')
    P        = mk_tag('p')
    Ul       = mk_tag('ul')
    Ol       = mk_tag('ol')
    Li       = mk_tag('li')
    I        = mk_tag('i')
    Button   = mk_tag('button')
    Dialog   = mk_tag('dialog')
    Textarea = mk_tag('textarea')
    Style    = mk_tag('style')
    Svg           = mk_tag('svg')
    Path          = mk_tag('path')
    Rect          = mk_tag('rect')
    Circle        = mk_tag('circle')
    Line          = mk_tag('line')
    G             = mk_tag('g')
    ForeignObject = mk_tag('foreignObject')


    # ── icons (lucide) ──────────────────────────────────────────────────────
    def _icon(*paths, size=16):
        """Wrap lucide-style path elements in a configured <svg>."""
        return Svg(
            *paths,
            xmlns="http://www.w3.org/2000/svg",
            width=size, height=size, viewBox="0 0 24 24",
            fill="none", stroke="currentColor", stroke_width=2,
            stroke_linecap="round", stroke_linejoin="round",
        )

    def IconMail(size=16):
        return _icon(
            Rect(x=2, y=4, width=20, height=16, rx=2),
            Path(d="m22 7-10 5L2 7"),
            size=size,
        )

    def IconPin(size=16):
        return _icon(
            Path(d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"),
            Circle(cx=14, cy=10, r=3),
            size=size,
        )

    def IconNotebook(size=24):
        return _icon(
            Path(d="M13.4 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-7.4"),
            Path(d="M2 6h4"), Path(d="M2 10h4"),
            Path(d="M2 14h4"), Path(d="M2 18h4"),
            Path(d="M21.378 5.626a1 1 0 1 0-3.004-3.004l-5.01 5.012a2 2 0 0 0-.506.854l-.837 2.87a.5.5 0 0 0 .62.62l2.87-.837a2 2 0 0 0 .854-.506z"),
            size=size,
        )

    def IconGithub(size=24):
        return _icon(
            Path(d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"),
            Path(d="M9 18c-4.51 2-5-2-7-2"),
            size=size,
        )

    def IconLinkedIn(size=24):
        return _icon(
            Path(d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"),
            Rect(width=4, height=12, x=2, y=9),
            Circle(cx=4, cy=4, r=2),
            size=size,
        )

    def IconPrinter(size=24):
        return _icon(
            Path(d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"),
            Path(d="M6 9V3a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v6"),
            Rect(x=6, y=14, width=12, height=8, rx=1),
            size=size,
        )

    def IconTheme(size=24):
        return _icon(
            Path(d="M12 2v2"),
            Path(d="M14.837 16.385a6 6 0 1 1-7.223-7.222c.624-.147.97.66.715 1.248a4 4 0 0 0 5.26 5.259c.589-.255 1.396.09 1.248.715"),
            Path(d="M16 12a4 4 0 0 0-4-4"),
            Path(d="m19 5-1.256 1.256"),
            Path(d="M20 12h2"),
            size=size,
        )

    def IconTextSize(size=24):
        return _icon(
            Path(d="m15 16 2.536-7.328a1.02 1.02 1 0 1 1.928 0L22 16"),
            Path(d="M15.697 14h5.606"),
            Path(d="m2 16 4.039-9.69a.5.5 0 0 1 .923 0L11 16"),
            Path(d="M3.304 13h6.392"),
            size=size,
        )

    def IconClose(size=24):
        return _icon(
            Path(d="M18 6 6 18"),
            Path(d="m6 6 12 12"),
            size=size,
        )


    # ── primitives ──────────────────────────────────────────────────────────
    def Tag(text, *, cls_extra="", hue_shift=None, color=None):
        """A pill tag — uses the global `.tag.surface` class."""
        style_parts = []
        if hue_shift is not None: style_parts.append(f"--hue-shift:{hue_shift}")
        if color     is not None: style_parts.append(f"--color:{color}")
        kw = {"cls": f"tag surface {cls_extra}".strip()}
        if style_parts: kw["style"] = ";".join(style_parts)
        return Span(text, **kw)


    def Contact(icon, text):
        """An icon + text contact row used in the header."""
        return Span(icon, text, cls="contact")


    # ── header ──────────────────────────────────────────────────────────────
    # Timeline: single lane, month precision, fluid SVG, non-scaling strokes.
    #
    # Input dates are (year, month) tuples — month is 1-indexed. End is exclusive
    # (so (2015, 6) means "up to and including May 2015"). The timeline spans
    # from `start` to `end` (also (year, month) tuples).
    #
    # Architecture: SVG draws shapes only — lane bg, grid lines, period rects,
    # axis line — using viewBox "0 0 100 H" with preserveAspectRatio="none" so
    # x stretches to fill the container while non-scaling-stroke keeps strokes
    # 1px crisp. Labels (period names + year ticks) are HTML overlaid via
    # absolute positioning + `left: X%`, so their typography is independent of
    # the SVG stretch and gets ellipsis truncation, the --type cascade, etc.
    #
    # (Earlier draft used <foreignObject> for labels, but FO content inherits
    # the SVG's transform when preserveAspectRatio="none" is set, which stretches
    # the text horizontally. The HTML overlay approach sidesteps that entirely.)

    def _months_between(a, b):
        """Months from (yr, mo) tuple `a` to `b`. Result can be negative."""
        return (b[0] - a[0]) * 12 + (b[1] - a[1])

    def _x_pos(date, start, total_months):
        """Map a (yr, mo) date into [0, 100] viewBox-x units."""
        return _months_between(start, date) / total_months * 100

    def TimelineBlock(label, *, frm, to, hue, start, total_months, lane_y=2, lane_h=52):
        """A single period — emits TWO things:
           - an SVG <g> with just the rect (caller places it inside the <svg>)
           - an HTML <div> label (caller places it inside the .labels overlay)
        Returns (svg_group, html_label).
        """
        x = _x_pos(frm, start, total_months)
        w = _x_pos(to,  start, total_months) - x
        svg_group = G(
            Rect(
                x=f"{x:.3f}", y=str(lane_y),
                width=f"{w:.3f}", height=str(lane_h),
                rx="1",
                vector_effect="non-scaling-stroke",
            ),
            cls="period",
            style=f"--h:{hue}",
        )
        html_label = Div(
            label,
            cls="period-label",
            style=f"--h:{hue};left:{x:.3f}%;width:{w:.3f}%",
        )
        return svg_group, html_label

    def Timeline(blocks, *, start, end, lane_h=56, axis_h=24):
        """Single-lane month-precision timeline.

        Strategy: SVG handles shapes (background, grid, period rects) with a
        fluid `preserveAspectRatio="none"` viewBox so it stretches to any
        container width while non-scaling-stroke keeps lines crisp. Labels
        (period names, year ticks) are rendered as HTML positioned via `left: X%`
        so their typography is not distorted by the SVG stretch.

        Args:
            blocks: list of dicts: {label, frm: (yr, mo), to: (yr, mo), hue: int}
            start:  (yr, mo) tuple — left edge of timeline
            end:    (yr, mo) tuple — right edge (exclusive)
            lane_h: lane height in viewBox-y units (and CSS px for the lane)
            axis_h: tick axis height below the lane
        """
        total_months = _months_between(start, end)
        if total_months <= 0:
            raise ValueError(f"end must be after start (got {start} → {end})")

        # Minor (monthly) gridlines: every month boundary, skip year boundaries.
        minor_lines = []
        for m in range(1, total_months):
            mo = (start[1] - 1 + m) % 12 + 1
            if mo == 1: continue   # year boundary -> major
            x = m / total_months * 100
            minor_lines.append(
                Line(x1=f"{x:.3f}", y1="0", x2=f"{x:.3f}", y2=str(lane_h),
                     vector_effect="non-scaling-stroke")
            )

        # Major (yearly) gridlines + which years get tick labels (every 5).
        major_lines = []
        tick_labels = []
        cur_y = start[0] if start[1] == 1 else start[0] + 1
        end_y = end[0]   if end[1]   == 1 else end[0]
        while cur_y <= end_y:
            m = _months_between(start, (cur_y, 1))
            if 0 <= m <= total_months:
                x = m / total_months * 100
                major_lines.append(
                    Line(x1=f"{x:.3f}", y1="0", x2=f"{x:.3f}", y2=str(lane_h),
                         vector_effect="non-scaling-stroke")
                )
                if cur_y % 5 == 0:
                    tick_labels.append((cur_y, x))
            cur_y += 1

        # Build period SVG groups + HTML labels in parallel.
        svg_groups = []
        html_labels = []
        for b in blocks:
            sg, lbl = TimelineBlock(start=start, total_months=total_months, **b)
            svg_groups.append(sg)
            html_labels.append(lbl)

        css = f"""
        me {{
          display: block;
          width: 100%;
          position: relative;
          aspect-ratio: var(--tl-aspect, 18 / 1);
        }}
        me .stage {{
          position: relative;
          width: 100%;
          height: 100%;
        }}
        me svg {{
          position: absolute;
          inset: 0;
          width: 100%;
          height: 100%;
          display: block;
        }}
        me .lane-bg    {{ fill: var(--bg); }}
        me .grid-major {{ stroke: var(--border); fill: none; }}
        me .grid-minor {{ stroke: var(--border); fill: none; opacity: 0.4; stroke-dasharray: 2 4; }}
        me .axis-line  {{ stroke: var(--Border); fill: none; }}
        me .period rect {{
          fill:   oklch(58% 0.16 var(--h, 220));
          stroke: oklch(38% 0.20 var(--h, 220));
        }}
        me .period:hover rect {{
          fill:   oklch(65% 0.20 var(--h, 220));
        }}

        /* Label overlay: positioned in the lane's coordinate space. */
        me .labels {{
          position: absolute;
          inset: 0;
          pointer-events: none;
        }}
        me .lane-labels {{
          position: absolute;
          left: 0; right: 0;
          top: 0;
          height: calc(100% * {lane_h} / {lane_h + axis_h});
        }}
        me .period-label {{
          position: absolute;
          top: 0; bottom: 0;
          display: flex;
          align-items: center;
          padding: 0 0.6em;
          font-family: var(--font-body);
          --type: -1;
          font-weight: 600;
          color: oklch(15% 0.05 var(--h, 220));
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          box-sizing: border-box;
        }}

        me .tick-labels {{
          position: absolute;
          left: 0; right: 0;
          top: calc(100% * {lane_h} / {lane_h + axis_h});
          height: calc(100% * {axis_h} / {lane_h + axis_h});
        }}
        me .tick-label {{
          position: absolute;
          top: 4px;
          transform: translateX(-50%);
          font-family: var(--font-mono);
          --type: -2;
          --contrast: 0.55;
          white-space: nowrap;
        }}
        """

        h = lane_h + axis_h
        return Div(
            Style(css),
            Div(
                Svg(
                    Rect(cls="lane-bg", x="0", y="0", width="100", height=str(lane_h),
                         vector_effect="non-scaling-stroke"),
                    G(*minor_lines, cls="grid-minor"),
                    G(*major_lines, cls="grid-major"),
                    *svg_groups,
                    Line(cls="axis-line", x1="0", y1=str(lane_h), x2="100", y2=str(lane_h),
                         vector_effect="non-scaling-stroke"),
                    viewBox=f"0 0 100 {h}",
                    preserveAspectRatio="none",
                ),
                Div(
                    Div(*html_labels, cls="lane-labels"),
                    Div(
                        *(Div(str(yr), cls="tick-label", style=f"left:{x:.3f}%")
                          for yr, x in tick_labels),
                        cls="tick-labels",
                    ),
                    cls="labels",
                ),
                cls="stage",
            ),
            cls="timeline",
        )

    def ResumeHeader(*, name, email, location, blurb, timeline):
        return tag('header')(
            Div(
                Div(H1(name), cls="cluster"),
                Div(
                    Contact(IconMail(), email),
                    Contact(IconPin(), location),
                    cls="cluster",
                ),
                cls="header-top split",
            ),
            P(blurb, cls="blurb"),
            timeline,
            id="header",
        )



    # ── example assembly ────────────────────────────────────────────────────
    timeline = Timeline(
        blocks=[
            {"label": "B.S. EE — Purdue",
             "frm": (2010, 8), "to": (2014, 12), "hue": 140},
            {"label": "Primera Engineers",
             "frm": (2015, 6), "to": (2021, 8),  "hue": 60},
            {"label": "M.S. Data Science — NU",
             "frm": (2021, 9), "to": (2023, 3),  "hue": 200},
            {"label": "Superior Beverage",
             "frm": (2023, 3), "to": (2024, 2),  "hue": 260},
            {"label": "Event OS",
             "frm": (2025, 1), "to": (2026, 2),  "hue": 320},
        ],
        start=(2010, 1), end=(2026, 4),
    )

    return (
        Color_type_css,
        Datastar,
        Favicon,
        MeCSS,
        Pointer,
        Safe,
        html_doc,
        render,
    )


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
