"""HTML/SVG generation for Python. Zero dependencies."""
__version__ = '0.1.15'
__author__ = 'Deufel'
from .tag import normalize, attrmap, flatten, Tag, Safe, Fragment, mktag
from .render import render_attrs, to_html
from .dev import pretty, html_to_tag, repr_html
__all__ = [
    "Fragment",
    "Safe",
    "Tag",
    "attrmap",
    "flatten",
    "html_to_tag",
    "mktag",
    "normalize",
    "pretty",
    "render_attrs",
    "repr_html",
    "to_html",
]
def __getattr__(name):
        return mktag(name.rstrip('_').replace('_', '-'))
