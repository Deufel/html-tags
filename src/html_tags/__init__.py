"""concise html tag generation"""
__version__ = '0.0.7'
__author__ = 'Deufel'
from .core import setup_tags, to_html, pretty
from .sse import patch_elements, patch_signals, datastar_stream
__all__ = [
    "datastar_stream",
    "patch_elements",
    "patch_signals",
    "pretty",
    "setup_tags",
    "to_html",
]
