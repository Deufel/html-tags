import types
from html import escape
from html.parser import HTMLParser
from urllib.parse import quote

VOID = frozenset('area base br col embed hr img input link meta source track wbr'.split())
RAW = frozenset('script style'.split())
SVG_VOID = frozenset('circle ellipse line path polygon polyline rect stop set image use feBlend feColorMatrix feComposite feConvolveMatrix feDisplacementMap feDistantLight feDropShadow feFlood feFuncA feFuncB feFuncG feFuncR feGaussianBlur feImage feMergeNode feMorphology feOffset fePointLight feSpotLight feTile feTurbulence'.split())
MATH_VOID = frozenset('mprescripts none'.split())
NS_RULES = {'html': (VOID, False), 'svg': (SVG_VOID, True), 'math': (MATH_VOID, False)}
NS_ATTRS = {'svg': 'xmlns="http://www.w3.org/2000/svg"', 'math': 'xmlns="http://www.w3.org/1998/Math/MathML"'}
ATTR_MAP = {'cls': 'class', '_class': 'class', '_for': 'for', '_from': 'from', '_in': 'in', '_is': 'is'}

"""HTML/SVG tag construction and rendering — pure-functional, closure-based.

    A tag is a closure capturing (name, children, attrs) and callable to produce
    a new closure with additional children/attrs. No mutation anywhere.
    """

class Safe(str):
    """A string that is already HTML-safe and will not be escaped on render."""
    def __html__(self): return self

def unpack(items):
    """Flatten nested iterables, dropping None and False."""
    out = []
    for o in items:
        if o is None or o is False:
            continue
        elif isinstance(o, (list, tuple, types.GeneratorType)):
            out.extend(unpack(o))
        else:
            out.append(o)
    return tuple(out)

def _preproc(c, kw):
    """Separate positional children from dict-style attr overrides."""
    ch, d = [], {}
    for o in c:
        if isinstance(o, dict): d.update(o)
        else:                   ch.append(o)
    d.update(kw)
    return unpack(ch), d

def is_tag(x):
    """Duck-type check: a tag is any callable with our marker attribute."""
    return getattr(x, '_is_tag', False)

def tag(name, children=(), attrs=None):
    """Construct a tag closure.

    The returned object is callable: calling it with more children/attrs
    returns a *new* tag closure. Nothing mutates. The closure exposes
    .tag, .children, .attrs for introspection and rendering.
    """
    attrs = attrs or {}

    def extend(*c, **kw):
        nc, nd = _preproc(c, kw)
        return tag(name, children + nc, {**attrs, **nd})

    extend.tag      = name
    extend.children = children
    extend.attrs    = attrs
    extend._is_tag  = True
    extend.__html__ = lambda: render(extend)
    extend.__repr__ = lambda: f'{name}({children!r}, {attrs!r})'
    return extend

def render_attrs(d):
    """Render an attribute dict to an HTML attribute string."""
    out = []
    for k, v in d.items():
        k = ATTR_MAP.get(k, k.rstrip('_').replace('_', '-'))
        if v is True:
            out.append(f' {k}')
        elif v not in (False, None):
            out.append(f' {k}="{escape(str(v))}"')
    return ''.join(out)

def render(node, ns='html', depth=0, indent=2):
    """Recursively render a tag (or any value) to an HTML string."""
    if isinstance(node, Safe):
        return str(node)
    if not is_tag(node):
        return ' ' * (indent * depth) + escape(str(node))

    name, children, a = node.tag, node.children, node.attrs

    # Namespace tracking for SVG / MathML / foreignObject
    new_ns = ns
    if   name == 'svg':           new_ns = 'svg'
    elif name == 'math':          new_ns = 'math'
    elif name == 'foreignObject': new_ns = 'html'

    voids, self_close = NS_RULES[new_ns]
    attr_str = render_attrs(a)
    if name in NS_ATTRS:
        attr_str = f' {NS_ATTRS[name]}' + attr_str

    pad = ' ' * (indent * depth)

    if name in voids:
        return f'{pad}<{name}{attr_str} />' if self_close else f'{pad}<{name}{attr_str}>'
    if name in RAW:
        return f'{pad}<{name}{attr_str}>{"".join(str(c) for c in children)}</{name}>'
    if len(children) == 1 and not is_tag(children[0]) and not isinstance(children[0], Safe):
        return f'{pad}<{name}{attr_str}>{escape(str(children[0]))}</{name}>'

    inner = '\n'.join(render(c, new_ns, depth + 1, indent) for c in children)
    return f'{pad}<{name}{attr_str}>\n{inner}\n{pad}</{name}>'

def html_doc(head, body, lang='en'):
    """Wrap head + body in a full <!DOCTYPE html> document."""
    h = tag('html', (head, body), {'lang': lang})
    return Safe(f'<!DOCTYPE html>\n{render(h)}')

def mk_tag(name):
    """Return a constructor for the given element name.

    Trailing underscores and underscores become hyphens so that Python-reserved
    names and custom elements work naturally::

        data_list = mk_tag('data_list')       # → <data-list>
        my_comp   = mk_tag('my_component_')   # → <my-component>
    """
    clean = name.rstrip('_').replace('_', '-')
    def ctor(*c, **kw):
        c, kw = _preproc(c, kw)
        return tag(clean, c, kw)
    ctor.__name__ = clean
    return ctor

def html_to_tag(s):
    """Parse an HTML string into a tag tree (or tuple of tags)."""
    stack, root = [[]], []

    class P(HTMLParser):
        def handle_starttag(self, t, a):
            d = {k: (v if v is not None else True) for k, v in a}
            if t in VOID | SVG_VOID:
                stack[-1].append(tag(t, (), d))
            else:
                stack.append([])
                root.append((t, d))

        def handle_endtag(self, t):
            if t in VOID | SVG_VOID:
                return
            children, (name, d) = tuple(stack.pop()), root.pop()
            stack[-1].append(tag(name, children, d))

        def handle_data(self, data):
            if data.strip():
                stack[-1].append(data.strip())

    P().feed(s)
    res = stack[0]
    return res[0] if len(res) == 1 else tuple(res)

def Datastar(v='1.0.0'):
    """Script tag for the Datastar client library.

    Pass ``v='latest'`` for the main branch, or any tag like ``v='1.0.0-beta.11'``.
    """
    ref = 'main' if v == 'latest' else v
    return tag('script', (), {
        'type': 'module',
        'src':  f'https://cdn.jsdelivr.net/gh/starfederation/datastar@{ref}/bundles/datastar.js',
    })

def MeCSS(v='v1.0.1'):
    """Script tag for the me_css.js helper."""
    return tag('script', (), {
        'src': f'https://cdn.jsdelivr.net/gh/Deufel/toolbox@{v}/js/me_css.js',
    })

def Pointer(v='v1.0.1'):
    """Script tag for the pointer_events.js helper."""
    return tag('script', (), {
        'src': f'https://cdn.jsdelivr.net/gh/Deufel/toolbox@{v}/js/pointer_events.js',
    })

def Favicon(emoji):
    """Link tag that sets an emoji favicon via an inline SVG data URI."""
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
         f'<text y=".9em" font-size="90">{emoji}</text></svg>')
    return tag('link', (), {
        'rel':  'icon',
        'href': f'data:image/svg+xml,{quote(s, safe=":/@!,")}',
    })
