"""Concise, immutable HTML/SVG generation for Python. Zero dependencies."""
__version__ = '0.0.15'
__author__ = 'Deufel'
from .core import setup_tags, mktag, Tag, to_html, pretty
from .sse import patch_elements, patch_signals, datastar_stream
from .svg import setup_svg
__all__ = [
    "Tag",
    "datastar_stream",
    "mktag",
    "patch_elements",
    "patch_signals",
    "pretty",
    "setup_svg",
    "setup_tags",
    "to_html",
]
