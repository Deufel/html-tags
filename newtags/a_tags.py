import marimo

__generated_with = "0.22.0"
app = marimo.App()

with app.setup:
    from html import escape
    from dataclasses import dataclass, field
    from html.parser import HTMLParser
    import xml.etree.ElementTree as ET

    HTML5 = dict(
        void=set('area base br col embed hr img input link meta source track wbr'.split()),
        raw=set('script style'.split()),
        ns_switch=dict(svg='svg', math='math', foreignObject='html'),
        ns_attrs=dict(svg='http://www.w3.org/2000/svg', math='http://www.w3.org/1998/Math/MathML'))
    HTML5['inline'] = set('a b code em i span strong'.split())
    HTML5['preserve'] = set('pre textarea'.split())



@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    You build a tree. The renderer asks the tree what it is, the profile what the rules are, and the formatter what it should look like. Three jobs, three places.

    A tag is data. `El("div", {...}, (...))` holds a name, attrs, and children — nothing more. `Txt` and `Raw` are leaves. `Frag` is a tuple of siblings with no wrapper.

    Authoring builds that tree. `mk_tag("div")` returns a constructor; calling it makes an `El`; calling the `El` again extends it. `cls=` becomes `class=`, `None` and `False` drop out, strings become `Txt`. The tree is the only thing your components return.

    The profile is a table. It lists which names are void, which are raw, which switch namespace. HTML5 is one table; SVG sits inside it as a switch rule. Want a different dialect? Pass a different table.

    The walk turns the tree into events: `open`, `close`, `void`, `txt`, `raw`. It consults the profile, tracks the namespace, flattens fragments. It does not format.

    The formatter turns events into a string. Indent, escape, join. It does not know about HTML.

    To change look, edit the formatter. To change dialect, edit the profile. To change shape, edit the tree. Each change stays in its own room.

    ```
       author code              data                 rules
      ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
      │  mk_tag,     │───▶│ El, Txt, Raw │    │   HTML5      │
      │  tag, frag,  │    │   Frag       │    │   profile    │
      │  components  │    └──────┬───────┘    └──────┬───────┘
      └──────────────┘           │                   │
                                 ▼                   │
                          ┌──────────────┐           │
                          │    walk      │◀──────────┘
                          │  tree→events │
                          └──────┬───────┘
                                 │  open / close / void / txt / raw
                                 ▼
                          ┌──────────────┐
                          │     fmt      │
                          │ events→string│
                          └──────┬───────┘
                                 ▼
                              HTML out
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A roadmap, smallest-meaningful-step first. Each item should be runnable and checkable on its own.

    1. **Node types** — `El`, `Txt`, `Raw`, `Frag`. Build a couple by hand, eyeball the repr.
    2. **Authoring helpers** — `_flat`, `_kid`, `_kids`, `_attrs`, `ATTR_MAP`, `tag`, `frag`, `mk_tag`, `El.__call__`. Check that `div(cls='x')(p('hi'))` builds the expected tree.
    3. **HTML5 profile** — the data table only. No code consumes it yet; just print it and confirm it's the shape you want.
    4. **Walk** — tree → event stream. Test on a flat doc, a nested doc, a fragment, a void element, an SVG subtree. Confirm namespace switching shows up in the events.
    5. **Format** — events → string, with the indentation behaviour you want for SSE / brotli. Test against the same fixtures as step 4.
    6. **`render`** — one-line composition of walk + fmt. This is the public entry point.
    7. **Whitespace cases** — text-only elements on one line, `<pre>` preserve, inline elements no break. Add the profile flags, extend `fmt`, regression-test against step 5.
    8. **Module `__getattr__` + cache** — auto-tags by import, stash on the module so repeat lookups are free.
    9. **`html_doc` and `Layout`** — rebuild as thin wrappers returning `Frag` / `El`. Confirm no double-`<body>`.
    10. **`html_to_tag`** — pick a parser that preserves case so SVG round-trips. Decide whether to keep `HTMLParser` for HTML and add a separate XML path, or switch wholesale.
    11. **Cdn helpers** — `Datastar`, `MeCSS`, `Pointer`, `Highlight`, `Color_type_css`, `Favicon`. Mechanical port.
    12. **`Show`** — port the iframe wrapper on top of the new `render`.
    13. **Context-aware escaping** — pass `escape_for(ctx)` into `fmt`, branch on body / attr / url / js / css. Bolt-on, doesn't touch the tree.
    14. **Regression suite** — the five-failure cell from earlier becomes the test fixture. Add fragment, multi-root parse, `<pre>`, inline mixing, SVG case.

    Want to start at step 1?
    """)
    return


@app.cell
def _():


    class Frag(tuple): pass
    @dataclass
    class Txt: s:str
    @dataclass
    class Raw: s:str
    @dataclass
    class El: name:str; attrs:dict=field(default_factory=dict); kids:tuple=()


    return El, Frag, Raw, Txt


@app.cell
def _(El, Frag, Raw, Txt):
    ATTR_MAP = dict(cls='class', _for='for', _in='in', _is='is')

    def _norm(k): return ATTR_MAP.get(k, k.rstrip('_').replace('_','-'))
    def _attrs(kw): return {_norm(k):v for k,v in kw.items()}

    def _flat(xs):
        for x in xs:
            if x is None or x is False: continue
            elif isinstance(x,(list,tuple)) and not isinstance(x,Frag): yield from _flat(x)
            else: yield x

    def _kid(x): return x if isinstance(x,(El,Txt,Raw,Frag)) else Txt(str(x))
    def _kids(c): return tuple(_kid(x) for x in _flat(c))

    El.__call__ = lambda self,*c,**kw: El(self.name, {**self.attrs, **_attrs(kw)}, self.kids + _kids(c))

    def _attrs_from(c, kw):
        d = {}
        rest = []
        for o in c:
            if isinstance(o, dict): d.update(o)
            else: rest.append(o)
        d.update(_attrs(kw))
        return d, rest

    def tag(name,*c,**kw): d,c = _attrs_from(c,kw); return El(name, d, _kids(c))
    
    El.__call__ = lambda self,*c,**kw: (lambda d,c: El(self.name, {**self.attrs, **d}, self.kids + _kids(c)))(*_attrs_from(c,kw))

    def frag(*c): return Frag(_kids(c))
    def mk_tag(name): n=name.rstrip('_').replace('_','-'); return lambda *c,**kw: tag(n,*c,**kw)

    return frag, mk_tag


@app.cell
def _(mk_tag):
    div,p = mk_tag('div'),mk_tag('p')
    div(cls='card')(p('hi'), None, [p('two'), False, p('three')])
    return div, p


@app.cell
def _():
    return


@app.cell
def _():
    HTML5
    return


@app.cell
def _(Frag, Raw, Txt):

    def _mode(name, prof):
        if name in prof['preserve']: return 'preserve'
        if name in prof['raw']:      return 'raw'
        if name in prof['inline']:   return 'inline'
        return 'block'

    def walk(node, prof, ns='html'):
        if isinstance(node,(list,tuple,Frag)):
            for c in node: yield from walk(c,prof,ns)
            return
        if isinstance(node,Txt): yield 'txt',node.s; return
        if isinstance(node,Raw): yield 'raw',node.s; return
        nns = prof['ns_switch'].get(node.name, ns)
        a = node.attrs
        if node.name in prof['ns_attrs']: a = {'xmlns':prof['ns_attrs'][node.name], **a}
        if node.name in prof['void']: yield 'void',node.name,a; return
        m = _mode(node.name, prof)
        yield 'open',node.name,a,m
        for c in node.kids: yield from walk(c,prof,nns)
        yield 'close',node.name,m


    return (walk,)


@app.cell
def _(div, mk_tag, p, walk):
    svg,circle,br = mk_tag('svg'),mk_tag('circle'),mk_tag('br')
    list(walk(div(cls='card')(p('hi'), br(), svg(viewBox='0 0 1 1')(circle(r=1))), HTML5))
    return br, circle, svg


@app.function
def render_attrs(d):
    out = []
    for k,v in d.items():
        if v is True: out.append(f' {k}')
        elif v not in (False,None): out.append(f' {k}="{escape(str(v))}"')
    return ''.join(out)


@app.cell
def _(br, circle, div, fmt, p, svg, walk):
    print(fmt(walk(div(cls='card')(p('hi'), br(), svg(viewBox='0 0 1 1')(circle(r=1))), HTML5)))

    return


@app.cell
def _():
    return


@app.cell
def _(div, frag, p, render):
    print(render(frag(div(p('one')), div(p('two')))))

    return


@app.cell
def _():
    return


@app.cell
def _():
    # step 13
    import re
    from urllib.parse import quote as _q

    URL_ATTRS = set('href src action formaction poster cite data manifest'.split())
    JS_ATTR_RE = re.compile(r'^on[a-z]+$')

    def esc_body(s): return escape(s, quote=False)
    def esc_attr(s): return escape(str(s), quote=True)
    def esc_url(s):
        s = str(s)
        if re.match(r'^\s*javascript:', s, re.I): return '#'
        return _q(s, safe=":/?#[]@!$&'()*+,;=%-._~")
    def esc_js(s): return str(s).replace('\\','\\\\').replace('</','<\\/').replace("'","\\'").replace('"','\\"').replace('\n','\\n')
    def esc_css(s): return str(s).replace('</','<\\/').replace('\\','\\\\')



    def raw_ctx(tag_name):
        if tag_name == 'script': return esc_js
        if tag_name == 'style': return esc_css
        return lambda s: s

    def attr_ctx(tag_name, attr_name):
        if attr_name in URL_ATTRS: return esc_url
        if JS_ATTR_RE.match(attr_name): return esc_js
        return str



    return attr_ctx, esc_body, raw_ctx


@app.cell
def _(attr_ctx, esc_body, raw_ctx):
    # Re-done on step 13
    # step 13

    def _attrs_str(name, d):
        out = []
        for k, v in d.items():
            if v is True:                 out.append(f' {k}')
            elif v is False or v is None: continue           # identity check, not equality
            else:                         out.append(f' {k}="{escape(attr_ctx(name,k)(v), quote=True)}"')
        return ''.join(out)

    def fmt(events, indent=2):
        out, d, stack = [], 0, []
        def emit(x): (stack[-1][3] if stack else out).append(x)
        for e in events:
            if e[0]=='open': stack.append([e[1],e[2],e[3],[]]); d += 1
            elif e[0]=='close':
                d -= 1
                _,name,m = e
                _,a,_,buf = stack.pop()
                p, ip, atts = ' '*indent*d, ' '*indent*(d+1), _attrs_str(name, a)
                if m in ('preserve','raw'):
                    esc = raw_ctx(name) if m=='raw' else (lambda s: s)
                    emit(('block', f'{p}<{name}{atts}>{"".join(esc(s) for _,s in buf)}</{name}>'))
                elif all(k in ('txt','inline') for k,_ in buf):
                    inner = ''.join(s for _,s in buf)
                    emit(('inline', f'<{name}{atts}>{inner}</{name}>') if m=='inline' else ('block', f'{p}<{name}{atts}>{inner}</{name}>'))
                else:
                    inner = '\n'.join(f'{ip}{s}' if k in ('inline','txt') else s for k,s in buf)
                    emit(('block', f'{p}<{name}{atts}>\n{inner}\n{p}</{name}>'))
            elif e[0]=='void': emit(('block', f'{" "*indent*d}<{e[1]}{_attrs_str(e[1], e[2])}>'))
            elif e[0]=='txt':
                top = stack[-1] if stack else None
                if top and top[2] in ('preserve','raw'): top[3].append(('txt', e[1]))
                else: emit(('txt', esc_body(e[1])))
            elif e[0]=='raw': emit(('txt', e[1]))
        return '\n'.join(s for _,s in out)

    return (fmt,)


@app.cell
def _(mk_tag):
    # step 8
    def __getattr__(name):
        if name.startswith('_'): raise AttributeError(name)
        t = mk_tag(name)
        globals()[name] = t
        return t


    return


@app.cell
def _(Raw, mk_tag, render):
    html_,head,body,header,nav,main,aside,footer,title = [mk_tag(n) for n in 'html head body header nav main aside footer title'.split()]
    h1 = mk_tag("h1")

    def html_doc(head_, body_, lang='en'): return Raw(f'<!DOCTYPE html>\n{render(html_(lang=lang)(head_, body_))}')

    def Layout(main_, *, header_=None, nav_=None, aside_=None, footer_=None):
        return body(cls='surface')(
            header_ and header(id='header', cls='split')(header_),
            nav_    and nav(id='nav')(nav_),
            main(id='main', cls='surface')(main_),
            aside_  and aside(id='aside')(aside_),
            footer_ and footer(id='footer', cls='split')(footer_))

    return Layout, body, h1, head, html_doc, title


@app.cell
def _(Layout, div, h1, head, html_doc, p, title):
    doc = html_doc(head(title('test')), Layout(div(p('hi')), header_=h1('My Site'), footer_=p('© 2026')))
    print(doc.s)
    return


@app.cell
def _(El, Frag, Txt, fmt, walk):
    def html_to_tag(s):
        "Parse HTML into an `El`/`Frag` tree (tag names lowercased per HTML5)."
        stack, opens, voids = [[]], [], HTML5['void']
        class P(HTMLParser):
            def handle_starttag(s_, t, a):
                d = {k:(v if v is not None else True) for k,v in a}
                if t in voids: stack[-1].append(El(t, d, ()))
                else: stack.append([]); opens.append((t, d))
            def handle_startendtag(s_, t, a):
                d = {k:(v if v is not None else True) for k,v in a}
                stack[-1].append(El(t, d, ()))
            def handle_endtag(s_, t):
                if t in voids: return
                kids, (name, d) = tuple(stack.pop()), opens.pop()
                stack[-1].append(El(name, d, kids))
            def handle_data(s_, data):
                if data.strip(): stack[-1].append(Txt(data.strip()))
        P().feed(s)
        r = stack[0]
        return r[0] if len(r)==1 else Frag(r)

    def internal_et(e):
        name = e.tag.split('}')[-1] if '}' in e.tag else e.tag
        kids = []
        if e.text and e.text.strip(): kids.append(Txt(e.text))
        for c in e:
            kids.append(internal_et(c))
            if c.tail and c.tail.strip(): kids.append(Txt(c.tail))
        return El(name, dict(e.attrib), tuple(kids))

    def xml_to_tag(s):
        "Parse XML into an `El` tree, preserving case (use this for SVG/MathML)."
        return internal_et(ET.fromstring(s))


    def render(node, prof=HTML5, indent=2): return fmt(walk(node,prof), indent)

    return html_to_tag, render, xml_to_tag


@app.cell
def _(html_to_tag, render, xml_to_tag):
    print(render(html_to_tag('<p>x</p><p>y</p>')))
    print('---')
    print(render(xml_to_tag('<svg viewBox="0 0 10 10"><linearGradient id="g"/></svg>')))
    return


@app.cell
def _(html_to_tag, render, xml_to_tag):
    print(render(html_to_tag('<p>x</p><p>y</p>')))
    print('---')
    print(render(xml_to_tag('<svg viewBox="0 0 10 10"><linearGradient id="g"/></svg>')))
    return


@app.cell
def _(mk_tag):
    # step 12
    from urllib.parse import quote
    script,link = mk_tag('script'),mk_tag('link')

    def Datastar(v='latest'):
        "Datastar client library."
        ref = 'main' if v=='latest' else v
        return script(type='module', src=f'https://cdn.jsdelivr.net/gh/starfederation/datastar@{ref}/bundles/datastar.js')

    def MeCSS(v='latest'):
        "me_css.js helper for scoped <style> blocks."
        return script(src=f'https://cdn.jsdelivr.net/gh/Deufel/toolbox@{v}/js/me_css.js')

    def Pointer(v='latest'):
        "pointer_events.js for .hover/.active/.disabled on .btn."
        return script(src=f'https://cdn.jsdelivr.net/gh/Deufel/toolbox@{v}/js/pointer_events.js')

    def Highlight(v='latest'):
        "highlight.js syntax highlighter."
        return script(type='module', src=f'https://cdn.jsdelivr.net/gh/Deufel/toolbox@{v}/js/highlight.js')

    def Color_type_css(v='latest'):
        "Toolbox core stylesheet."
        return link(rel='stylesheet', href=f'https://cdn.jsdelivr.net/gh/Deufel/toolbox@{v}/css/style.css')

    def Favicon(emoji):
        "Favicon from inline SVG data URI."
        s = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">{emoji}</text></svg>'
        return link(rel='icon', href=f'data:image/svg+xml,{quote(s, safe=":/@!,")}')

    return Color_type_css, Datastar, Favicon, Highlight, MeCSS, Pointer


@app.cell
def _(
    Color_type_css,
    Datastar,
    Favicon,
    Highlight,
    MeCSS,
    Pointer,
    head,
    render,
    title,
):
    print(render(head(title('demo'), Favicon('🧪'), Color_type_css(), MeCSS(), Pointer(), Highlight(), Datastar())))
    return


@app.cell
def _(
    Color_type_css,
    Datastar,
    Favicon,
    Highlight,
    MeCSS,
    Pointer,
    body,
    head,
    html_doc,
    mk_tag,
    render,
    title,
):
    iframe = mk_tag('iframe')

    class Show:
        "Render content in an iframe for notebook display."
        def __init__(self, content): self.content = content
        def _repr_html_(self):
            doc = html_doc(
                head(title('test'), Favicon('🧪'), Color_type_css(), MeCSS(), Pointer(), Highlight(), Datastar()),
                body(self.content))
            return render(iframe(srcdoc=doc.s, style='width:stretch;height:stretch;border:0'))

    return (Show,)


@app.cell
def _(Show, div, h1, p):
    Show(div(h1('Welcome'), p('hello world', style="--contrast:.5")))
    return


@app.cell
def _(div, mk_tag, p, render):
    # step 13 test; 
    a = mk_tag('a')
    style,onclick = 'color:red;</style><script>x</script>', "alert('hi')"
    print(render(div(
        a(href="javascript:alert(1)")('xss attempt'),
        a(href='/safe?q=hello world&x=1')('ok link'),
        p(style=style)('styled'),
        p(onclick=onclick)('click'))))
    return (a,)


@app.function
# step 14

def check(name, got, want): print(f'{"OK" if got==want else "FAIL"} {name}'); print(got) if got!=want else None


@app.cell
def _(mk_tag):
    pre = mk_tag("pre")
    b = mk_tag("b")
    return b, pre


@app.cell
def _(a, b, div, frag, h1, html_to_tag, mk_tag, p, pre, render, xml_to_tag):
    check('fragment',
        render(frag(h1('a'), h1('b'))),
        '<h1>a</h1>\n<h1>b</h1>')

    check('multi-root parse',
        render(html_to_tag('<p>x</p><p>y</p>')),
        '<p>x</p>\n<p>y</p>')

    check('text-only collapses',
        render(p('hello')),
        '<p>hello</p>')

    check('pre preserves',
        render(pre('line1\nline2')),
        '<pre>line1\nline2</pre>')

    check('inline mixing',
        render(p('a ', b('bold'), ' c')),
        '<p>a <b>bold</b> c</p>')

    check('svg case preserved',
        render(xml_to_tag('<svg><linearGradient id="g"/></svg>')),
        '<svg xmlns="http://www.w3.org/2000/svg">\n  <linearGradient id="g"></linearGradient>\n</svg>')

    check('void no close',
        render(div(mk_tag('br')())),
        '<div>\n  <br>\n</div>')

    check('javascript: neutralized',
        render(a(href='javascript:alert(1)')('x')),
        '<a href="#">x</a>')

    check('url & escaped',
        render(a(href='/q?a=1&b=2')('x')),
        '<a href="/q?a=1&amp;b=2">x</a>')

    check('style attr escaped',
        render(p(style='</style><x>')('y')),
        '<p style="&lt;/style&gt;&lt;x&gt;">y</p>')

    check('cls -> class',
        render(div(cls='card')),
        '<div class="card"></div>')

    check('None/False dropped',
        render(div(p('a'), None, False, p('b'))),
        '<div>\n  <p>a</p>\n  <p>b</p>\n</div>')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Datastar integration
    """)
    return


@app.cell
def _(div, render):
    print(render(div({'data-on:click':"@get('/x')"})("hi")))
    return


@app.cell
def _():
    def _mods(kw): return ''.join(f'__{k}'+('.'+'.'.join(v.split()) if isinstance(v,str) and v else '') for k,v in kw.items())
    def _obj(d): return '{'+', '.join(f"'{k}': {v}" for k,v in d.items())+'}'

    def data_on(event, expr, **mods): return {f'data-on:{event}{_mods(mods)}': expr}
    def data_bind(name): return {f'data-bind:{name}': True}
    def data_text(expr): return {'data-text': expr}
    def data_show(expr): return {'data-show': expr}
    def data_init(expr, **mods): return {f'data-init{_mods(mods)}': expr}
    def data_effect(expr): return {'data-effect': expr}
    def data_ref(name): return {f'data-ref:{name}': True}
    def data_indicator(name): return {f'data-indicator:{name}': True}
    def data_computed(name, expr): return {f'data-computed:{name}': expr}
    def data_attr(name, expr): return {f'data-attr:{name}': expr}
    def data_style(name, expr): return {f'data-style:{name}': expr}
    def data_class(spec): return {'data-class': spec if isinstance(spec,str) else _obj(spec)}
    def data_signals(**kw): return {'data-signals': _obj(kw)}
    def data_signal(name, val, **mods): return {f'data-signals:{name}{_mods(mods)}': val}

    return data_bind, data_on, data_signals, data_text


@app.cell
def _(data_bind, data_on, data_signals, data_text, div, mk_tag, render):
    button = mk_tag("button")
    print(render(div(data_signals(count=0, name="''"))(
        button(data_on('click', "@get('/x')", debounce='500ms leading'))("Go"),
        input_ := mk_tag('input'), input_(data_bind('name')),
        div(data_text('$count')))))
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
