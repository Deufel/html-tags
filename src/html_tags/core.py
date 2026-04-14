import types, json
from html import escape
from html.parser import HTMLParser
from functools import partial
from urllib.parse import quote

VOID = frozenset('area base br col embed hr img input link meta source track wbr'.split())
RAW = frozenset('script style'.split())
SVG_VOID = frozenset('circle ellipse line path polygon polyline rect stop set image use feBlend feColorMatrix feComposite feConvolveMatrix feDisplacementMap feDistantLight feDropShadow feFlood feFuncA feFuncB feFuncG feFuncR feGaussianBlur feImage feMergeNode feMorphology feOffset fePointLight feSpotLight feTile feTurbulence'.split())
MATH_VOID = frozenset('mprescripts none'.split())
NS_RULES = {'html': (VOID, False), 'svg': (SVG_VOID, True), 'math': (MATH_VOID, False)}
NS_ATTRS = {'svg': 'xmlns="http://www.w3.org/2000/svg"', 'math': 'xmlns="http://www.w3.org/1998/Math/MathML"'}
ATTR_MAP = {'cls': 'class', '_class': 'class', '_for': 'for', '_from': 'from', '_in': 'in', '_is': 'is'}
DS_EVENT = 'datastar-patch-elements'
DS_SIGNAL = 'datastar-merge-signals'

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

class Tag:
    def __init__(self, tag, cs=(), attrs=None):
        self.tag, self.children, self.attrs = tag, cs, attrs or {}
    def __call__(self, *c, **kw):
        c, kw = _preproc(c, kw)
        if c: self.children = self.children + c
        if kw: self.attrs = {**self.attrs, **kw}
        return self
    def __repr__(self): return f'{self.tag}({self.children}, {self.attrs})'

def render(node, ns='html', depth=0, indent=2):
    if isinstance(node, Safe): return str(node)
    if not isinstance(node, Tag): return ' ' * (indent * depth) + escape(str(node))
    tag, children, a = node.tag, node.children, node.attrs
    new_ns = ns
    if tag == 'svg': new_ns = 'svg'
    elif tag == 'math': new_ns = 'math'
    elif tag == 'foreignObject': new_ns = 'html'
    voids, sc = NS_RULES[new_ns]
    attr_str = render_attrs(a)
    if tag in NS_ATTRS:
        attr_str = f' {NS_ATTRS[tag]}' + attr_str
    pad = ' ' * (indent * depth)
    if tag in voids: return f'{pad}<{tag}{attr_str} />' if sc else f'{pad}<{tag}{attr_str}>'
    if tag in RAW: return f'{pad}<{tag}{attr_str}>{"".join(str(c) for c in children)}</{tag}>'
    if len(children) == 1 and not isinstance(children[0], Tag):
        return f'{pad}<{tag}{attr_str}>{escape(str(children[0]))}</{tag}>'
    inner = '\n'.join(render(c, new_ns, depth + 1, indent) for c in children)
    return f'{pad}<{tag}{attr_str}>\n{inner}\n{pad}</{tag}>'

def html_doc(head, body, lang='en'):
    h = Tag('html', (head, body), {'lang': lang})
    return Safe(f'<!DOCTYPE html>\n{render(h)}')

def mk_tag(name):
    tag_name = name.rstrip('_').replace('_', '-')
    def _tag(*c, **kw):
        c, kw = _preproc(c, kw)
        return Tag(tag_name, c, kw)
    _tag.__name__ = tag_name
    return _tag

def sse_signal(data):
    return f"event: {DS_SIGNAL}\ndata: signals {json.dumps(data)}\n\n"

def sse_patch(tag, indent=2):
    html = render(tag, indent=indent) if indent else render(tag)
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
    return res[0] if len(res) == 1 else tuple(res)

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

def heatmap(rows):
    from datetime import date, timedelta
    from html_tags import mk_tag, render
    svg, rect = mk_tag('svg'), mk_tag('rect')

    today, start = date.today(), date.today() - timedelta(weeks=52)
    by_date = {r['date']: r['cases'] for r in rows}
    mx = max(by_date.values(), default=1) or 1
    CELL, GAP, STEP = 11, 2, 13
    cells = []
    for week in range(52):
        for dow in range(7):
            d = start + timedelta(weeks=week, days=dow)
            if d > today: continue
            i = by_date.get(d.isoformat(), 0) / mx
            cells.append(rect(x=str(week*STEP), y=str(dow*STEP), width=str(CELL), height=str(CELL), rx='2',
                              fill=f'oklch({int(96-i*52)}% {0.04+i*0.16:.3f} 142)'))

    print(len(cells))  # should be ~364
    result = svg({"viewBox": f"0 0 {52*STEP} {7*STEP}"}, width='100%', height=str(7*STEP), style='display:block')(*cells)
    print(render(result)[:200])  # first 200 chars
    return result
