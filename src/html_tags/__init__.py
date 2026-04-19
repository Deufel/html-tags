"""HTML/SVG generation via python functions."""
__version__ = '0.3.2'
__author__ = 'Deufel'
from .template import Safe, unpack, is_tag, tag, render_attrs, render, html_doc, mk_tag, html_to_tag, Datastar, MeCSS, Pointer, Highlight, Color_type_css, Favicon, Layout
__all__ = [
    "Color_type_css",
    "Datastar",
    "Favicon",
    "Highlight",
    "Layout",
    "MeCSS",
    "Pointer",
    "Safe",
    "html_doc",
    "html_to_tag",
    "is_tag",
    "mk_tag",
    "render",
    "render_attrs",
    "tag",
    "unpack",
]
def __getattr__(name):
        return mk_tag(name)
