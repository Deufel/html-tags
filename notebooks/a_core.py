import marimo

__generated_with = "0.22.0"
app = marimo.App(width="medium")

with app.setup:
    import types, json 
    from html import escape
    from html.parser import HTMLParser
    from enum import Enum, auto
    from functools import partial
    from urllib.parse import quote



    class NS(Enum):
        HTML = auto()
        SVG  = auto()
        MATH = auto()

    VOID      = frozenset('area base br col embed hr img input link meta source track wbr'.split())
    RAW       = frozenset('script style'.split())

    NS_ATTRS = {NS.SVG: 'xmlns="http://www.w3.org/2000/svg"', NS.MATH: 'xmlns="http://www.w3.org/1998/Math/MathML"'}

    SVG_VOID = frozenset('circle ellipse line path polygon polyline rect stop set image use feBlend feColorMatrix feComposite feConvolveMatrix feDisplacementMap feDistantLight feDropShadow feFlood feFuncA feFuncB feFuncG feFuncR feGaussianBlur feImage feMergeNode feMorphology feOffset fePointLight feSpotLight feTile feTurbulence'.split())


    MATH_VOID = frozenset('mprescripts none'.split())
    NS_RULES  = {NS.HTML: (VOID, False), NS.SVG: (SVG_VOID, True), NS.MATH: (MATH_VOID, False)}
    ATTR_MAP  = {'cls': 'class', '_class': 'class', '_for': 'for', '_from': 'from', '_in': 'in', '_is': 'is'}


    DS_EVENT  = 'datastar-patch-elements'
    DS_SIGNAL = 'datastar-merge-signals'



@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Core
    """)
    return


@app.class_definition
class Safe(str):
    def __html__(self): return self


@app.function
def unpack(items):
    out = []
    for o in items:
        if o is None or o is False: continue
        elif isinstance(o, (list, tuple, types.GeneratorType)): out.extend(unpack(o))
        else: out.append(o)
    return tuple(out)


@app.function
def internal_preproc(c, kw):
    ch, d = [], {}
    for o in c:
        if isinstance(o, dict): d.update(o)
        else: ch.append(o)
    d.update(kw)
    return unpack(ch), d


@app.function
def render_attrs(d):
    out = []
    for k, v in d.items():
        k = ATTR_MAP.get(k, k.rstrip('_').replace('_', '-'))
        if v is True: out.append(f' {k}')
        elif v not in (False, None): out.append(f' {k}="{escape(str(v))}"')
    return ''.join(out)


@app.function
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


@app.function
def tag(tag, *c, **kw):
    c, kw = internal_preproc(c, kw)
    return Tag(tag, c, kw)


@app.class_definition
class Tag:
    def __init__(self, tag, cs=(), attrs=None):
        self.tag, self.children, self.attrs = tag, cs, attrs or {}
    def __call__(self, *c, **kw):
        c, kw = internal_preproc(c, kw)
        if c: self.children = self.children + c
        if kw: self.attrs = {**self.attrs, **kw}
        return self
    def __repr__(self): return f'{self.tag}({self.children}, {self.attrs})'


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Factory
    """)
    return


@app.function
def mk_tag(name):
    """Create a Tag constructor for any element name."""
    tag_name = name.rstrip('_').replace('_', '-')
    def tag(*c, **kw):
        c, kw = internal_preproc(c, kw)
        return Tag(tag_name, c, kw)
    tag.__name__ = tag_name
    return tag


@app.function
def Fragment(*c, **kw):
    c, kw = internal_preproc(c, kw)
    return Tag('', c, kw)


