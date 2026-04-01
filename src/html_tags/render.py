import re
from html import escape
from .tag import Tag, Safe, VOID, RAW, SVG_VOID, SVG_SC

SAFE_ATTR = re.compile('^[a-zA-Z_][\\w\\-:.]*$')
BAD_URL = re.compile('^(?:javascript:|vbscript:|data:(?!(?:text/html|text/plain|image/|application/json)))', re.I)
URL_ATTRS = frozenset('href src action formaction data poster codebase cite background'.split())

"""Render Tag trees to HTML strings."""

def _is_void(tag): return tag in VOID or tag in SVG_VOID

def _is_raw(tag):  return tag in RAW

def _is_sc(tag):   return tag in SVG_SC or tag in SVG_VOID

def render_attrs(d):
    """Render an attrs dict to an HTML attribute string (with leading spaces)."""
    parts = []
    for k, v in d.items():
        if not SAFE_ATTR.match(k): raise ValueError(f'Bad attr name: {k!r}')
        if k in URL_ATTRS and BAD_URL.match(str(v)): raise ValueError(f'Bad URL in {k}')
        if   v is True:  parts.append(f' {k}')
        elif v is not False and v is not None:
            v2 = str(v).replace('&', '&amp;').replace('<', '&lt;').replace('"', '&quot;')
            parts.append(f' {k}="{v2}"')
    return ''.join(parts)

def to_html(t):
    """Render a Tag tree to an HTML string."""
    if hasattr(t, '__html__') and not isinstance(t, Tag): return t.__html__()
    if not isinstance(t, Tag): return escape(str(t).replace('\x00', ''))
    a = render_attrs(t.attrs) if t.attrs else ''
    tag = t.tag
    if _is_void(tag):
        if t.children: raise ValueError(f'<{tag}> is void, no children')
        return f'<{tag}{a} />' if _is_sc(tag) else f'<{tag}{a}>'
    if _is_raw(tag):
        inner = ''.join(str(c).replace('\x00', '') for c in t.children)
        return f'<{tag}{a}>{inner}</{tag}>'
    inner = ''.join(to_html(c) for c in t.children)
    if not tag: return inner
    if not inner and _is_sc(tag): return f'<{tag}{a} />'
    if tag == 'html': return f'<!DOCTYPE html>\n<{tag}{a}>{inner}</{tag}>'
    return f'<{tag}{a}>{inner}</{tag}>'
