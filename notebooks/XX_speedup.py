import marimo

__generated_with = "0.20.4"
app = marimo.App()

with app.setup:
    import types, re
    from collections import namedtuple
    from html import escape
    from functools import lru_cache

    VOID_TAGS = frozenset({'area','base','br','col','embed','hr','img','input','link','meta','source','track','wbr'})
    RAW_TAGS = frozenset({'script','style'})
    RAW_CLOSE_RE = re.compile(r'</(script|style)[\s/>]', re.IGNORECASE)



    _ATTR_MAP = dict(cls='class', klass='class', _class='class', _for='for', fr='for')

    @lru_cache(maxsize=256)
    def _mapkey(k): return _ATTR_MAP.get(k) or k.lstrip('_').replace('_', '-')

    _TagBase = namedtuple('Tag', 'tag children attrs', defaults=((), {}))

    class Tag(_TagBase):
        __slots__ = ()
        def __str__(self): return to_html(self)
        def __html__(self): return to_html(self)
        def _repr_html_(self): return to_html(self)

    def render_attrs(d):
        parts = []
        for k, v in d.items():
            k = _mapkey(k)
            if v is True: parts.append(f' {k}')
            elif v is not False and v is not None: parts.append(f' {k}="{escape(str(v), quote=True)}"')
        return ''.join(parts)

    def to_html(t):
        if isinstance(t, str): return escape(t)
        if not isinstance(t, Tag): return escape(str(t))
        name, children, attrs = t
        a = render_attrs(attrs) if attrs else ''
        if name in RAW_TAGS:
            inner = ''.join(str(c) for c in children)
            if RAW_CLOSE_RE.search(inner):
                raise ValueError(f'Raw text in <{name}> contains closing tag: {inner!r}')
        elif len(children) == 1: inner = to_html(children[0])
        else: inner = ''.join(to_html(c) for c in children)
        if not name: return inner
        if name in VOID_TAGS: return f'<{name}{a}>'
        return f'<{name}{a}>{inner}</{name}>'

    def flatten(c):
        for o in c:
            if o is None or o is False: continue
            if isinstance(o, Tag): yield o
            elif isinstance(o, (list, tuple, map, filter, types.GeneratorType)): yield from flatten(o)
            else: yield o

    def tag(name, *c, **kw):
        children, dattrs = [], {}
        for o in c:
            if isinstance(o, dict): dattrs.update(o)
            else: children.append(o)
        return Tag(name, tuple(flatten(children)), {**dattrs, **kw})

    def mktag(name):
        def f(*c, **kw): return tag(name, *c, **kw)
        f.__name__ = name
        return f

    class TagNS:
        def __getattr__(self, name): return mktag(name.lower())
        def export(self, *names): return [getattr(self, n) for n in names]

    def Fragment(*c, **kw): return tag('', *c, **kw)


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
