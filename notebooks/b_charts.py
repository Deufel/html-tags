import marimo

__generated_with = "0.22.0"
app = marimo.App()

with app.setup:
    from html import escape

    from a_tags import mk_tag, render, html_doc, Safe, Datastar, MeCSS, Pointer, Highlight, Color_type_css, Favicon

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


@app.class_definition
class Frame:
    def __init__(self, content): self.content = content
    def _repr_html_(self):
        doc = html_doc(
            head(
                title("test"),
                Favicon("🧪"),
                Color_type_css(), MeCSS(), Pointer(), Highlight(), Datastar(),
            ),
            body(self.content),
        )
        return render(iframe(
            srcdoc=str(doc),
            style="width:stretch;height:100svh;border:0",
        ))


@app.class_definition
class Show:
    def __init__(self, content): self.content = content
    def _repr_html_(self):
        doc = html_doc(
            head(
                title("test"),
                Favicon("🧪"),
                Color_type_css(), MeCSS(), Pointer(), Highlight(), Datastar(),
            ),
            body(self.content),
        )
        return render(iframe(
            srcdoc=str(doc),
            style="width:stretch;height:100svh;border:0",
        ))


@app.function
def sparkline(
    values,
    padding: int ,
):
    "values: [y, ...] or [(x, y), ...]"
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
    Frame(chart_card(sparkline(data)))
    return


