import marimo

__generated_with = "0.22.0"
app = marimo.App(width="medium")

with app.setup:
    """Tag tree: pure data, construction, and element constants."""
    import types
    from collections import namedtuple


    # ── element classification sets ──────────────────────────────────────
    VOID = frozenset('area base br col embed hr img input link meta source track wbr'.split())
    RAW  = frozenset(('script', 'style'))

    SVG_VOID = frozenset('stop set image use'.split()) | frozenset(
        'feBlend feColorMatrix feComposite feConvolveMatrix feDisplacementMap '
        'feDistantLight feDropShadow feFlood feFuncA feFuncB feFuncG feFuncR '
        'feGaussianBlur feImage feMergeNode feMorphology feOffset fePointLight '
        'feSpotLight feTile feTurbulence'.split())

    SVG_SC = frozenset('circle ellipse line path polygon polyline rect '
                        'animate animateMotion animateTransform'.split())

    SVG_NAMES = {
        'clipPath': 'clipPath', 'foreignObject': 'foreignObject',
        'linearGradient': 'linearGradient', 'radialGradient': 'radialGradient',
        'textPath': 'textPath', 'animateMotion': 'animateMotion',
        'animateTransform': 'animateTransform',
        **{k: k for k in
           'feBlend feColorMatrix feComponentTransfer feComposite feConvolveMatrix '
           'feDiffuseLighting feDisplacementMap feDistantLight feDropShadow feFlood '
           'feFuncA feFuncB feFuncG feFuncR feGaussianBlur feImage feMerge '
           'feMergeNode feMorphology feOffset fePointLight feSpecularLighting '
           'feSpotLight feTile feTurbulence'.split()}}

    SVG_NAMES_LOWER = {k.lower(): v for k, v in SVG_NAMES.items()}

    _ATTR_MAP = {'cls': 'class', '_class': 'class', '_for': 'for',
                 '_from': 'from', '_in': 'in', '_is': 'is'}


@app.cell
def _():
    # ── pure functions ───────────────────────────────────────────────────
    return


@app.function
def normalize(name):
    """Single source of truth for tag name casing."""
    low = name.lower()
    return SVG_NAMES_LOWER.get(low, low)


@app.function
def attrmap(k):
    """cls→class, _for→for, trailing_ strip, underscores→hyphens."""
    return _ATTR_MAP.get(k, k.rstrip('_').replace('_', '-'))


@app.function
def flatten(items):
    for o in items:
        if o is None or o is False: continue
        if hasattr(o, 'tag'): yield o          # Tag-like, don't recurse into it
        elif isinstance(o, (list, tuple, map, filter, types.GeneratorType)):
            yield from flatten(o)
        else: yield o


@app.function
def internal_parse_args(c, kw):
    """Split positional args into (children_tuple, attrs_dict).
    Dicts in positional args merge into attrs. kwargs go through attrmap.
    """
    da, ch = {}, []
    for o in c:
        if isinstance(o, dict): da.update(o)
        else: ch.append(o)
    attrs = {attrmap(k): v for k, v in kw.items()}
    attrs.update(da)
    return tuple(flatten(ch)), attrs


@app.cell
def _():
    # ── data types ───────────────────────────────────────────────────────
    return


@app.class_definition
class Tag(namedtuple('Tag', 'tag children attrs', defaults=((), {}))):
    """An HTML/SVG element as pure data. Three fields, no rendering."""

    def __call__(self, *c, **kw):
        children, attrs = internal_parse_args(c, kw)
        return self._replace(
            children=self.children + children,
            attrs={**self.attrs, **attrs})

    def __html__(self):
        from .render import to_html # Marimo cycle hackery ugly but effective
        return to_html(self)

    def __str__(self):
        return self.__html__()


@app.class_definition
class Safe(str):
    """Pre-escaped HTML string."""
    def __html__(self): return self


@app.cell
def _():
    # ── constructors ─────────────────────────────────────────────────────
    return


@app.function
def Fragment(*c, **kw):
    """Tag with empty name — renders as bare children."""
    children, attrs = internal_parse_args(c, kw)
    return Tag('', children, attrs)


@app.function
def mktag(name):
    """Create a Tag constructor for any element name."""
    name = normalize(name)
    def tag(*c, **kw):
        children, attrs = internal_parse_args(c, kw)
        return Tag(name, children, attrs)
    tag.__name__ = name
    return tag


@app.cell
def _():
    # Rendering (now in same module Testing)
    return


if __name__ == "__main__":
    app.run()
