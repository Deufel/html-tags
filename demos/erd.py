import marimo

__generated_with = "0.22.0"
app = marimo.App()


@app.cell
def _():
    """Backend ERD generator.

    Reads a SQLite database, introspects its schema via PRAGMA, and emits a
    single static HTML file with an SVG entity-relationship diagram. No
    JavaScript, no build step — just html_tags composing HTML and SVG
    directly from Python data.

    Usage:
        python build_erd.py path/to/database.sqlite  [output.html]

    Design:
    - Tables laid out in depth layers (root tables → dependents, left to right).
    - Each column is a row inside the table rect with a known y-coordinate.
    - Foreign keys render as Catmull-Rom curves (the /6 formula, C1-continuous)
      connecting the exact FK row to the exact referenced PK row.
    """
    import sqlite3
    import sys
    import html_tags as h


    # ── PRAGMA introspection ─────────────────────────────────────────────────

    def introspect(db_path):
        """Return {table_name: {'cols': [(name, type, pk, notnull), ...],
                                'fks': [(from_col, ref_table, to_col), ...]}}"""
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' "
                  "AND name NOT LIKE 'sqlite_%' ORDER BY name")
        tables = [r[0] for r in c.fetchall()]

        schema = {}
        for t in tables:
            c.execute(f"PRAGMA table_info({t})")
            cols = [(name, (ctype or '').upper() or '—', bool(pk), bool(notnull))
                    for _cid, name, ctype, notnull, _dflt, pk in c.fetchall()]

            c.execute(f"PRAGMA foreign_key_list({t})")
            fks = [(from_col, ref_table, to_col)
                   for _id, _seq, ref_table, from_col, to_col, *_ in c.fetchall()]

            schema[t] = {'cols': cols, 'fks': fks}

        conn.close()
        return schema


    # ── Layout: assign each table a (x, y) based on dependency depth ─────────

    def layer_tables(schema):
        """Longest-path layering: a table's layer = 1 + max(layer of tables it FKs to).
        Root tables (no outgoing FKs) land in layer 0.
        Cycles are broken by treating already-visited tables as depth 0.
        """
        layer = {}

        def depth(t, seen):
            if t in layer: return layer[t]
            if t in seen:  return 0                 # cycle — bail
            seen = seen | {t}
            fks = schema[t]['fks']
            if not fks:
                layer[t] = 0
            else:
                layer[t] = 1 + max(depth(r, seen) for _f, r, _to in fks
                                   if r in schema)
            return layer[t]

        for t in schema:
            depth(t, set())
        return layer


    # Dimensions — pure constants, tweak freely
    COL_GAP    = 80       # horizontal gap between layers
    TABLE_W    = 240      # table rect width
    ROW_H      = 22       # height of each column row
    HEADER_H   = 32       # height of the table's header (name) row
    TABLE_GAP  = 24       # vertical gap between stacked tables
    MARGIN     = 40       # outer margin


    def layout(schema):
        """Compute {table: {x, y, w, h, col_y: {col_name: y}}} for every table."""
        layer = layer_tables(schema)

        # Bucket tables by layer
        by_layer = {}
        for t, L in layer.items():
            by_layer.setdefault(L, []).append(t)

        # Reorder tables within each layer by barycenter of their connections:
        # a table's position is pulled toward the average position of tables
        # in adjacent layers that it connects to (incoming or outgoing FK).
        # This is a single-pass Sugiyama-style crossing reduction — not optimal,
        # but much better than alphabetical.
        def adjacent_tables(t):
            """Tables connected by FK, in either direction."""
            neighbors = set()
            for _from, ref, _to in schema[t]['fks']:
                if ref in schema: neighbors.add(ref)
            for other, info in schema.items():
                if any(ref == t for _f, ref, _to in info['fks']):
                    neighbors.add(other)
            return neighbors

        # Seed each layer with alphabetical order, then sweep a few times
        # pulling each table toward the mean index of its neighbors.
        order = {L: sorted(ts) for L, ts in by_layer.items()}
        for _sweep in range(4):
            for L in sorted(order):
                def score(t):
                    idxs = []
                    for nb in adjacent_tables(t):
                        nb_layer = layer[nb]
                        if nb in order[nb_layer]:
                            idxs.append(order[nb_layer].index(nb))
                    return sum(idxs) / len(idxs) if idxs else 0
                order[L] = sorted(order[L], key=score)

        positions = {}
        max_layer = max(layer.values()) if layer else 0

        for L in range(max_layer + 1):
            tables_in_layer = order.get(L, [])
            x = MARGIN + L * (TABLE_W + COL_GAP)
            y_cursor = MARGIN
            for t in tables_in_layer:
                cols = schema[t]['cols']
                h_total = HEADER_H + len(cols) * ROW_H
                col_y = {}
                for i, (name, _ctype, _pk, _nn) in enumerate(cols):
                    col_y[name] = y_cursor + HEADER_H + i * ROW_H + ROW_H / 2
                positions[t] = {
                    'x': x, 'y': y_cursor, 'w': TABLE_W, 'h': h_total,
                    'col_y': col_y,
                }
                y_cursor += h_total + TABLE_GAP

        return positions


    # ── Catmull-Rom → cubic Bézier (the /6 formula) ──────────────────────────
    # For segment p1→p2 in polyline [p0,p1,p2,p3]:
    #   cp1 = p1 + (p2 - p0) / 6
    #   cp2 = p2 - (p3 - p1) / 6
    # The first and last points in the input are treated as PHANTOMS — they
    # are not drawn, but they shape the tangent at the real endpoints. Draw
    # segments from index 1 to len-2. Place phantoms horizontally outside the
    # real endpoints to enforce horizontal entry/exit tangents.

    def catmull_rom_path(points):
        """Render a Catmull-Rom spline as an SVG path string.

        `points` includes phantom endpoints at index 0 and -1; these shape
        tangents but are not drawn through.
        """
        if len(points) < 4:
            return ''
        # Draw from points[1] through points[-2]. Move to the first real point.
        d = [f"M {points[1][0]:.1f} {points[1][1]:.1f}"]
        for i in range(1, len(points) - 2):
            p0, p1, p2, p3 = points[i-1], points[i], points[i+1], points[i+2]
            cp1x = p1[0] + (p2[0] - p0[0]) / 6
            cp1y = p1[1] + (p2[1] - p0[1]) / 6
            cp2x = p2[0] - (p3[0] - p1[0]) / 6
            cp2y = p2[1] - (p3[1] - p1[1]) / 6
            d.append(f"C {cp1x:.1f} {cp1y:.1f}, {cp2x:.1f} {cp2y:.1f}, "
                     f"{p2[0]:.1f} {p2[1]:.1f}")
        return ' '.join(d)


    def edge_points(src, dst):
        """Build control points for an FK curve from src to dst.

        Three REAL points (start, midpoint, end) surrounded by two PHANTOM
        points placed horizontally outside the start/end. Phantoms are not
        drawn — they shape tangents so the curve enters/exits horizontally.

        This avoids the overshoot kink that the naive stub-and-midpoint
        approach produced: with uniform /6 Catmull-Rom, tangent vectors scale
        with chord length, so a short stub would get a Bézier control point
        placed behind its own segment — causing the curve to curl back.
        """
        sx, sy = src
        dx, dy = dst
        phantom = 60
        # Direction of horizontal travel determines which side the phantoms sit.
        # Normal case: source-left, dest-right → phantoms at sx-60 and dx+60.
        # Backward case: source-right, dest-left → phantoms at sx+60 and dx-60.
        sign = 1 if dx >= sx else -1
        return [
            (sx - sign * phantom, sy),
            (sx,                  sy),
            ((sx + dx) / 2, (sy + dy) / 2),
            (dx,                  dy),
            (dx + sign * phantom, dy),
        ]


    # ── SVG rendering via html_tags ──────────────────────────────────────────

    # Color accents for different column kinds
    C_PK        = '#b07512'   # primary key — amber
    C_FK        = '#4a7bbf'   # foreign key — blue
    C_NOTNULL   = '#555'
    C_REGULAR   = '#333'
    C_TYPE      = '#999'
    C_TABLE_BG  = '#fdfdfb'
    C_TABLE_BD  = '#d8d4c8'
    C_HEADER_BG = '#f0ebe0'
    C_EDGE      = '#8b8778'


    def render_table(name, info, pos, fk_cols):
        """Return an SVG <g> containing one table: header + column rows.
        `fk_cols` is the set of column names in this table that are FKs."""
        x, y, w = pos['x'], pos['y'], pos['w']

        # Header
        children = [
            h.rect(x=x, y=y, width=w, height=HEADER_H,
                   rx=6, fill=C_HEADER_BG, stroke=C_TABLE_BD,
                   **{'stroke-width': '1'}),
            h.text(name,
                   x=x + 12, y=y + HEADER_H / 2 + 4,
                   **{'font-family': 'system-ui, sans-serif',
                      'font-size': '13', 'font-weight': '600',
                      'fill': '#222'}),
        ]

        # Column rows
        for i, (col_name, ctype, is_pk, notnull) in enumerate(info['cols']):
            row_y = y + HEADER_H + i * ROW_H
            is_fk = col_name in fk_cols

            # Row background (alternating for readability)
            if i % 2 == 1:
                children.append(h.rect(
                    x=x + 1, y=row_y, width=w - 2, height=ROW_H,
                    fill='#faf8f2', stroke='none',
                ))

            # PK/FK marker dot at left
            if is_pk:
                children.append(h.circle(cx=x + 10, cy=row_y + ROW_H/2, r=3,
                                         fill=C_PK))
            elif is_fk:
                children.append(h.circle(cx=x + 10, cy=row_y + ROW_H/2, r=3,
                                         fill=C_FK))

            # Column name
            color = C_PK if is_pk else (C_FK if is_fk else C_REGULAR)
            weight = '600' if is_pk else ('500' if is_fk else '400')
            children.append(h.text(
                col_name,
                x=x + 22, y=row_y + ROW_H/2 + 4,
                **{'font-family': 'system-ui, sans-serif',
                   'font-size': '12', 'font-weight': weight, 'fill': color},
            ))

            # Type (right-aligned, muted). Prefix with '*' if NOT NULL (not PK).
            type_label = f'* {ctype}' if (notnull and not is_pk) else ctype
            children.append(h.text(
                type_label,
                x=x + w - 10, y=row_y + ROW_H/2 + 4,
                **{'font-family': 'ui-monospace, Menlo, monospace',
                   'font-size': '10', 'fill': C_TYPE,
                   'text-anchor': 'end'},
            ))

        # Outer table rect (drawn last so its border sits on top)
        children.append(h.rect(
            x=x, y=y, width=w, height=pos['h'],
            rx=6, fill='none', stroke=C_TABLE_BD,
            **{'stroke-width': '1'},
        ))

        return h.g(*children)


    def render_edge(src_table, src_col, dst_table, dst_col, positions):
        """Render one FK curve from (src_table.src_col) to (dst_table.dst_col)."""
        sp = positions[src_table]
        dp = positions[dst_table]

        # Default: curve leaves FK row's right edge, enters PK row's left edge
        sx = sp['x'] + sp['w']
        sy = sp['col_y'][src_col]
        dx = dp['x']
        dy = dp['col_y'][dst_col]

        # If dest is to the LEFT of source (unusual — cycle or backward layer),
        # flip attachment: leave left edge, enter right edge
        if dx < sx:
            sx = sp['x']
            dx = dp['x'] + dp['w']

        pts = edge_points((sx, sy), (dx, dy))

        return h.g(
            h.path(
                d=catmull_rom_path(pts),
                fill='none', stroke=C_EDGE,
                **{'stroke-width': '1.5', 'stroke-linecap': 'round'},
            ),
            # Small dot at each endpoint to anchor the curve visually
            h.circle(cx=sx, cy=sy, r=2.5, fill=C_EDGE),
            h.circle(cx=dx, cy=dy, r=2.5, fill=C_EDGE),
        )


    def render_erd(db_path, title='Schema'):
        schema = introspect(db_path)
        positions = layout(schema)

        # Canvas bounds
        max_x = max((p['x'] + p['w'] for p in positions.values()), default=400)
        max_y = max((p['y'] + p['h'] for p in positions.values()), default=200)
        canvas_w = max_x + MARGIN
        canvas_h = max_y + MARGIN

        # Precompute FK column sets per table for highlighting
        fk_cols_by_table = {t: {fk[0] for fk in info['fks']}
                            for t, info in schema.items()}

        # Edges first (so they render under the tables)
        edges = []
        for t, info in schema.items():
            for from_col, ref_table, to_col in info['fks']:
                if ref_table in positions:
                    edges.append(render_edge(t, from_col, ref_table, to_col,
                                              positions))

        # Tables
        tables = [render_table(t, info, positions[t], fk_cols_by_table[t])
                  for t, info in schema.items()]

        svg = h.svg(
            *edges, *tables,
            viewBox=f"0 0 {canvas_w} {canvas_h}",
            width=str(canvas_w), height=str(canvas_h),
            style="display:block; max-width:100%; height:auto;",
        )

        # Legend + summary stats
        n_tables = len(schema)
        n_cols   = sum(len(info['cols']) for info in schema.values())
        n_fks    = sum(len(info['fks'])  for info in schema.values())

        legend = h.div(
            {'style': 'display:flex; gap:1.5rem; font-size:12px; color:#555; '
                      'margin-bottom:1rem; flex-wrap:wrap;'},
            h.div(h.span({'style': f'display:inline-block; width:10px; height:10px; '
                                    f'border-radius:50%; background:{C_PK}; '
                                    f'margin-right:0.4rem; vertical-align:middle;'}),
                  'Primary key'),
            h.div(h.span({'style': f'display:inline-block; width:10px; height:10px; '
                                    f'border-radius:50%; background:{C_FK}; '
                                    f'margin-right:0.4rem; vertical-align:middle;'}),
                  'Foreign key'),
            h.div(h.span({'style': f'font-family:ui-monospace, monospace; '
                                    f'color:{C_TYPE}; margin-right:0.4rem;'},
                         '*'),
                  'NOT NULL'),
            h.div({'style': 'margin-left:auto; color:#888;'},
                  f'{n_tables} tables · {n_cols} columns · {n_fks} relationships'),
        )

        return h.html_doc(
            h.head(
                h.meta(charset='utf-8'),
                h.title(f'ERD — {title}'),
                h.Favicon('🗂️'),
                h.style(h.Safe("""
                    body { margin:0; padding:2rem 1rem; background:#fafaf7;
                           font-family:system-ui, -apple-system, sans-serif;
                           color:#1a1a1a; min-height:100vh; }
                    .wrap { max-width:1400px; margin:0 auto; }
                    h1 { font-size:1.5rem; font-weight:500; margin:0 0 0.25rem; }
                    .sub { color:#666; font-size:0.875rem; margin:0 0 1.25rem; }
                    .canvas { background:white; border:1px solid #e5e2da;
                              border-radius:10px; padding:1rem; overflow-x:auto; }
                """)),
            ),
            h.body(
                h.div({'class': 'wrap'})(
                    h.h1(f'ERD — {title}'),
                    h.p({'class': 'sub'},
                        'Generated by introspecting ', h.code(db_path),
                        ' via PRAGMA table_info / foreign_key_list.'),
                    legend,
                    h.div({'class': 'canvas'})(svg),
                ),
            ),
        )


    # ── Entry point ──────────────────────────────────────────────────────────

    if __name__ == '__main__':
        if len(sys.argv) < 2:
            print(__doc__)
            sys.exit(1)
        db_path = sys.argv[1]
        out_path = sys.argv[2] if len(sys.argv) > 2 else '/home/claude/erd.html'

        import os
        title = os.path.splitext(os.path.basename(db_path))[0]
        html = render_erd(db_path, title=title)
        with open(out_path, 'w') as f:
            f.write(str(html))
        print(f"Wrote {out_path}")
    return


if __name__ == "__main__":
    app.run()
