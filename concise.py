import marimo

__generated_with = "0.20.4"
app = marimo.App()


@app.cell
def _():
    """concise html tag generation"""
    __version__ = '0.0.5'
    __author__ = 'Deufel'
    __all__ = ["Fragment", "TagNS", "attrmap", "flatten", "is_raw", "is_void", "render_attrs", "tag", "to_html", "validate_raw"]

    import types, re
    from collections import namedtuple
    from html import escape

    VOID_TAGS = frozenset({'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'})
    RAW_TAGS = frozenset({'script', 'style'})
    RAW_CLOSE_RE = re.compile(r'</\s*(script|style)\b[^>]*>', re.IGNORECASE)
    attr_map = dict(cls='class', klass='class', _class='class', _for='for', fr='for')

    class Tag(namedtuple('Tag', 'tag children attrs', defaults=((), {}))):
        def __str__(self): return globals()['to_html'](self)
        __html__ = _repr_html_ = __str__

    def attrmap(k): return attr_map.get(k, k.lstrip('_').replace('_', '-'))

    def render_attrs(d): return ''.join(f' {attrmap(k)}' if v is True else f' {attrmap(k)}="{v}"' for k,v in d.items() if v not in (False, None))

    def is_void(t): return t.tag in VOID_TAGS
    def is_raw(t): return t.tag in RAW_TAGS

    def to_html(t):
        if isinstance(t, str): return escape(t)
        if not hasattr(t, 'tag'): return escape(str(t))
        attrs = render_attrs(t.attrs) if t.attrs else ''
        if is_raw(t):
            inner = ''.join(str(c) for c in t.children)
            validate_raw(t.tag, inner)
        elif len(t.children) == 1: inner = to_html(t.children[0])
        else: inner = ''.join(to_html(c) for c in t.children)
        if not t.tag: return inner
        if is_void(t): return f'<{t.tag}{attrs}>'
        return f'<{t.tag}{attrs}>{inner}</{t.tag}>'

    class TagNS:
        def __getattr__(self, name):
            n = name.lower()
            def f(*c, **kw): return tag(n, *c, **kw)
            f.__name__ = name.capitalize()
            return f
        def export(self, *names): return [getattr(self, n) for n in names]

    def Fragment(*c, **kw): return tag('', *c, **kw)

    def flatten(c):
        for o in c:
            if o is None or o is False: continue
            if hasattr(o, 'tag'): yield o
            elif isinstance(o, (list, tuple, map, filter, types.GeneratorType)): yield from flatten(o)
            else: yield o

    def tag(name, *c, **kw):
        children = tuple(flatten(o for o in c if not isinstance(o, dict)))
        attrs = {k:v for o in c if isinstance(o, dict) for k,v in o.items()}
        return Tag(name, children, {**attrs, **kw})

    def validate_raw(tag, text):
        if RAW_CLOSE_RE.search(text): raise ValueError(f'Raw text in <{tag}> must not contain closing tag pattern: {text!r}')

    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
