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


@app.cell
def _():
    return


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
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
