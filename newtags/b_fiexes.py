import marimo

__generated_with = "0.22.0"
app = marimo.App()


@app.cell
def _():
    """Patched version of the lib with bugs 1-3 fixed."""
    from html import escape
    from dataclasses import dataclass, field
    from html.parser import HTMLParser
    import xml.etree.ElementTree as ET
    import re
    from urllib.parse import quote as _q

    MERGE_ATTRS = {'class': ' ', 'style': '; '}

    HTML5 = dict(
        void=set('area base br col embed hr img input link meta source track wbr'.split()),
        raw=set('script style'.split()),
        ns_switch=dict(svg='svg', math='math', foreignObject='html'),
        ns_attrs=dict(svg='http://www.w3.org/2000/svg', math='http://www.w3.org/1998/Math/MathML'))
    HTML5['inline'] = set('a b code em i span strong'.split())
    HTML5['preserve'] = set('pre textarea'.split())

    class Frag(tuple): pass
    @dataclass
    class Txt: s:str
    @dataclass
    class Raw: s:str
    @dataclass
    class El:
        name:str
        attrs:dict=field(default_factory=dict)
        kids:tuple=()

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

    def _merge(old, new):
        "Combine attr dicts. `class`/`style` concatenate; others overwrite. None/False/'' on the right means 'no opinion'."
        out = dict(old)
        for k, v in new.items():
            if v is None or v is False or v == '': continue
            if k in MERGE_ATTRS and out.get(k): out[k] = f'{out[k]}{MERGE_ATTRS[k]}{v}'
            else:                                out[k] = v
        return out
    
    def _attrs_from(c, kw):
        d = {}
        rest = []
        for o in c:
            if isinstance(o, dict): d = _merge(d, o)
            else:                   rest.append(o)
        return _merge(d, _attrs(kw)), rest

    def tag(name, *c, **kw):
        d, c = _attrs_from(c, kw)
        if name in HTML5['void'] and c:
            raise ValueError(f'<{name}> is a void element and cannot have children: got {len(c)}')
        return El(name, d, _kids(c))

    def _call(self, *c, **kw):
        d, c = _attrs_from(c, kw)
        if self.name in HTML5['void'] and c:
            raise ValueError(f'<{self.name}> is a void element and cannot have children: got {len(c)}')
        return El(self.name, _merge(self.attrs, d), self.kids + _kids(c))
    El.__call__ = _call

    def frag(*c): return Frag(_kids(c))
    def mk_tag(name): n=name.rstrip('_').replace('_','-'); return lambda *c,**kw: tag(n,*c,**kw)

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

    # FIX 2: complete URL_ATTRS set
    URL_ATTRS = set('href src action formaction poster cite data manifest ping background longdesc icon usemap srcset'.split())
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

    # FIX 1: identity check, not equality, for bool/None drop.
    # 0 == False in Python so `0 in (False, None)` is True and dropped values silently disappear.
    def _attrs_str(name, d):
        out = []
        for k, v in d.items():
            if v is True:                  out.append(f' {k}')
            elif v is False or v is None:  continue
            else:                          out.append(f' {k}="{escape(attr_ctx(name,k)(v), quote=True)}"')
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

    def render(node, prof=HTML5, indent=2): return fmt(walk(node,prof), indent)

    return mk_tag, render


