"""concise html tag generation"""
__version__ = '0.0.11'
__author__ = 'Deufel'
from .core import setup_tags, Tag, to_html, mktag, pretty
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
