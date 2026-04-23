from html import escape
from .tags import mk_tag, render, html_doc, Safe, Datastar, MeCSS, Pointer, Highlight, Color_type_css, Favicon

head = mk_tag('head')
body = mk_tag('body')
title = mk_tag('title')
iframe = mk_tag('iframe')
div = mk_tag('div')
svg = mk_tag('svg')
style = mk_tag('style')
polyline = mk_tag('polyline')

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
