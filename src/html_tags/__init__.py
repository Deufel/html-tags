"""HTML/SVG generation for Python."""
__version__ = '0.2.2'
__author__ = 'Deufel'
from .core import Safe, unpack, render_attrs, render, Tag, mk_tag, sse_signal, sse_patch, html_to_tag, Datastar, MeCSS, Pointer, Favicon, heatmap
__all__ = [
    "Datastar",
    "Favicon",
    "MeCSS",
    "Pointer",
    "Safe",
    "Tag",
    "heatmap",
    "html_to_tag",
    "mk_tag",
    "render",
    "render_attrs",
    "sse_patch",
    "sse_signal",
    "unpack",
]
def __getattr__(name):
        return mk_tag(name)
