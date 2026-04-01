from html import escape
from html.parser import HTMLParser
from .tag import Tag, Safe, Fragment, normalize, VOID, RAW, SVG_VOID
from .render import render_attrs, to_html

"""Development tools: pretty printing, HTML parsing, notebook display."""

def pretty(t, indent=2, _depth=0):
    """Render a Tag tree as indented HTML for debugging."""
    pad  = ' ' * (indent * _depth)
    pad1 = ' ' * (indent * (_depth + 1))
    if hasattr(t, '__html__') and not isinstance(t, Tag): return t.__html__()
    if not isinstance(t, Tag): return pad + escape(str(t).replace('\x00', ''))
    a = render_attrs(t.attrs) if t.attrs else ''
    tag = t.tag
    void = tag in VOID or tag in SVG_VOID
    if void: return f'{pad}<{tag}{a} />' if tag in SVG_VOID else f'{pad}<{tag}{a}>'
    if tag in RAW:
        inner = ''.join(str(c).replace('\x00', '') for c in t.children)
        if not inner: return f'{pad}<{tag}{a}></{tag}>'
        lines = inner.strip().splitlines()
        return f'{pad}<{tag}{a}>\n' + '\n'.join(pad1 + l for l in lines) + f'\n{pad}</{tag}>'
    if not tag: return '\n'.join(pretty(c, indent, _depth) for c in t.children)
    if not t.children: return f'{pad}<{tag}{a}></{tag}>'
    if len(t.children) == 1 and isinstance(t.children[0], str):
        return f'{pad}<{tag}{a}>{escape(t.children[0])}</{tag}>'
    pre = '<!DOCTYPE html>\n' if tag == 'html' else ''
    kids = '\n'.join(pretty(c, indent, _depth + 1) for c in t.children)
    return f'{pre}{pad}<{tag}{a}>\n{kids}\n{pad}</{tag}>'

def html_to_tag(s):
    """Parse an HTML string into a Tag tree. Uses normalize() for SVG casing."""
    stack, root = [[]], []
    class P(HTMLParser):
        def handle_starttag(self, tag, attrs):
            name = normalize(tag)
            d = {k: (v if v is not None else True) for k, v in attrs}
            if name in VOID or name in SVG_VOID:
                stack[-1].append(Tag(name, (), d))
            else:
                stack.append([])
                root.append((name, d))
        def handle_endtag(self, tag):
            name = normalize(tag)
            if name in VOID or name in SVG_VOID: return
            children = tuple(stack.pop())
            t, d = root.pop()
            stack[-1].append(Tag(t, children, d))
        def handle_data(self, data):
            if data.strip(): stack[-1].append(data.strip())
    P().feed(s)
    res = stack[0]
    return res[0] if len(res) == 1 else Fragment(*res)

def repr_html(t):
    """Return an HTML string suitable for notebook _repr_html_ display."""
    return to_html(t)
