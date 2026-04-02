"""HTML/SVG generation for Python."""
__version__ = '0.1.21'
__author__ = 'Deufel'
from .tag import normalize, attrmap, flatten, Tag, Safe, Fragment, mktag
from .render import render_attrs, to_html
from .dev import pretty, html_to_tag, repr_html
from .extras import Datastar, ScopedCSS, Favicon, CSP, Social
__all__ = [
    "CSP",
    "Datastar",
    "Favicon",
    "Fragment",
    "Safe",
    "ScopedCSS",
    "Social",
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
