"""concise html tag generation"""
__version__ = '0.0.4'
__author__ = 'Deufel'
from .core import attrmap, render_attrs, is_void, is_raw, to_html, mktag, TagNS, Fragment, flatten, tag, validate_raw
__all__ = [
    "Fragment",
    "TagNS",
    "attrmap",
    "flatten",
    "is_raw",
    "is_void",
    "mktag",
    "render_attrs",
    "tag",
    "to_html",
    "validate_raw",
]
