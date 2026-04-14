"""HTML/SVG generation for Python."""
__version__ = '0.2.0'
__author__ = 'Deufel'
from .core import Safe, unpack, render_attrs, render, tag, Tag, mk_tag, Fragment, sse_signal, render_pretty, sse_patch, html_to_tag, Datastar, MeCSS, Pointer, Favicon
__all__ = [
    "Datastar",
    "Favicon",
    "Fragment",
    "MeCSS",
    "Pointer",
    "Safe",
    "Tag",
    "html_to_tag",
    "mk_tag",
    "render",
    "render_attrs",
    "render_pretty",
    "sse_patch",
    "sse_signal",
    "tag",
    "unpack",
]
def __getattr__(name):
        return mk_tag(name)
