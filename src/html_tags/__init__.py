"""HTML/SVG generation via python functions."""
__version__ = '0.3.3'
__author__ = 'Deufel'
from .tags import Safe, unpack, is_tag, tag, render_attrs, render, html_doc, mk_tag, html_to_tag, Datastar, MeCSS, Pointer, Highlight, Color_type_css, Favicon, Layout
from .charts import Show, sparkline, chart_card, card_size_resize, card_aspect_resize
__all__ = [
    "Color_type_css",
    "Datastar",
    "Favicon",
    "Highlight",
    "Layout",
    "MeCSS",
    "Pointer",
    "Safe",
    "Show",
    "card_aspect_resize",
    "card_size_resize",
    "chart_card",
    "html_doc",
    "html_to_tag",
    "is_tag",
    "mk_tag",
    "render",
    "render_attrs",
    "sparkline",
    "tag",
    "unpack",
]
def __getattr__(name):
        return mk_tag(name)
