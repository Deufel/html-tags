import types, json
from html import escape
from html.parser import HTMLParser
from enum import Enum, auto
from functools import partial
from urllib.parse import quote

VOID = frozenset('area base br col embed hr img input link meta source track wbr'.split())
RAW = frozenset('script style'.split())
NS_ATTRS = {NS.SVG: 'xmlns="http://www.w3.org/2000/svg"', NS.MATH: 'xmlns="http://www.w3.org/1998/Math/MathML"'}
SVG_VOID = frozenset('circle ellipse line path polygon polyline rect stop set image use feBlend feColorMatrix feComposite feConvolveMatrix feDisplacementMap feDistantLight feDropShadow feFlood feFuncA feFuncB feFuncG feFuncR feGaussianBlur feImage feMergeNode feMorphology feOffset fePointLight feSpotLight feTile feTurbulence'.split())
MATH_VOID = frozenset('mprescripts none'.split())
NS_RULES = {NS.HTML: (VOID, False), NS.SVG: (SVG_VOID, True), NS.MATH: (MATH_VOID, False)}
ATTR_MAP = {'cls': 'class', '_class': 'class', '_for': 'for', '_from': 'from', '_in': 'in', '_is': 'is'}
DS_EVENT = 'datastar-patch-elements'
DS_SIGNAL = 'datastar-merge-signals'

class NS(Enum):
        HTML = auto()
        SVG  = auto()
        MATH = auto()

class Safe(str):
    def __html__(self): return self

def unpack(items):
    out = []
    for o in items:
        if o is None or o is False: continue
        elif isinstance(o, (list, tuple, types.GeneratorType)): out.extend(unpack(o))
        else: out.append(o)
    return tuple(out)

def _preproc(c, kw):
    ch, d = [], {}
    for o in c:
        if isinstance(o, dict): d.update(o)
        else: ch.append(o)
    d.update(kw)
    return unpack(ch), d

def render_attrs(d):
    out = []
    for k, v in d.items():
        k = ATTR_MAP.get(k, k.rstrip('_').replace('_', '-'))
        if v is True: out.append(f' {k}')
        elif v not in (False, None): out.append(f' {k}="{escape(str(v))}"')
    return ''.join(out)

def render(node, ns=NS.HTML):
    if isinstance(node, Safe): return str(node)
    if not isinstance(node, Tag): return escape(str(node))
    tag, children, a = node.tag, node.children, node.attrs
    new_ns = ns
    if tag == 'svg': new_ns = NS.SVG
    elif tag == 'math': new_ns = NS.MATH
    elif tag == 'foreignObject': new_ns = NS.HTML
    voids, sc = NS_RULES[new_ns]
    attr_str = render_attrs(a)
    if new_ns != ns and new_ns in NS_ATTRS:
        attr_str = f' {NS_ATTRS[new_ns]}' + attr_str
    if tag in voids: return f'<{tag}{attr_str} />' if sc else f'<{tag}{attr_str}>'
    if tag in RAW: return f'<{tag}{attr_str}>{"".join(str(c) for c in children)}</{tag}>'
    inner = ''.join(render(c, new_ns) for c in children)
    return f'<{tag}{attr_str}>{inner}</{tag}>'

def tag(tag, *c, **kw):
    c, kw = _preproc(c, kw)
    return Tag(tag, c, kw)

class Tag:
    def __init__(self, tag, cs=(), attrs=None):
        self.tag, self.children, self.attrs = tag, cs, attrs or {}
    def __call__(self, *c, **kw):
        c, kw = _preproc(c, kw)
        if c: self.children = self.children + c
        if kw: self.attrs = {**self.attrs, **kw}
        return self
    def __repr__(self): return f'{self.tag}({self.children}, {self.attrs})'

def mk_tag(name):
    """Create a Tag constructor for any element name."""
    tag_name = name.rstrip('_').replace('_', '-')
    def tag(*c, **kw):
        c, kw = _preproc(c, kw)
        return Tag(tag_name, c, kw)
    tag.__name__ = tag_name
    return tag

def Fragment(*c, **kw):
    c, kw = _preproc(c, kw)
    return Tag('', c, kw)

def sse_signal(data):
    return f"event: {DS_SIGNAL}\ndata: signals {json.dumps(data)}\n\n"

def render_pretty(node, ns=NS.HTML, depth=0, indent=2):
    if isinstance(node, Safe): return str(node)
    if not isinstance(node, Tag): return ' ' * (indent * depth) + escape(str(node))
    tag, children, a = node.tag, node.children, node.attrs
    new_ns = ns
    if tag == 'svg': new_ns = NS.SVG
    elif tag == 'math': new_ns = NS.MATH
    elif tag == 'foreignObject': new_ns = NS.HTML
    voids, sc = NS_RULES[new_ns]
    attr_str = render_attrs(a)
    if new_ns != ns and new_ns in NS_ATTRS:
        attr_str = f' {NS_ATTRS[new_ns]}' + attr_str
    pad = ' ' * (indent * depth)
    if tag in voids: return f'{pad}<{tag}{attr_str} />' if sc else f'{pad}<{tag}{attr_str}>'
    if tag in RAW: return f'{pad}<{tag}{attr_str}>{"".join(str(c) for c in children)}</{tag}>'
    inner = '\n'.join(render_pretty(c, new_ns, depth + 1, indent) for c in children)
    return f'{pad}<{tag}{attr_str}>\n{inner}\n{pad}</{tag}>'

def sse_patch(tag, indent=2):
    html = render_pretty(tag, indent=indent) if indent else render(tag)
    data = ''.join(f"data: elements {line}\n" for line in html.split('\n'))
    return f"event: {DS_EVENT}\n{data}\n"

def html_to_tag(s):
    stack, root = [[]], []
    class P(HTMLParser):
        def handle_starttag(self, tag, a):
            d = {k: (v if v is not None else True) for k, v in a}
            if tag in VOID | SVG_VOID: stack[-1].append(Tag(tag, (), d))
            else: stack.append([]); root.append((tag, d))
        def handle_endtag(self, tag):
            if tag in VOID | SVG_VOID: return
            children, (t, d) = tuple(stack.pop()), root.pop()
            stack[-1].append(Tag(t, children, d))
        def handle_data(self, data):
            if data.strip(): stack[-1].append(data.strip())
    P().feed(s)
    res = stack[0]
    return res[0] if len(res) == 1 else Fragment(*res)

def Datastar(v='1.0.0-RC.8'):
    """Datastar client library script tag."""
    return Tag('script', (), {
        'type': 'module',
        'src': f'https://cdn.jsdelivr.net/gh/starfederation/datastar@{v}/bundles/datastar.js'
    })

def MeCSS(v='v1.0.1'):
    return Tag('script', (), {'src': f'https://cdn.jsdelivr.net/gh/Deufel/toolbox@{v}/js/me_css.js'})

def Pointer(v='v1.0.1'):
    return Tag('script', (), {'src': f'https://cdn.jsdelivr.net/gh/Deufel/toolbox@{v}/js/pointer_events.js'})

def Favicon(emoji):
    s = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">{emoji}</text></svg>'
    return Tag('link', (), {'rel': 'icon', 'href': f'data:image/svg+xml,{quote(s, safe=":/@!,")}'})
