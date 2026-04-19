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

"""HTML/SVG/MathML tag construction and rendering.

    A tag is a closure capturing (name, children, attrs) and callable to produce
    a new closure with extended children/attrs. No mutation. Parameter docs use
    the fastcore docments convention: one-line description above the signature,
    per-parameter details as inline comments next to each parameter.
    """

class Safe(str):
    """A string that is already HTML-safe and will not be escaped on render."""
    def __html__(self): return self

def unpack(
    items, # iterable of values to flatten
):         # tuple with nested lists/tuples/generators expanded, `None` and `False` dropped
    "Flatten nested iterables, dropping `None` and `False` values."
    out = []
    for o in items:
        if o is None or o is False:
            continue
        elif isinstance(o, (list, tuple, types.GeneratorType)):
            out.extend(unpack(o))
        else:
            out.append(o)
    return tuple(out)

def _preproc(
    c,  # positional args (may include dicts treated as attrs)
    kw, # keyword args to be pythonified into attrs
):      # tuple of (flattened_children, final_attrs_dict)
    """Split positional children from attrs and normalize kwarg keys.
 
    Dict keys pass through verbatim. Kwarg keys are Pythonified — looked up in
    `ATTR_MAP`, trailing underscore stripped, internal underscores become
    hyphens. Transformation happens here so attrs dicts are always in their
    final form once inside a tag.
    """
    ch, d = [], {}
    for o in c:
        if isinstance(o, dict): d.update(o)
        else:                   ch.append(o)
    for k, v in kw.items():
        k = ATTR_MAP.get(k, k.rstrip('_').replace('_', '-'))
        d[k] = v
    return unpack(ch), d

def is_tag(
    x, # any value
):     # True if `x` is a tag closure (has the `_is_tag` marker)
    "Duck-type check for tag closures."
    return getattr(x, '_is_tag', False)