@app.cell
def _():
    div, span, p, h1, h2, h3 = partial(tag,'div'), partial(tag,'span'), partial(tag,'p'), partial(tag,'h1'), partial(tag,'h2'), partial(tag,'h3')
    img, br, hr, input_ = partial(tag,'img'), partial(tag,'br'), partial(tag,'hr'), partial(tag,'input')
    ul, ol, li, a = partial(tag,'ul'), partial(tag,'ol'), partial(tag,'li'), partial(tag,'a')
    form, button, label, select, option, textarea = partial(tag,'form'), partial(tag,'button'), partial(tag,'label'), partial(tag,'select'), partial(tag,'option'), partial(tag,'textarea')
    table, thead, tbody, tr, th, td = partial(tag,'table'), partial(tag,'thead'), partial(tag,'tbody'), partial(tag,'tr'), partial(tag,'th'), partial(tag,'td')
    header, footer, main, section, article, nav = partial(tag,'header'), partial(tag,'footer'), partial(tag,'main'), partial(tag,'section'), partial(tag,'article'), partial(tag,'nav')
    script, style, link, meta = partial(tag,'script'), partial(tag,'style'), partial(tag,'link'), partial(tag,'meta')
    svg_el, path, circle, rect, line = partial(tag,'svg'), partial(tag,'path'), partial(tag,'circle'), partial(tag,'rect'), partial(tag,'line')
    return circle, div, line, p, path, rect, span, svg_el


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## SSE Helpers
    """)
    return


@app.function
def sse_signal(data):
    return f"event: {DS_SIGNAL}\ndata: signals {json.dumps(data)}\n\n"


@app.function
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


@app.function
def sse_patch(tag, indent=2):
    html = render_pretty(tag, indent=indent) if indent else render(tag)
    data = ''.join(f"data: elements {line}\n" for line in html.split('\n'))
    return f"event: {DS_EVENT}\n{data}\n"


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## html -> tag
    """)
    return


@app.function
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Extras
    """)
    return


@app.function
def Datastar(v='1.0.0-RC.8'):
    """Datastar client library script tag."""
    return Tag('script', (), {
        'type': 'module',
        'src': f'https://cdn.jsdelivr.net/gh/starfederation/datastar@{v}/bundles/datastar.js'
    })


@app.function
def MeCSS(v='v1.0.1'):
    return Tag('script', (), {'src': f'https://cdn.jsdelivr.net/gh/Deufel/toolbox@{v}/js/me_css.js'})


@app.function
def Pointer(v='v1.0.1'):
    return Tag('script', (), {'src': f'https://cdn.jsdelivr.net/gh/Deufel/toolbox@{v}/js/pointer_events.js'})


@app.function
def Favicon(emoji):
    s = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">{emoji}</text></svg>'
    return Tag('link', (), {'rel': 'icon', 'href': f'data:image/svg+xml,{quote(s, safe=":/@!,")}'})


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Exploratory Testing
    """)
    return


@app.cell
def _(div, mo, p, span):

    def card(*children, **kw):
        return div(cls="card", style="background:#fff;border-radius:12px;padding:1.25rem 1.5rem", **kw)(*children)

    def badge(text, variant='ok'):
        styles = dict(ok='background:#E1F5EE;color:#0F6E56', warn='background:#FAEEDA;color:#854F0B', bad='background:#FCEBEB;color:#A32D2D')
        return span(text, style=f'font-size:.68rem;font-weight:600;padding:2px 7px;border-radius:20px;{styles[variant]}')

    mo.Html( render(card(badge("lapsing", "bad"), badge("ok"), p("Some content"))))
    return


@app.cell
def _(circle, line, mo, path, rect, svg_el):
    def test_svg():
        return svg_el({"viewBox": "0 0 200 200"}, width="200", height="200", style="background:#f8fafc")(
            circle({"cx": "100", "cy": "100", "r": "80"}, fill="none", stroke="#378ADD", stroke_width="3"),
            path({"d": "M 60 100 Q 100 40 140 100 Q 100 160 60 100"}, fill="#378ADD", opacity="0.2"),
            rect(x="70", y="70", width="60", height="60", rx="8", fill="none", stroke="#1D9E75", stroke_width="2", stroke_dasharray="4 2"),
            line({"x1": "100", "y1": "20", "x2": "100", "y2": "180"}, stroke="#94a3b8", stroke_width="1", stroke_linecap="round"),
            tag('text', "SVG Test", {"text-anchor": "middle", "dominant-baseline": "middle"}, x="100", y="100", fill="#0f172a", font_size="14", font_weight="bold"),
            tag('g', {"transform": "translate(100,100)"})(
                circle(r="4", fill="#D85A30"),
                tag('animateTransform', {"attributeName": "transform", "type": "rotate", "from": "0", "to": "360", "dur": "4s", "repeatCount": "indefinite"}),
            ),
        )

    mo.Html(render_pretty(test_svg()))
    return


