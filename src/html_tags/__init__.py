"""HTML/SVG generation for Python. Zero dependencies."""
__version__ = '0.1.9'
__author__ = 'Deufel'
from .tag import attrmap, flatten, Tag, Safe
from .render import render_attrs, to_html
from .dev import pretty, html_to_tag, repr_html
__all__ = [
    "Safe",
    "Tag",
    "attrmap",
    "flatten",
    "html_to_tag",
    "pretty",
    "render_attrs",
    "repr_html",
    "to_html",
]
def __getattr__(name):
        return mktag(name.rstrip('_').replace('_', '-'))
