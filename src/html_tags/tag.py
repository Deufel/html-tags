import types
from collections import namedtuple

VOID = frozenset('area base br col embed hr img input link meta source track wbr'.split())
RAW = frozenset(('script', 'style'))
SVG_VOID = frozenset('stop set image use'.split()) | frozenset('feBlend feColorMatrix feComposite feConvolveMatrix feDisplacementMap feDistantLight feDropShadow feFlood feFuncA feFuncB feFuncG feFuncR feGaussianBlur feImage feMergeNode feMorphology feOffset fePointLight feSpotLight feTile feTurbulence'.split())
SVG_SC = frozenset('circle ellipse line path polygon polyline rect animate animateMotion animateTransform'.split())
SVG_NAMES = {'clipPath': 'clipPath', 'foreignObject': 'foreignObject', 'linearGradient': 'linearGradient', 'radialGradient': 'radialGradient', 'textPath': 'textPath', 'animateMotion': 'animateMotion', 'animateTransform': 'animateTransform', **{k: k for k in 'feBlend feColorMatrix feComponentTransfer feComposite feConvolveMatrix feDiffuseLighting feDisplacementMap feDistantLight feDropShadow feFlood feFuncA feFuncB feFuncG feFuncR feGaussianBlur feImage feMerge feMergeNode feMorphology feOffset fePointLight feSpecularLighting feSpotLight feTile feTurbulence'.split()}}
SVG_NAMES_LOWER = {k.lower(): v for k, v in SVG_NAMES.items()}
_ATTR_MAP = {'cls': 'class', '_class': 'class', '_for': 'for', '_from': 'from', '_in': 'in', '_is': 'is'}

"""Tag tree: pure data, construction, and element constants."""

def normalize(name):
    """Single source of truth for tag name casing."""
    low = name.lower()
    return SVG_NAMES_LOWER.get(low, low)

def attrmap(k):
    """cls→class, _for→for, trailing_ strip, underscores→hyphens."""
    return _ATTR_MAP.get(k, k.rstrip('_').replace('_', '-'))

def flatten(items):
    for o in items:
        if o is None or o is False: continue
        if hasattr(o, '__html__'): yield o       # This is HTML - like, don't recurse into it
        elif isinstance(o, (list, tuple, map, filter, types.GeneratorType)):
            yield from flatten(o)
        else: yield o

def _parse_args(c, kw):
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

class Tag(namedtuple('Tag', 'tag children attrs', defaults=((), {}))):
    """An HTML/SVG element as pure data. Three fields, no rendering."""

    def __call__(self, *c, **kw):
        children, attrs = _parse_args(c, kw)
        return self._replace(
            children=self.children + children,
            attrs={**self.attrs, **attrs})

    def __html__(self):
        from .render import to_html # Marimo cycle hackery ugly but effective
        return to_html(self)

    def __str__(self):
        return self.__html__()

class Safe(str):
    """Pre-escaped HTML string."""
    def __html__(self): return self

def Fragment(*c, **kw):
    """Tag with empty name — renders as bare children."""
    children, attrs = _parse_args(c, kw)
    return Tag('', children, attrs)

def mktag(name):
    """Create a Tag constructor for any element name."""
    name = normalize(name)
    def tag(*c, **kw):
        children, attrs = _parse_args(c, kw)
        return Tag(name, children, attrs)
    tag.__name__ = name
    return tag