def tag(
    name,         # element name, e.g. 'div', 'svg', 'my-component'
    children=(),  # tuple of child tags/strings/Safe values
    attrs=None,   # attribute dict (keys emitted verbatim)
):                # tag closure — callable, carries `.tag`/`.children`/`.attrs`/`_is_tag`
    """Construct a tag closure.
 
    The returned object is callable: calling it with more children/attrs
    returns a *new* tag closure. Nothing mutates. The closure exposes
    `.tag`, `.children`, `.attrs` for introspection and rendering.
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

def render_attrs(
    d, # attribute dict (keys already in final HTML form)
):     # serialized attribute string, leading space included per attr
    """Serialize an attribute dict to an HTML attribute string.
 
    Values: `True` renders a bare attr name, `False`/`None` omits, everything
    else is str-escaped and quoted. Keys are emitted verbatim — all transforms
    happen upstream in `_preproc`.
    """
    out = []
    for k, v in d.items():
        if v is True:
            out.append(f' {k}')
        elif v not in (False, None):
            out.append(f' {k}="{escape(str(v))}"')
    return ''.join(out)

def render(
    node,        # tag closure, Safe string, or any value (stringified + escaped)
    ns='html',   # current namespace: 'html', 'svg', or 'math'
    depth=0,     # indentation depth for pretty-printing
    indent=2,    # spaces per indent level
):               # rendered HTML string
    """Recursively render a tag tree to HTML.
 
    Namespace switches automatically at `<svg>`, `<math>`, and back to HTML
    inside `<foreignObject>`. Void elements follow per-namespace rules (HTML
    voids render without closing, SVG voids self-close XML-style).
    """
    if isinstance(node, Safe):
        return str(node)
    if not is_tag(node):
        return ' ' * (indent * depth) + escape(str(node))
 
    name, children, a = node.tag, node.children, node.attrs
 
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

def html_doc(
    head,      # a <head> tag (or any tag/string placed in head position)
    body,      # a <body> tag (or any tag/string placed in body position)
    lang='en', # value for the `<html lang="...">` attribute
):             # a Safe string containing `<!DOCTYPE html>` followed by the rendered document
    "Wrap head + body in a full `<!DOCTYPE html>` document."
    h = tag('html', (head, body), {'lang': lang})
    return Safe(f'<!DOCTYPE html>\n{render(h)}')

def mk_tag(
    name, # element name, underscores → hyphens, trailing `_` stripped
):        # a constructor `ctor(*children, **attrs)` that returns a tag closure
    """Return a constructor for the given element name.
 
    `mk_tag('data_list')` gives `<data-list>`; `mk_tag('input_')` gives
    `<input>` (useful for Python-reserved names). The module also exposes
    a `__getattr__` so `from html_tags import any_name` auto-calls this.
    """
    clean = name.rstrip('_').replace('_', '-')
    def ctor(*c, **kw):
        c, kw = _preproc(c, kw)
        return tag(clean, c, kw)
    ctor.__name__ = clean
    return ctor

def __getattr__(
    name, # any attribute name not already defined in the module
):        # a tag constructor for that name
    """Module-level fallback: `from html_tags import div, my_thing` works for any name.
 
    Dunder names (`__foo__`) raise `AttributeError` so Python's internals
    (pickle probes, IDE introspection, etc.) don't get hijacked into tags.
    """
    if name.startswith('_'):
        raise AttributeError(name)
    return mk_tag(name)

def html_to_tag(
    s, # HTML source string
):     # a single tag (if one top-level element) or tuple of tags
    """Parse an HTML string into a tag tree.
 
    Attributes with no value (`<input required>`) become `True` in the attrs
    dict. Whitespace-only text nodes are dropped. Self-closing / void elements
    in either HTML or SVG sets are handled.
    """
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

def Datastar(
    v='latest', # version tag, `'latest'` for main branch, or e.g. `'1.0.0-beta.11'`
):             # `<script type="module">` tag loading the Datastar bundle
    "Script tag for the Datastar client library."
    ref = 'main' if v == 'latest' else v
    return tag('script', (), {
        'type': 'module',
        'src':  f'https://cdn.jsdelivr.net/gh/starfederation/datastar@{ref}/bundles/datastar.js',
    })

def MeCSS(
    v='latest', # toolbox release tag
):              # `<script>` tag loading `me_css.js`
    "Script tag for the `me_css.js` helper (scoped `<style>` blocks)."
    return tag('script', (), {
        'src': f'https://cdn.jsdelivr.net/gh/Deufel/toolbox@{v}/js/me_css.js',
    })

def Pointer(
    v='latest', # toolbox release tag
):              # `<script>` tag loading `pointer_events.js`
    "Script tag for `pointer_events.js` (drives `.hover`/`.active`/`.disabled` on `.btn` elements) to avoid the requirement of using normal hover & js for ios touch just use the pointer api it generalises better (imho)."
    return tag('script', (), {
        'src': f'https://cdn.jsdelivr.net/gh/Deufel/toolbox@{v}/js/pointer_events.js',
    })

def Highlight(
    v='latest', # toolbox release tag
):              # `<script type="module">` tag loading `highlight.js`
    "Script tag for `highlight.js` (CSS Custom Highlight API syntax highlighter)."
    return tag('script', (), {
        'type': 'module',
        'src':  f'https://cdn.jsdelivr.net/gh/Deufel/toolbox@{v}/js/highlight.js',
    })

def Color_type_css(
    v='latest', # toolbox release tag
):              # `<link rel="stylesheet">` tag
    "Link tag for the toolbox core stylesheet (Color & Type system). Complex CSS for a simple API"
    return tag('link', (), {
        'rel':  'stylesheet',
        'href': f'https://cdn.jsdelivr.net/gh/Deufel/toolbox@{v}/css/style.css',
    })

def Favicon(
    emoji, # a single-character emoji or short text to embed as the favicon
):         # `<link rel="icon">` tag with an inline SVG data URI
    "Favicon link tag built from an inline SVG data URI — no image file needed."
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
         f'<text y=".9em" font-size="90">{emoji}</text></svg>')
    return tag('link', (), {
        'rel':  'icon',
        'href': f'data:image/svg+xml,{quote(s, safe=":/@!,")}',
    })

def Layout(main,
           *, 
           header=None, 
           nav=None,
           aside=None,
           footer=None, 
          ):
    _body   = mk_tag('body')
    _header = mk_tag("header")
    _nav    = mk_tag("nav")
    _main   = mk_tag("main")
    _aside  = mk_tag("aside")
    _footer = mk_tag("footer")
    return _body(cls=f"surface")(
        header and _header(id="header")(header),
        nav    and _nav(id="nav")(nav),
        _main(id="main", cls="surface")(main),
        aside  and _aside(id="aside")(aside),
        footer and _footer(id="footer")(footer),
    )
