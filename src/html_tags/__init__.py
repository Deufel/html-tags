"""HTML/SVG generation for Python. Zero dependencies."""
__version__ = '0.0.20'
__author__ = 'Deufel'
from .core import setup_tags, mktag, Tag, attrmap, render_attrs, is_void, is_raw, is_root, to_html, Fragment, flatten, validate_raw, pretty, __getattr__
from .svg import setup_svg
__all__ = [
    "Fragment",
    "Tag",
    "__getattr__",
    "attrmap",
    "flatten",
    "is_raw",
    "is_root",
    "is_void",
    "mktag",
    "pretty",
    "render_attrs",
    "setup_svg",
    "setup_tags",
    "to_html",
    "validate_raw",
]
