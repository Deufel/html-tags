"""HTML/SVG generation via python functions."""
__version__ = '0.4.0'
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