@app.cell
def _(mk_tag, render):
    """Verify the three fixes against the same scenarios that exposed them,
    plus the surrounding behaviour, so we know nothing else regressed."""

    div, p, input_, td, a, img, br = [mk_tag(n) for n in 'div p input td a img br'.split()]

    def check(name, got, want):
        ok = got == want
        print(f'{"PASS" if ok else "FAIL"} {name}')
        if not ok:
            print(f'   got:  {got!r}')
            print(f'   want: {want!r}')
        return ok

    print('═══ FIX 1: integer 0 attrs no longer drop ═══')
    check('tabindex=0',   render(input_(tabindex=0)),    '<input tabindex="0">')
    check('tabindex=1',   render(input_(tabindex=1)),    '<input tabindex="1">')
    check('tabindex=-1',  render(input_(tabindex=-1)),   '<input tabindex="-1">')
    check('rowspan=0',    render(td(rowspan=0)),         '<td rowspan="0"></td>')
    check('value=0',      render(input_(value=0)),       '<input value="0">')
    check('value=""',     render(input_(value='')),      '<input value="">')
    # guard: True/False/None still behave correctly
    check('disabled=True',  render(input_(disabled=True)),  '<input disabled>')
    check('disabled=False', render(input_(disabled=False)), '<input>')
    check('disabled=None',  render(input_(disabled=None)),  '<input>')
    # 1.0 == True trap — same shape as the 0/False bug
    check('opacity=1.0',  render(div(style='x', data_o=1.0)), '<div style="x" data-o="1.0"></div>')

    print('\n═══ FIX 2: URL_ATTRS now covers ping & srcset ═══')
    check('ping js: blocked',
          render(a(ping='javascript:alert(1)')('x')),
          '<a ping="#">x</a>')
    check('srcset js: blocked',
          render(img(srcset='javascript:alert(1)')),
          '<img srcset="#">')
    check('ping ok url passes',
          render(a(ping='/track')('x')),
          '<a ping="/track">x</a>')
    # guard: regular href still works
    check('href js: blocked',
          render(a(href='javascript:alert(1)')('x')),
          '<a href="#">x</a>')
    check('href ok url',
          render(a(href='/safe?q=1&r=2')('x')),
          '<a href="/safe?q=1&amp;r=2">x</a>')

    print('\n═══ FIX 3: void element with kids raises clearly ═══')
    def expect_raise(name, fn):
        try:
            out = fn()
            print(f'FAIL {name}: should have raised, got {out!r}')
        except ValueError as e:
            print(f'PASS {name}: ValueError("{e}")')
        except Exception as e:
            print(f'FAIL {name}: wrong exception {type(e).__name__}: {e}')

    expect_raise('br with text kid',   lambda: br('inside'))
    expect_raise('img with kid',       lambda: img('alt-text'))
    expect_raise('br via tag()',       lambda: __import__('fixed_lib').tag('br', 'kid'))
    expect_raise('br extended',        lambda: br()(p('after')))   # __call__ path
    # guard: void with attrs still works
    check('br no kids',               render(br()),                     '<br>')
    check('img with attrs only',      render(img(src='/x.png', alt='x')), '<img src="/x.png" alt="x">')
    check('br with attrs',            render(br(cls='spacer')),         '<br class="spacer">')

    print('\n═══ FULL REGRESSION: every original case still passes ═══')
    # Replay the OK cases from stress.py to confirm no regression
    span, b, pre, button, ul, li, svg, circle = [
        mk_tag(n) for n in 'span b pre button ul li svg circle'.split()]

    cases = [
        ('empty div',       render(div()),                          '<div></div>'),
        ('text',            render(div('hello')),                   '<div>hello</div>'),
        ('cls→class',       render(div(cls='foo')),                 '<div class="foo"></div>'),
        ('xss text',        render(div('<script>x</script>')),
            '<div>&lt;script&gt;x&lt;/script&gt;</div>'),
        ('inline mix',      render(p('a ', b('bold'), ' c')),       '<p>a <b>bold</b> c</p>'),
        ('pre preserves',   render(pre('l1\nl2')),                  '<pre>l1\nl2</pre>'),
        ('block of inlines', render(div(b('1'), span('2'))),        '<div><b>1</b><span>2</span></div>'),
        ('zero text child', render(div(0)),                         '<div>0</div>'),
        ('none drops',      render(div(p('a'), None, p('b'))),
            '<div>\n  <p>a</p>\n  <p>b</p>\n</div>'),
        ('svg ns',          render(svg(viewBox='0 0 1 1')(circle(r=1))),
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1">\n  <circle r="1"></circle>\n</svg>'),
    ]
    for name, got, want in cases:
        check(name, got, want)
    return (div,)


@app.cell
def _(div):
    div(cls='a')(cls='b')
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
