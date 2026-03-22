"""Concise, immutable HTML/SVG generation for Python. Zero dependencies."""
__version__ = '0.0.18'
__author__ = 'Deufel'
from .core import setup_tags, mktag, Tag, to_html, pretty
from .svg import setup_svg
__all__ = [
    "Tag",
    "mktag",
    "pretty",
    "setup_svg",
    "setup_tags",
    "to_html",
]
