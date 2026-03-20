"""concise html tag generation"""
__version__ = '0.0.10'
__author__ = 'Deufel'
from .core import setup_tags, to_html, pretty
from .sse import patch_elements, patch_signals, datastar_stream
from .svg import setup_svg
__all__ = [
    "datastar_stream",
    "patch_elements",
    "patch_signals",
    "pretty",
    "setup_svg",
    "setup_tags",
    "to_html",
]
