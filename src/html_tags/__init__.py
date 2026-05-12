"""HTML/SVG generation via python functions."""
__version__ = '0.4.4'
__author__ = 'Deufel'
from .node import Node, Safe
from .attrs import normalize_attrs
from .ns import child_ns
from .render import render
from .dsl import TagFactory
__all__ = [
    "Node",
    "Safe",
    "TagFactory",
    "child_ns",
    "normalize_attrs",
    "render",
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
