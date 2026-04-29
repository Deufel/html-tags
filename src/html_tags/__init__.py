"""HTML/SVG generation via python functions."""
__version__ = '0.4.2'
__author__ = 'Deufel'
from .node import Node, Safe
from .attrs import normalize_attrs
from .ns import child_ns
from .render import render
from .dsl import TagFactory
from .viz_scale import Scale, LinearScale, BandScale, HueScale, OrdinalHueScale
from .viz_mark import rect, circle, line, polyline, path, path_d, area_d, text, group
from .viz_axis import axis
from .viz_chart import Margin, BoundMargin, chart
__all__ = [
    "BandScale",
    "BoundMargin",
    "HueScale",
    "LinearScale",
    "Margin",
    "Node",
    "OrdinalHueScale",
    "Safe",
    "Scale",
    "TagFactory",
    "area_d",
    "axis",
    "chart",
    "child_ns",
    "circle",
    "group",
    "line",
    "normalize_attrs",
    "path",
    "path_d",
    "polyline",
    "rect",
    "render",
    "text",
]
HTML = 'html'
SVG = 'svg'
MATH = 'math'
h = TagFactory(HTML)
s = TagFactory(SVG)
m = TagFactory(MATH)
def doc(*args, lang: str = 'en') -> str:
        """Render a full HTML document with DOCTYPE declaration.

        Usage:
            doc(
                h.head(h.title('My Page')),
                h.body(h.p('Hello')),
            )

        Args are the direct children of <html>. Lang defaults to 'en'.
        """
        page = h.html(*args, lang=lang)
        return '<!DOCTYPE html>\n' + render(page)
def render_pretty(node, indent: int = 2) -> str:
        """Render with indentation for debugging. Never use in production."""
        import xml.dom.minidom
        raw = render(node)
        try:
            return xml.dom.minidom.parseString(raw).toprettyxml(indent=' ' * indent)
        except Exception:
            return raw