@app.cell
def _(circle, mo, rect, svg_el):
    def animated_svg():
        return svg_el({"viewBox": "0 0 300 200"}, width="300", height="200", style="background:#0f172a;border-radius:12px")(
            rect(x="0", y="0", width="300", height="200", fill="#0f172a"),
            tag('defs')(
                tag('linearGradient', {"id": "grad1", "x1": "0%", "y1": "0%", "x2": "100%", "y2": "100%"})(
                    tag('stop', {"offset": "0%", "stop-color": "#378ADD"}),
                    tag('stop', {"offset": "100%", "stop-color": "#1D9E75"}),
                ),
            ),
            circle(cx="150", cy="100", r="40", fill="none", stroke="url(#grad1)", stroke_width="2")(
                tag('animate', {"attributeName": "r", "values": "40;50;40", "dur": "3s", "repeatCount": "indefinite"}),
                tag('animate', {"attributeName": "opacity", "values": "1;0.4;1", "dur": "3s", "repeatCount": "indefinite"}),
            ),
            circle(cx="150", cy="100", r="60", fill="none", stroke="#378ADD", opacity="0.3", stroke_width="1")(
                tag('animate', {"attributeName": "r", "values": "60;70;60", "dur": "4s", "repeatCount": "indefinite"}),
            ),
            tag('g')(
                circle(cx="150", cy="100", r="6", fill="#1D9E75"),
                tag('animateTransform', {"attributeName": "transform", "type": "rotate", "from": "0 150 100", "to": "360 150 100", "dur": "6s", "repeatCount": "indefinite"}),
                circle(cx="150", cy="60", r="4", fill="#378ADD"),
            ),
            tag('g')(
                tag('animateTransform', {"attributeName": "transform", "type": "rotate", "from": "360 150 100", "to": "0 150 100", "dur": "4s", "repeatCount": "indefinite"}),
                circle(cx="150", cy="50", r="3", fill="#D85A30"),
            ),
            *[tag('g')(
                tag('animateTransform', {"attributeName": "transform", "type": "rotate", "from": f"{i*30} 150 100", "to": f"{i*30+360} 150 100", "dur": f"{8+i}s", "repeatCount": "indefinite"}),
                circle(cx="150", cy=str(25 + i*5), r="1.5", fill="#94a3b8", opacity="0.5"),
            ) for i in range(6)],
            tag('text', "⬡", {"text-anchor": "middle", "dominant-baseline": "middle"}, x="150", y="100", fill="white", font_size="16")(
                tag('animate', {"attributeName": "opacity", "values": "1;0.5;1", "dur": "2s", "repeatCount": "indefinite"}),
            ),
        )

    mo.Html(render(animated_svg()))

    return


@app.cell
def _(rect, svg_el):
    def heatmap(rows):
        from datetime import date, timedelta
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
        return svg_el({"viewBox": f"0 0 {52*STEP} {7*STEP}"}, width='100%', height=str(7*STEP), style='display:block')(*cells)

    return (heatmap,)


@app.cell
def _(heatmap, mo):
    import random
    from datetime import date, timedelta

    today = date.today()
    test_rows = [dict(date=(today - timedelta(days=i)).isoformat(), cases=random.randint(0, 20)) for i in range(365)]
    mo.Html(render(heatmap(test_rows)))

    return


@app.cell
def _():
    math = mk_tag('math')
    mi = mk_tag('mi')
    mn = mk_tag('mn')
    moo = mk_tag('mo')
    msup = mk_tag('msup')
    mrow = mk_tag('mrow')

    eq = math(display="block")(
        mrow()(
            mi("x"), moo("="), 
            msup()(
                mn("2"), mn("3")
            )
        )
    )

    print(render_pretty(eq))
    return (eq,)


@app.cell
def _(eq, mo):
    mo.Html(render_pretty(eq))
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
