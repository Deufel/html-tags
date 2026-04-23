from .tags import svg, polyline

def sparkline(values):
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
                 style="--color: 0.5", stroke_width="2"),
        viewBox="0 0 100 100", preserveAspectRatio="none",
        cls="sparkline",
    )
