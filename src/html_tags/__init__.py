"""HTML/SVG generation for Python. Zero dependencies."""
__version__ = '0.1.01'
__author__ = 'Deufel'
from .core import attrmap, flatten, Tag, mktag, Fragment, validate, render_attrs, to_html, HTML, setup_tags, setup_svg, pretty, Safe, html_to_tag
__all__ = [
    "Fragment",
    "HTML",
    "Safe",
    "Tag",
    "attrmap",
    "flatten",
    "html_to_tag",
    "mktag",
    "pretty",
    "render_attrs",
    "setup_svg",
    "setup_tags",
    "to_html",
    "validate",
]