@app.function
def card_resize(content, *, min_h="100px", min_w="200px"):
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
    Frame(
        div(
        card_resize(sparkline(data)),
        card_resize(sparkline(data))
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
def _(data):
    Frame(card_aspect_resize(sparkline(data)))
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _(sankey):
    # A more complex demo with 4 distinct layers
    complex_flows = [
        # Layer 0: Income sources
        ("Job", "Accounts", 4000),
        ("Side Gig", "Accounts", 1500),
        ("Investment", "Accounts", 800),

        # Layer 1: Accounts splits
        ("Accounts", "Checking", 3000),
        ("Accounts", "Savings", 2500),
        ("Accounts", "Brokerage", 800),

        # Layer 2: Checking → expenses (early exits)
        ("Checking", "Housing", 1500),
        ("Checking", "Food", 600),
        ("Checking", "Transit", 400),
        ("Checking", "Fun", 500),

        # Layer 2-3: Savings path (middle flows)
        ("Savings", "Emergency Fund", 1000),
        ("Savings", "Vacation", 800),
        ("Savings", "Brokerage", 700),  # merges

        # Layer 3: Investment flows continue
        ("Brokerage", "Stocks", 1000),
        ("Brokerage", "Bonds", 500),
        ("Stocks", "Retirement", 1000),  # final sink
        ("Bonds", "Retirement", 500),
    ]

    Frame(sankey(complex_flows))
    return


@app.cell
def _():
    netflix= [
        # Revenue by Region → Revenue
        ("U.S. & Canada", "Revenue", 4224),
        ("Europe, M.East, Africa", "Revenue", 2958),
        ("Latin America", "Revenue", 1165),
        ("Asia-Pacific", "Revenue", 1023),

        # Revenue → Cost of Revenue + Gross Profit
        ("Revenue", "Cost of revenue", 4977),
        ("Revenue", "Gross profit", 4393),

        # Gross Profit → Operating profit + Operating cost (simplified split)
        ("Gross profit", "Operating profit", 2633),
        ("Gross profit", "Operating cost", 1761),   # approx from diagram

        # Operating profit → Net profit + Tax + Interest (simplified)
        ("Operating profit", "Net profit", 2332),
        ("Operating profit", "Tax", 282),
        ("Operating profit", "Interest", 17),      # small negative impact shown

        # Operating cost breakdown (approximate from diagram)
        ("Operating cost", "Marketing", 654),
        ("Operating cost", "Tech & Dev", 702),
        ("Operating cost", "G&A", 404),
    ]
    test_data= [
        # Revenue by Region → Revenue
        ("Beer", "Revenue", 4224),
        ("Wine", "Revenue", 2958),
        ("Spirits", "Revenue", 1165),
        ("Non", "Revenue", 1023),

        # Revenue → Cost of Revenue + Gross Profit
        ("Revenue", "Cost of revenue", 4977),
        ("Revenue", "Gross profit", 4393),

        # Gross Profit → Operating profit + Operating cost (simplified split)
        ("Gross profit", "Operating profit", 2633),
        ("Gross profit", "Operating cost", 1761),   # approx from diagram

        # Operating profit → Net profit + Tax + Interest (simplified)
        ("Operating profit", "Net profit", 2332),
        ("Operating profit", "Tax", 282),
        ("Operating profit", "Interest", 17),      # small negative impact shown

        # Operating cost breakdown (approximate from diagram)
        ("Operating cost", "Marketing", 654),
        ("Operating cost", "Tech & Dev", 702),
        ("Operating cost", "G&A", 404),
    ]
    # Note: Values are in $M (millions). Total Revenue ≈ $9.37B
    return (netflix,)


@app.cell
def _(netflix, sankey):
    Frame(sankey(netflix))
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    def sankey(flows, *, gap=2.0):
        "\"\"
        Improved Sankey: better node ordering + flow sorting to minimize crossings over intermediate nodes.
        "\"\"
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

        # Correct totals
        totals = {}
        for n in nodes:
            in_total = sum(v for _, v in in_edges[n])
            out_total = sum(v for _, v in out_edges[n])
            if not in_edges[n]:
                totals[n] = out_total or 1
            elif not out_edges[n]:
                totals[n] = in_total or 1
            else:
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
                weight = sum(v for s, v in in_edges[n] if s in x_pos) + sum(v for d, v in out_edges[n] if d in x_pos)
                if weight > 0:
                    x_pos[n] = weighted / weight

        # Y-positions (iterative)
        scale_y = (100 - gap * (len(nodes) - 1)) / sum(totals.values())
        y_center = {n: 50.0 for n in nodes}

        for _ in range(250):   # more iterations for stability
            new_y = {}
            for n in nodes:
                weighted = weight = 0.0
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
                # Use weighted position from ALL connected nodes (in + out)
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
                return (avg, -totals[n], str(n))

            col_nodes.sort(key=sort_key)

            # Pack the column
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

        # IMPORTANT: Sort flows by the FINAL y-position of the source node
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

        # Nodes
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
    """)
    return


@app.cell
def _():
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
    from html_tags import g, rect, path, text
    from collections import defaultdict
    from typing import List, Tuple

    Flow = Tuple[str, str, float]   # (source, target, value)

    def sankey(flows: List[Flow], *, gap: float = 2.0, title: str = None):
        """
        Sankey diagram using html-tags + your CSS system.
        Preserves the excellent 1:1 throughput + anti-crossing strategy from your original.
        """
        nodes = set()
        out_edges = defaultdict(list)
        in_edges = defaultdict(list)

        for s, d, v in flows:
            nodes.add(s)
            nodes.add(d)
            out_edges[s].append((d, v))
            in_edges[d].append((s, v))

        # === Throughput calculation (key part of your strategy) ===
        totals = {}
        for n in nodes:
            in_total = sum(v for _, v in in_edges[n])
            out_total = sum(v for _, v in out_edges[n])
            if not in_edges[n]:           # source
                totals[n] = out_total or 1
            elif not out_edges[n]:        # sink
                totals[n] = in_total or 1
            else:                         # intermediate (including 1:1)
                totals[n] = max(in_total, out_total) or 1

        max_val = max((v for _, _, v in flows), default=1)

        # === X positions (iterative) ===
        x_pos = {}
        sources = [n for n in nodes if not in_edges[n]]
        sinks   = [n for n in nodes if not out_edges[n]]
        for s in sources: x_pos[s] = 8.0
        for s in sinks:   x_pos[s] = 92.0

        intermediates = [n for n in nodes if n not in x_pos]
        for _ in range(40):
            for n in intermediates:
                weighted = sum(x_pos.get(s, 50) * v for s, v in in_edges[n] if s in x_pos)
                weighted += sum(x_pos.get(d, 50) * v for d, v in out_edges[n] if d in x_pos)
                weight = sum(v for s, v in in_edges[n] if s in x_pos) + \
                         sum(v for d, v in out_edges[n] if d in x_pos)
                if weight > 0:
                    x_pos[n] = weighted / weight

        # === Y positioning (iterative centering) ===
        scale_y = (100 - gap * (len(nodes) - 1)) / sum(totals.values())
        y_center = {n: 50.0 for n in nodes}

        for _ in range(250):
            new_y = {}
            for n in nodes:
                weighted = weight = 0.0
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

        # === Column grouping + final Y packing ===
        columns = defaultdict(list)
        for n in nodes:
            columns[round(x_pos[n], 3)].append(n)

        final_y = {}
        for col_nodes in columns.values():
            def sort_key(n):
                total_w = weighted = 0.0
                for s, v in in_edges[n]:
                    if s in y_center: weighted += y_center[s] * v; total_w += v
                for d, v in out_edges[n]:
                    if d in y_center: weighted += y_center[d] * v; total_w += v
                avg = weighted / total_w if total_w > 0 else y_center.get(n, 50)
                return (avg, -totals[n], str(n))

            col_nodes.sort(key=sort_key)

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

        # Global vertical centering
        all_mins = [final_y[n] for n in nodes]
        all_maxs = [final_y[n] + totals[n] * scale_y for n in nodes]
        offset = 50 - (min(all_mins) + max(all_maxs)) / 2
        for n in nodes:
            final_y[n] += offset

        # ====================== Build SVG with html-tags ======================
        node_w = 5.5

        # Sort flows by final source y (critical for clean non-crossing)
        sorted_flows = sorted(flows, key=lambda f: (final_y.get(f[0], 50), -f[2], str(f[0]), str(f[1])))

        link_offset_src = {n: 0.0 for n in nodes}
        link_offset_dst = {n: 0.0 for n in nodes}

        link_elements = []
        for s, d, v in sorted_flows:
            x0, x1 = x_pos[s], x_pos[d]
            h = v * scale_y
            y0_base = final_y[s] + link_offset_src[s]
            y1_base = final_y[d] + link_offset_dst[d]

            y0 = y0_base + h / 2
            y1 = y1_base + h / 2

            link_offset_src[s] += h
            link_offset_dst[d] += h

            # Color intensity based on relative value (you can replace with your semantic colors)
            intensity = 0.15 + 0.75 * (v / max_val)
            color = f"oklch(62% {intensity*0.18} 240 / 0.88)"   # or use var(--hue) later

            dx = (x1 - x0) * 0.38

            path_d = (
                f"M {x0 + node_w/2:.2f},{y0 - h/2:.2f} "
                f"C {x0 + dx:.2f},{y0 - h/2:.2f} {x1 - dx:.2f},{y1 - h/2:.2f} {x1 - node_w/2:.2f},{y1 - h/2:.2f} "
                f"L {x1 - node_w/2:.2f},{y1 + h/2:.2f} "
                f"C {x1 - dx:.2f},{y1 + h/2:.2f} {x0 + dx:.2f},{y0 + h/2:.2f} {x0 + node_w/2:.2f},{y0 + h/2:.2f} Z"
            )

            link_elements.append(
                path(d=path_d, fill=color, stroke="transparent")
            )

        # Nodes on top
        node_elements = []
        for n in nodes:
            h = totals[n] * scale_y
            x = x_pos[n] - node_w / 2
            y = final_y[n]

            node_elements.append(
                rect(
                    x=x, y=y, width=node_w, height=h, rx=1.2,
                    fill="var(--bg)",
                    stroke="var(--Border)",
                    stroke_width="0.6"
                )
            )

        # Labels (basic version — easy to enhance)
        label_elements = []
        for n in nodes:
            label_elements.append(
                text(
                    x = x_pos[n] + (node_w/2 + 1.5 if x_pos[n] < 50 else -node_w/2 - 1.5),
                    y = final_y[n] + totals[n]*scale_y/2 + 0.8,
                    text_anchor = "start" if x_pos[n] < 50 else "end",
                    font_size="3.2",
                    fill="var(--contrast(0.92))",
                    font_weight="500"
                )(n)
            )

        diagram = svg(
            width="100%", height="100%",
            viewBox="0 0 100 100",
            preserveAspectRatio="xMidYMid meet",
            style="background: var(--bg);"
        )(
            g()( *link_elements ),
            g()( *node_elements ),
            g()( *label_elements ),
            text(x=50, y=6, text_anchor="middle", font_size="5.5", fill="var(--contrast(0.95))", font_weight="600")(
                title or "Sankey Diagram"
            )
        )

        return div(cls="surface sankey-container")(
            style(" .sankey-container svg { width: 100%; height: auto; max-height: 85vh; } "),
            diagram
        )

    return (sankey,)


@app.cell
def _(sankey):
    h1 = mk_tag("h1")
    p  = mk_tag("p")
    def show_demo_sankey():
        flows = [
            ("US", "Revenue", 20.0),
            ("Europe", "Revenue", 14.5),
            ("LatAm", "Revenue", 5.4),
            ("APAC", "Revenue", 5.4),
            ("Revenue", "Gross Profit", 21.9),
            ("Revenue", "Cost of Revenue", 23.3),
            # ... add the rest from your Netflix image
            ("Gross Profit", "Operating Profit", 13.3),
            ("Operating Profit", "Net Profit", 11.0),
            # etc.
        ]

        diagram = sankey(flows, title="Netflix FY25 Income Statement", gap=1.8)
        return Frame(diagram)

    # Then:
    # show_demo_sankey()
    return


@app.cell
def _():
    return


app._unparsable_cell(
    """
    from collections import namedtuple
    import math as pymath  # for computing plot points

    # ====================== HELPERS ======================

    def Math(*children, display=\"block\", **attrs):
        \"\"\"Convenient wrapper for <math> with automatic namespace handling.\"\"\"
        return tag('math', children, {**attrs, 'display': display, 'xmlns': random'http://www.w3.org/1998/Math/MathML'})


    def Mi(text): return tag('mi')(text)
    def Mn(num):  return tag('mn')(str(num))
    def Mo(op):   return tag('mo')(op)
    def Msup(base, exp): return tag('msup')(base, exp)
    def Mrow(*children): return tag('mrow')(children)
    def Mfrac(num, den): return tag('mfrac')(num, den)


    def function_plot(func, x_min=-5, x_max=5, y_min=None, y_max=None,
                      width=420, height=320, steps=180, label=\"\",
                      hue_shift=0):
        \"\"\"SVG plot of a Python function. Includes grid, axes, curve, and rich foreignObject labels.\"\"\"
        if y_min is None or y_max is None:
            ys = [func(x) for x in [x_min + i*(x_max-x_min)/steps for i in range(steps+1)]]
            y_min = min(ys) * 1.1
            y_max = max(ys) * 1.1

        scale_x = width / (x_max - x_min)
        scale_y = height / (y_max - y_min)

        def svg_x(x): return (x - x_min) * scale_x
        def svg_y(y): return height - (y - y_min) * scale_y

        # Generate curve points
        points = []
        for i in range(steps + 1):
            x = x_min + i * (x_max - x_min) / steps
            y = func(x)
            points.append(f\"{svg_x(x):.1f},{svg_y(y):.1f}\")

        # Grid lines
        grid = []
        for i in range(-4, 5):
            # vertical
            x = svg_x(i)
            grid.append(line(x1=x, x2=x, y1=0, y2=height, stroke=\"var(--border)\", stroke_width=\"0.8\", opacity=\"0.3\"))
            # horizontal
            y = svg_y(i)
            grid.append(line(x1=0, x2=width, y1=y, y2=y, stroke=\"var(--border)\", stroke_width=\"0.8\", opacity=\"0.3\"))

        # Axes
        axes = [
            line(x1=svg_x(0), x2=svg_x(0), y1=0, y2=height, stroke=\"var(--contrast(0.6))\", stroke_width=\"2\"),
            line(x1=0, x2=width, y1=svg_y(0), y2=svg_y(0), stroke=\"var(--contrast(0.6))\", stroke_width=\"2\"),
        ]

        # Rich foreignObject inside the SVG (this is the magic!)
        foreign = foreignObject(
            x=width-160, y=12, width=148, height=110,
            style=\"overflow:visible; font-size:13px;\"
        )(
            div(cls=\"surface\", style=f\"padding:8px; border-radius:6px; --hue-shift:{hue_shift}; height:100%;\")(
                Math(display=\"inline\")(
                    Mrow(Mi(\"y\"), Mo(\"=\"), label)
                ),
                div(style=\"margin-top:6px; font-size:11px; opacity:0.85\")(
                    f\"Domain: [{x_min}, {x_max}]\"
                ),
                sparkline([func(x_min + i*(x_max-x_min)/8) for i in range(9)], 
                          label=\"Sample\", trend=\"suc\" if func(0) > 0 else \"inf\")
            )
        )

        return svg(
            width=width, height=height,
            viewBox=f\"0 0 {width} {height}\",
            style=\"background:var(--bg); border:1px solid var(--border); border-radius:8px;\"
        )(
            g()(*grid),
            g()(*axes),
            path(
                d=f\"M {' '.join(points)}\",
                fill=\"none\",
                stroke=f\"oklch(55% 0.22 calc(var(--cfg-color-hue) + {hue_shift}))\",
                stroke_width=\"3.5\",
                stroke_linecap=\"round\"
            ),
            text(x=width-18, y=height-12, text_anchor=\"end\", fill=\"var(--contrast(0.7))\", font_size=\"13\")(label or \"f(x)\"),
            foreign
        )


    # ====================== DEMO PAGE ======================
    def demo_math_svg_page():
        content = div(cls=\"surface\", style=\"padding:2.5rem; max-width:1280px; margin:0 auto\")(
            h1(style=\"--type:2.5\")(\"html-tags + Unified CSS = Magic Math Visuals\"),
            p(cls=\"note\", style=\"max-width:70ch\")(
                \"This page proves the unique power of your stack: \",
                strong(\"HTML + MathML + SVG + foreignObject\"),
                \" all composed in the same Python tree. \",
                \"Every color, surface, and label respects the exact same \",
                code(\"--hue\"), code(\"--color\"), code(\"--depth\"), \" system. \",
                \"No other library makes this seamless.\"
            ),

            # Example 1: Quadratic
            div(cls=\"row\", style=\"gap:2rem; margin-bottom:3rem\")(
                div(style=\"flex:1\")(
                    h2()(\"Quadratic\"),
                    Math(display=\"block\")(
                        Mrow(Mi(\"y\"), Mo(\"=\"), Msup(Mi(\"x\"), Mn(2)))
                    ),
                    p(\"Classic parabola. The foreignObject inside the SVG contains the same MathML + a live sparkline.\")
                ),
                function_plot(
                    lambda x: x**2,
                    x_min=-4, x_max=4, y_min=0, y_max=18,
                    label=Mrow(Mi(\"x\"), Msup(Mo(\"²\"), Mn(\"\")))
                )
            ),

            # Example 2: Sine
            div(cls=\"row\", style=\"gap:2rem; margin-bottom:3rem\")(
                div(style=\"flex:1\")(
                    h2()(\"Sine Wave\"),
                    Math(display=\"block\")(
                        Mrow(Mi(\"y\"), Mo(\"=\"), Mo(\"sin\"), Mo(\"(\"), Mi(\"x\"), Mo(\")\"))
                    )
                ),
                function_plot(
                    pymath.sin,
                    x_min=-2*pymath.pi, x_max=2*pymath.pi, y_min=-1.3, y_max=1.3,
                    label=Mrow(Mo(\"sin\"), Mo(\"(\"), Mi(\"x\"), Mo(\")\")),
                    hue_shift=80
                )
            ),

            # Example 3: Exponential
            div(cls=\"row\", style=\"gap:2rem; margin-bottom:3rem\")(
                div(style=\"flex:1\")(
                    h2()(\"Exponential Growth\"),
                    Math(display=\"block\")(
                        Mrow(Mi(\"y\"), Mo(\"=\"), Mi(\"e\"), Msup(Mo(\"^\"), Mi(\"x\")))
                    )
                ),
                function_plot(
                    pymath.exp,
                    x_min=-2, x_max=3.5, y_min=0, y_max=35,
                    label=Mrow(Mi(\"e\"), Msup(Mo(\"^\"), Mi(\"x\"))),
                    hue_shift=140
                )
            ),

            # Example 4: Linear with annotation
            div(cls=\"row\", style=\"gap:2rem\")(
                div(style=\"flex:1\")(
                    h2()(\"Linear Function\"),
                    Math(display=\"block\")(
                        Mrow(Mi(\"y\"), Mo(\"=\"), Mn(\"2\"), Mi(\"x\"), Mo(\"+\"), Mn(\"1\"))
                    )
                ),
                function_plot(
                    lambda x: 2*x + 1,
                    x_min=-4, x_max=4, y_min=-9, y_max=11,
                    label=Mrow(Mn(\"2\"), Mi(\"x\"), Mo(\"+\"), Mn(\"1\")),
                    hue_shift=-60
                )
            ),

            div(style=\"margin-top:3rem; text-align:center; opacity:0.7; font-size:13px\")(
                \"Change the page theme or --hue in the controls above — watch the entire page (MathML, SVG curves, surfaces, sparklines) update instantly.\"
            )
        )

        return Frame(
            div(cls=\"surface\", style=\"padding:1rem\")(
                Color_type_css(),
                MeCSS(),
                Pointer(),
                Highlight(),
                Datastar(),
                content
            )
        )


    # To display:
    demo_math_svg_page()
    """,
    name="_"
)


@app.cell
def _():
    strong = mk_tag("strong")
    code = mk_tag("code")
    h2 = mk_tag("h2")
    tag = mk_tag("tag")
    line = mk_tag("line")
    foreignObject = mk_tag("foreignObject")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
