"""concise html tag generation"""
__version__ = '0.0.5'
__author__ = 'Deufel'
from .core import Tag, attrmap, render_attrs, is_void, is_raw, to_html, mktag, TagNS, Fragment, flatten, tag, validate_raw, setup_tags, ui_head
from .sse import patch_elements, patch_signals, datastar_stream
__all__ = [
    "Fragment",
    "Tag",
    "TagNS",
    "attrmap",
    "datastar_stream",
    "flatten",
    "is_raw",
    "is_void",
    "mktag",
    "patch_elements",
    "patch_signals",
    "render_attrs",
    "setup_tags",
    "tag",
    "to_html",
    "ui_head",
    "validate_raw",
]
