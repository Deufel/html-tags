import marimo

__generated_with = "0.20.4"
app = marimo.App(width="columns")

with app.setup:
    import types, re
    from collections import namedtuple
    from html import escape

    VOID_TAGS = frozenset({"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"})
    RAW_TAGS = frozenset({"script", "style"})
    RAW_CLOSE_RE = re.compile(r'</(script|style)[\s/>]', re.IGNORECASE)

    # class Tag(namedtuple('Tag', 'tag children attrs', defaults=((), {}))):
    #     def __str__(self): return globals()['to_html'](self)
    #     def __html__(self): return globals()['to_html'](self)
    #     def _repr_html_(self): return globals()['to_html'](self)

    # class Tag(namedtuple('Tag', 'tag children attrs', defaults=((), {}))):
    #     def __str__(self): return globals()['to_html'](self)
    #     __html__ = _repr_html_ = __str__
    #     def __call__(self, *c, **kw):
    #         children = tuple(flatten(c))
    #         attrs = {**self.attrs, **kw}
    #         return Tag(self.tag, self.children + children, attrs)

    class Tag(namedtuple('Tag', 'tag children attrs', defaults=((), {}))):
        def __str__(self): return globals()['to_html'](self)
        __html__ = _repr_html_ = __str__
        def __call__(self, *c, **kw):
            return Tag(self.tag, self.children + tuple(globals()['flatten'](c)), {**self.attrs, **kw})




    attr_map = dict(cls='class', klass='class', _class='class', _for='for', fr='for')




@app.function
def attrmap(k): return attr_map.get(k, k.lstrip('_').replace('_', '-'))


@app.function
# def render_attrs(d):
#     parts = []
#     for k,v in d.items():
#         k = attrmap(k)
#         if v is True: parts.append(f' {k}')
#         elif v not in (False, None): parts.append(f' {k}="{v}"')
#     return ''.join(parts)

def render_attrs(d):
    out = ''
    for k,v in d.items():
        k = attrmap(k)
        if v is True: out += f' {k}'
        elif v not in (False, None): out += f' {k}="{v}"'
    return out


@app.function
def is_void(t): return t.tag in VOID_TAGS


@app.function
def is_raw(t): return t.tag in RAW_TAGS


@app.function
# def to_html(t, raw=False):
#     if isinstance(t, str): return t.replace('\x00', '') if raw else escape(t.replace('\x00', ''))
#     if not hasattr(t, 'tag'): return escape(str(t).replace('\x00', ''))
#     attrs = render_attrs(t.attrs)
#     if is_raw(t):
#         inner = ''.join(str(c).replace('\x00', '') for c in t.children)
#         validate_raw(t.tag, inner)
#     else:
#         inner = ''.join(to_html(c, raw=False) for c in t.children)
#     if not t.tag: return inner
#     if is_void(t): return f'<{t.tag}{attrs}>'
#     return f'<{t.tag}{attrs}>{inner}</{t.tag}>'



def to_html(t, raw=False):
    if isinstance(t, str): return escape(t)
    if not hasattr(t, 'tag'): return escape(str(t))
    attrs = render_attrs(t.attrs) if t.attrs else ''
    if is_raw(t):
        inner = ''.join(str(c) for c in t.children)
        validate_raw(t.tag, inner)
    elif len(t.children) == 1: inner = to_html(t.children[0])
    else: inner = ''.join(to_html(c) for c in t.children)
    if not t.tag: return inner
    if is_void(t): return f'<{t.tag}{attrs}>'
    return f'<{t.tag}{attrs}>{inner}</{t.tag}>'


@app.function
def mktag(name):
    def f(*c, **kw): return tag(name, *c, **kw)
    f.__name__ = name.capitalize()
    return f


@app.class_definition
class TagNS:
    def __getattr__(self, name): return mktag(name.lower())
    def export(self, *names): return [getattr(self, n) for n in names]


@app.function
def Fragment(*c, **kw): return tag('', *c, **kw)


@app.function
def flatten(c):
    for o in c:
        if o is None or o is False: continue
        if hasattr(o, 'tag'): yield o
        elif isinstance(o, (list, tuple, map, filter, types.GeneratorType)): yield from flatten(o)
        else: yield o


@app.function
def tag(name, *c, **kw):
    children = tuple(flatten(o for o in c if not isinstance(o, dict)))
    attrs = {k:v for o in c if isinstance(o, dict) for k,v in o.items()}
    return Tag(name, children, {**attrs, **kw})


@app.function
def validate_raw(tag, text):
    if RAW_CLOSE_RE.search(text): raise ValueError(f'Raw text in <{tag}> must not contain closing tag pattern: {text!r}')


@app.cell
def _():
    return


@app.cell
def _():
    t = TagNS()
    Div,B,Span,Img,A,P,H1,Ul,Li,Script,Br,Input,Form,Label,Button,Hr = t.export(
        'Div','B','Span','Img','A','P','H1','Ul','Li','Script','Br','Input','Form','Label','Button', 'Hr')

    show_link = False
    Div(
        P('hi', show_link and A('click', href='/')),
        Ul([Li(f'Item {i}') for i in range(3)]),
        Div('count: ', 42, None, False),
        Div(H1('hello'), P('This is ', B('bold')), cls='test'),
        Script('let x = 1 < 2;'),
        Br(),
        Fragment(P('one'), P('two')),
    )
    return A, B, Br, Div, H1, Hr, Img, Li, P, Script, Span, Ul, t


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Testing
    """)
    return


@app.cell
def _():
    import pytest

    return (pytest,)


@app.cell
def _(A, B, Br, Div, Img, Li, P, Script, Span, Ul, pytest, t):
    def test_basic_tag(): assert to_html(Div('hello')) == '<div>hello</div>'

    def test_nested_tags(): assert to_html(Div(P('inner'))) == '<div><p>inner</p></div>'

    def test_deeply_nested(): assert to_html(Div(Ul(Li(B('deep'))))) == '<div><ul><li><b>deep</b></li></ul></div>'

    def test_multiple_children(): assert to_html(Div('a', 'b', 'c')) == '<div>abc</div>'

    def test_attrs_cls(): assert to_html(Div('hi', cls='box')) == '<div class="box">hi</div>'

    def test_attrs_multiple(): assert to_html(Div('hi', cls='box', id='main')) == '<div class="box" id="main">hi</div>'

    def test_attrs_boolean_true(): assert to_html(t.Input(type='text', disabled=True)) == '<input type="text" disabled>'

    def test_attrs_boolean_false(): assert 'disabled' not in to_html(t.Input(type='text', disabled=False))

    def test_attrs_none_skipped(): assert 'title' not in to_html(Div('hi', title=None))

    def test_attrs_underscore_to_hyphen(): assert to_html(Div('hi', data_value='5')) == '<div data-value="5">hi</div>'

    def test_attrs_for(): assert to_html(t.Label('Name', _for='name')) == '<label for="name">Name</label>'

    def test_void_br(): assert to_html(Br()) == '<br>'

    def test_void_img(): assert to_html(Img(src='cat.jpg', alt='cat')) == '<img src="cat.jpg" alt="cat">'

    def test_void_no_children(): assert to_html(Br()) == '<br>'

    def test_escape_text(): assert to_html(Div('<script>alert("xss")</script>')) == '<div>&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;</div>'

    def test_escape_ampersand(): assert to_html(P('a & b')) == '<p>a &amp; b</p>'

    def test_raw_script(): assert to_html(Script('let x = 1 < 2;')) == '<script>let x = 1 < 2;</script>'

    def test_raw_style(): assert to_html(t.Style('body { color: red; }')) == '<style>body { color: red; }</style>'

    def test_none_filtered(): assert to_html(Div('a', None, 'b')) == '<div>ab</div>'

    def test_false_filtered(): assert to_html(Div('a', False, 'b')) == '<div>ab</div>'

    def test_conditional_rendering():
        show = False
        assert to_html(P('hi', show and A('link'))) == '<p>hi</p>'

    def test_conditional_rendering_true():
        show = True
        assert to_html(P('hi ', show and A('link', href='/'))) == '<p>hi <a href="/">link</a></p>'

    def test_list_flattening(): assert to_html(Ul([Li('a'), Li('b')])) == '<ul><li>a</li><li>b</li></ul>'

    def test_nested_list_flattening(): assert to_html(Div([[P('a')], [P('b')]])) == '<div><p>a</p><p>b</p></div>'

    def test_generator_children(): assert to_html(Ul(Li(str(i)) for i in range(3))) == '<ul><li>0</li><li>1</li><li>2</li></ul>'

    def test_int_child(): assert to_html(Div('count: ', 42)) == '<div>count: 42</div>'

    def test_float_child(): assert to_html(Span(3.14)) == '<span>3.14</span>'

    def test_fragment(): assert to_html(Fragment(P('a'), P('b'))) == '<p>a</p><p>b</p>'

    def test_fragment_empty(): assert to_html(Fragment()) == ''

    def test_str_method(): assert str(Div('hello')) == '<div>hello</div>'

    def test_html_method(): assert Div('hello').__html__() == '<div>hello</div>'

    def test_tagns_any_tag(): assert to_html(t.Article(t.Section('hi'))) == '<article><section>hi</section></article>'

    def test_empty_tag(): assert to_html(Div()) == '<div></div>'

    def test_mixed_children(): assert to_html(Div('text', B('bold'), ' more')) == '<div>text<b>bold</b> more</div>'

    def test_null_byte_stripped_raw(): assert to_html(Script('alert\x00("hi")')) == '<script>alert("hi")</script>'

    def test_null_byte_stripped_raw_style(): assert to_html(t.Style('body\x00 { color: red; }')) == '<style>body { color: red; }</style>'

    def test_null_byte_escaped_normal(): assert to_html(Div('hello\x00world')) == '<div>helloworld</div>'

    def test_raw_str_not_escaped(): assert to_html(Script('1 < 2 && 3 > 1')) == '<script>1 < 2 && 3 > 1</script>'

    def test_raw_validates_script():
        with pytest.raises(ValueError): to_html(Script('</script>'))

    def test_raw_validates_style():
        with pytest.raises(ValueError): to_html(t.Style('</style >'))

    def test_raw_validates_case_insensitive():
        with pytest.raises(ValueError): to_html(Script('</SCRIPT>'))

    def test_non_tag_escaped(): assert to_html(Div(42)) == '<div>42</div>'

    def test_fragment_renders_inner_only(): assert to_html(Fragment(Div('a'), Div('b'))) == '<div>a</div><div>b</div>'

    def test_void_no_closing(): assert to_html(Br()) == '<br>'

    def test_void_with_attrs(): assert to_html(Img(src='x.png')) == '<img src="x.png">'

    def test_empty_string_child(): assert to_html(Div('')) == '<div></div>'



    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Playground
    """)
    return


@app.cell
def _(Div, Img, P, t):
    card = lambda title,text,img: Div(
        Img(src=img, alt=title, style='width:100%;border-radius:8px'),
        t.H3(title), P(text),
        style='border:1px solid #ddd;padding:16px;border-radius:12px;width:200px;display:inline-block;margin:8px')

    Div(
        card('Mountains', 'Beautiful peaks', 'https://picsum.photos/200/120?1'),
        card('Ocean', 'Calm waters', 'https://picsum.photos/200/120?2'),
        card('Forest', 'Tall trees', 'https://picsum.photos/200/120?3'))

    return


@app.cell
def _(Div, t):
    Div(
        t.Table(
            t.Thead(t.Tr(t.Th('Name'), t.Th('Role'), t.Th('Status'))),
            t.Tbody(*[t.Tr(t.Td(n), t.Td(r), t.Td(s)) for n,r,s in [
                ('Alice', 'Engineer', '✅'), ('Bob', 'Designer', '🔄'), ('Carol', 'Manager', '✅')]])),
        t.Style('table{border-collapse:collapse}th,td{border:1px solid #ccc;padding:8px}th{background:#f0f0f0}'))
    return


@app.cell(hide_code=True)
def _():
    SCOPE_JS = '''window.cssScopeCount??=1;window.cssScope??=new MutationObserver(m=>{document?.body?.querySelectorAll('style:not([ready])').forEach(n=>{var s='me__'+(window.cssScopeCount++);n.parentNode.classList.add(s);n.textContent=n.textContent.replace(/(?:^|\\.|(\s|[^a-zA-Z0-9\\-\\_]))(me|this|self)(?![a-zA-Z])/g,'$1.'+s).replace(/((@keyframes|animation:|animation-name:)[^{};]*)\\.me__/g,'$1me__').replace(/(?:@media)\s(xs-|sm-|md-|lg-|xl-|sm|md|lg|xl|xx)/g,(m,p)=>'@media '+({'sm':'(min-width:640px)','md':'(min-width:768px)','lg':'(min-width:1024px)','xl':'(min-width:1280px)','xx':'(min-width:1536px)','xs-':'(max-width:639px)','sm-':'(max-width:767px)','md-':'(max-width:1023px)','lg-':'(max-width:1279px)','xl-':'(max-width:1535px)'}[p]));n.setAttribute('ready','')})}).observe(document.documentElement,{childList:true,subtree:true})'''
    return (SCOPE_JS,)


@app.cell(hide_code=True)
def _():
    UI_CSS = """/* ================================================================
       _ui-v4.css — color · type · layout · components
       ================================================================ */

    @layer reset, props, theme, color, typography, composition, layout, components, overrides;


    /* ── properties (unlayered — must precede all layers) ──────────── */

    @property --_color         { syntax: "<color>";   inherits: true; initial-value: oklch(50% 0.2 270); }
    @property --_surface-level { syntax: "<integer>"; inherits: true; initial-value: 0; }
    @property --_dark          { syntax: "<integer>"; inherits: true; initial-value: 0; }
    @property --_type          { syntax: "<number>";  inherits: false; initial-value: -999; }
    @property --_surface       { syntax: "<integer>"; inherits: false; initial-value: -999; }

    @property --_motion        { syntax: "<integer>"; inherits: true; initial-value: 1; }
    @property --_bg            { syntax: "<color>";   inherits: true; initial-value: oklch(100% 0 0); }
    @property --_type-scale    { syntax: "<number>";  inherits: true; initial-value: 1; }
    @property --_space-scale   { syntax: "<number>";  inherits: true; initial-value: 1; }


    @property --_depth-a { syntax: "<integer>"; inherits: true; initial-value: 0; }
    @property --_depth-b { syntax: "<integer>"; inherits: true; initial-value: 0; }
    @property --_parity  { syntax: "<integer>"; inherits: true; initial-value: 0; }

    /* ── functions (unlayered — definitions, not rules) ────────────── */

    @function --surface(--level <number>: 0, --c <color>: var(--_color)) returns <color> {
      --base: calc(95% - var(--_dark) * 75%);
      --step: calc(-2.5% + var(--_dark) * 5.5%);
      --chroma: calc(0.02 + abs(var(--level)) * 0.012);
      result: oklch(from var(--c) clamp(10%, calc(var(--base) + var(--level) * var(--step)), 99%) var(--chroma) h);
    }

    @function --fill(--level: 0, --c: var(--_color)) returns <color> {
      --base: calc(45% + var(--_dark) * 23%);
      --step: calc(-5% + var(--_dark) * 10%);
      result: oklch(from var(--c) calc(var(--base) + var(--level) * var(--step)) c h);
    }

    @function --contrast(--amount <number>: 0.85, --bg <color>: var(--_bg)) returns <color> {
      result: oklch(from var(--bg) calc(l + (clamp(0, calc((0.5 - l) * 999), 1) - l) * var(--amount)) c h);
    }

    @function --alpha(--a <number>: 0.5, --base <color>: var(--_bg)) returns <color> {
      result: oklch(from var(--base) l c h / var(--a));
    }

    @function --shadow(--level: 1, --c: var(--_color)) {
      result: 0 calc(var(--level) * 1px) calc(var(--level) * 3px) calc(var(--level) * 1px) oklch(from var(--c) 30% calc(c * 0.5) h / calc(0.15 + var(--level) * 0.04));
    }

    @function --type(--step: 0) returns <length> {
      --min: calc(var(--_type-min) * pow(var(--_type-min-ratio), var(--step)));
      --max: calc(var(--_type-max) * pow(var(--_type-max-ratio), var(--step)));
      result: calc(clamp(
        var(--min),
        calc(var(--min) + (var(--max) - var(--min)) * (100vi - var(--_fluid-min-vp)) / (var(--_fluid-max-vp) - var(--_fluid-min-vp))),
        var(--max)
      ) * var(--_type-scale));
    }

    @function --space(--step: 0) returns <length> {
      --min: calc(var(--_space-min) * pow(var(--_space-min-ratio), var(--step)));
      --max: calc(var(--_space-max) * pow(var(--_space-max-ratio), var(--step)));
      result: calc(clamp(
        var(--min),
        calc(var(--min) + (var(--max) - var(--min)) * (100vi - var(--_fluid-min-vp)) / (var(--_fluid-max-vp) - var(--_fluid-min-vp))),
        var(--max)
      ) * var(--_space-scale));
    }


    @function --hue(--angle <number>: 180, --c <color>: var(--_color)) returns <color> {
      result: oklch(from var(--c) l c calc(h + var(--angle)));
    }

    @function --mute(--amount <number>: 0.5, --c <color>: var(--_color)) returns <color> {
      result: oklch(from var(--c) l calc(c * (1 - var(--amount))) h);
    }

    @function --vibrant(--amount <number>: 0.5, --c <color>: var(--_color)) returns <color> {
      result: oklch(from var(--c) l calc(c + (0.4 - c) * var(--amount)) h);
    }

    /* ── reset ─────────────────────────────────────────────────────── */

    @layer reset {
      *, *::before, *::after { box-sizing: border-box; margin: 0; background-repeat: no-repeat; }
      :root { interpolate-size: allow-keywords; }
      html { color-scheme: light dark; line-height: 1.5; -moz-text-size-adjust: none; -webkit-text-size-adjust: none; text-size-adjust: none; }
      :where(body, figure, blockquote, dl, dd, p) { margin-block-end: 0; }
      :where(img, picture) { max-width: 100%; display: block; }
      :where(table, thead, tbody, tfoot, tr) { isolation: isolate; }
      :where(input, button, textarea, select) { font: inherit; }
    }


    /* ── props ─────────────────────────────────────────────────────── */

    @layer props {
      :root {
        --font-system-ui: system-ui, sans-serif;
        --font-transitional: Charter, Bitstream Charter, Sitka Text, Cambria, serif;
        --font-old-style: Iowan Old Style, Palatino Linotype, URW Palladio L, P052, serif;
        --font-humanist: Seravek, Gill Sans Nova, Ubuntu, Calibri, DejaVu Sans, source-sans-pro, sans-serif;
        --font-geometric-humanist: Avenir, Montserrat, Corbel, URW Gothic, source-sans-pro, sans-serif;
        --font-classical-humanist: Optima, Candara, Noto Sans, source-sans-pro, sans-serif;
        --font-neo-grotesque: Inter, Roboto, Helvetica Neue, Arial Nova, Nimbus Sans, Arial, sans-serif;
        --font-monospace-slab-serif: Nimbus Mono PS, Courier New, monospace;
        --font-monospace-code: Dank Mono, Operator Mono, Inconsolata, Fira Mono, ui-monospace, SF Mono, Monaco, Droid Sans Mono, Source Code Pro, Cascadia Code, Menlo, Consolas, DejaVu Sans Mono, monospace;
        --font-industrial: Bahnschrift, DIN Alternate, Franklin Gothic Medium, Nimbus Sans Narrow, sans-serif-condensed, sans-serif;
        --font-rounded-sans: ui-rounded, Hiragino Maru Gothic ProN, Quicksand, Comfortaa, Manjari, Arial Rounded MT, Arial Rounded MT Bold, Calibri, source-sans-pro, sans-serif;
        --font-slab-serif: Rockwell, Rockwell Nova, Roboto Slab, DejaVu Serif, Sitka Small, serif;
        --font-antique: Superclarendon, Bookman Old Style, URW Bookman, URW Bookman L, Georgia Pro, Georgia, serif;
        --font-didone: Didot, Bodoni MT, Noto Serif Display, URW Palladio L, P052, Sylfaen, serif;
        --font-handwritten: Segoe Print, Bradley Hand, Chilanka, TSCu_Comic, casual, cursive;
      }
    }


    /* ── theme ─────────────────────────────────────────────────────── */

    @layer theme {
      :root {
        --_fluid-min-vp:   22.5rem;
        --_fluid-max-vp:   77.5rem;
        --_type-min:       1.125rem;
        --_type-max:       1.25rem;
        --_type-min-ratio: 1.2;
        --_type-max-ratio: 1.25;
        --_space-min:       0.5rem;
        --_space-max:       0.75rem;
        --_space-min-ratio: 1.4;
        --_space-max-ratio: 1.65;
        --_font-heading:   var(--font-system-ui);
        --_font-body:      var(--font-system-ui);
        --_font-mono:      var(--font-monospace-code);
      }
    }


    /* ── color ─────────────────────────────────────────────────────── */

    @layer color {
      :where(*) {
        --_bg: if(not style(--_surface: -999): --surface(var(--_surface)));
        background: if(not style(--_surface: -999): var(--_bg));
      }
      body { --_surface: 0; }
      :root { --_dark: 0; --_motion: 1; }
      @media (prefers-color-scheme: dark) { :root { --_dark: 1; } }
      html[data-ui-scheme="dark"]  { --_dark: 1; }
      html[data-ui-scheme="light"] { --_dark: 0; }
      @media (prefers-reduced-motion: reduce) { :root { --_motion: 0; } }
      html[data-ui-motion="none"] { --_motion: 0; }
      html[data-ui-density="compact"]     { --_space-scale: 0.75; }
      html[data-ui-density="comfortable"] { --_space-scale: 1.25; }
      html[data-ui-size="small"]          { --_type-scale: 0.85; }
      html[data-ui-size="large"]          { --_type-scale: 1.15; }
      @container style(--_parity: 0) { .surface { --_depth-b: calc(var(--_depth-a) + 1); --_surface: var(--_depth-b); --_parity: 1; } }
      @container style(--_parity: 1) { .surface { --_depth-a: calc(var(--_depth-b) + 1); --_surface: var(--_depth-a); --_parity: 0; } }
    }


    /* ── typography ────────────────────────────────────────────────── */

    @layer typography {
      :where(*) {
        font-size: if(not style(--_type: -999): --type(var(--_type)));
        letter-spacing: if(not style(--_type: -999): calc(0.01em - var(--_type) * 0.01em));
        line-height: if(not style(--_type: -999): calc(1.5 - var(--_type) * 0.075));
      }

      body { --_type: 0; font-family: var(--_font-body); color: --contrast(0.9); }
      h1, h2, h3, h4, h5, h6 { font-family: var(--_font-heading); color: --fill(0); }
      h1 { --_type: 5; }
      h2 { --_type: 4; }
      h3 { --_type: 3; }
      h4 { --_type: 2; }
      h5 { --_type: 1; }
      small { --_type: -1; }
      .muted { color: --contrast(0.4); }
      code, pre { font-family: var(--_font-mono); font-size: 0.85em; }
      code { padding: 0.1em 0.4em; border-radius: 0.25rem; }
      a { color: --fill(); } a:hover { color: --fill(1); }
      hr { border: none; height: 1px; background: --alpha(0.15, --fill()); }
    }


    /* ── composition ───────────────────────────────────────────────── */

    @layer composition {
      /* containers */
      .stack { display: flex; flex-direction: column; gap: var(--_gap, .75rem); }
      .row   { display: flex; flex-wrap: wrap; gap: var(--_gap, .5rem); }
      .split { display: flex; flex-wrap: wrap; justify-content: space-between; gap: var(--_gap, .5rem); }
      .grid  { display: grid; grid-template-columns: repeat(auto-fit, minmax(var(--_col, 15rem), 1fr)); gap: var(--_gap, 1rem); }
      .flank { display: flex; flex-wrap: wrap; gap: var(--_gap, 1rem); }
      .flank > :first-child { flex: 1 1 var(--_flank, auto); }
      .flank > :last-child { flex: 999 1 0; }
      .flank-end { display: flex; flex-wrap: wrap; gap: var(--_gap, 1rem); }
      .flank-end > :first-child { flex: 999 1 0; }
      .flank-end > :last-child { flex: 1 1 var(--_flank, auto); }
      /* modifiers */
      .span { grid-column: 1 / -1; }
      .wrap { flex-wrap: wrap; } .nowrap { flex-wrap: nowrap; }
      /* alignment */
      .ai-start { align-items: flex-start; } .ai-center { align-items: center; } .ai-end { align-items: flex-end; } .ai-baseline { align-items: baseline; } .ai-stretch { align-items: stretch; }
      .jc-start { justify-content: flex-start; } .jc-center { justify-content: center; } .jc-end { justify-content: flex-end; } .jc-between { justify-content: space-between; } .jc-around { justify-content: space-around; } .jc-evenly { justify-content: space-evenly; }
      .as-start { align-self: flex-start; } .as-center { align-self: center; } .as-end { align-self: flex-end; } .as-baseline { align-self: baseline; } .as-stretch { align-self: stretch; }
    }


    /* ── layout ────────────────────────────────────────────────────── */

    @layer layout {
      .layout-doc { display: grid; grid-template-columns: var(--_sidebar, 16rem) 1fr; grid-template-rows: auto 1fr; grid-template-areas: "nav nav" "sidebar main"; min-height: 100dvh; }
      .layout-doc .layout-nav { grid-area: nav; }
      .layout-doc .layout-sidebar { display: block; grid-area: sidebar; --_bg: --surface(-1); background: var(--_bg); padding: --space(1); overflow-y: auto; position: sticky; top: 0; height: 100dvh; border: none; max-height: none; max-width: none; }
      .layout-doc .layout-sidebar::backdrop { display: none; }
      .layout-doc .layout-main { grid-area: main; padding: --space(2); max-width: 72ch; }
      .layout-doc .layout-toc { display: none; }

      .layout-app { display: grid; grid-template-columns: var(--_sidebar, 16rem) 1fr; grid-template-rows: 1fr; grid-template-areas: "sidebar main"; min-height: 100dvh; }
      .layout-app .layout-sidebar { display: block; grid-area: sidebar; --_bg: --surface(-1); background: var(--_bg); padding: --space(1); overflow-y: auto; position: sticky; top: 0; height: 100dvh; border: none; max-height: none; max-width: none; }
      .layout-app .layout-sidebar::backdrop { display: none; }
      .layout-app .layout-main { grid-area: main; padding: --space(2); }

      .layout-stack { display: grid; grid-template-columns: 1fr; grid-template-rows: auto 1fr auto; grid-template-areas: "header" "main" "footer"; min-height: 100dvh; }
      .layout-stack .layout-header { grid-area: header; }
      .layout-stack .layout-main { grid-area: main; padding: --space(2); max-width: 72ch; margin-inline: auto; width: 100%; }
      .layout-stack .layout-footer { grid-area: footer; }

      .layout-toggle { display: none; }

      @media (width < 768px) {
        .layout-doc { grid-template-columns: 1fr; grid-template-areas: "nav" "main"; }
        .layout-doc .layout-sidebar { display: revert; position: fixed; inset: 0 auto 0 0; width: var(--_sidebar, 16rem); height: 100dvh; max-height: 100dvh; z-index: 100; margin: 0; transform: translateX(-100%); opacity: 0; transition: transform calc(var(--_motion) * 0.25s) ease, opacity calc(var(--_motion) * 0.25s) ease, display calc(var(--_motion) * 0.25s) allow-discrete, overlay calc(var(--_motion) * 0.25s) allow-discrete; }
        .layout-doc .layout-sidebar[open] { transform: translateX(0); opacity: 1; }
        .layout-doc .layout-sidebar::backdrop { display: revert; background: oklch(0% 0 0 / 0.4); opacity: 0; transition: opacity calc(var(--_motion) * 0.25s) ease, display calc(var(--_motion) * 0.25s) allow-discrete, overlay calc(var(--_motion) * 0.25s) allow-discrete; }
        .layout-doc .layout-sidebar[open]::backdrop { opacity: 1; }
        .layout-doc .layout-main { padding: --space(1); }
        .layout-doc .layout-toggle { display: inline-flex; }

        .layout-app { grid-template-columns: 1fr; grid-template-areas: "main"; }
        .layout-app .layout-sidebar { display: revert; position: fixed; inset: 0 auto 0 0; width: var(--_sidebar, 16rem); height: 100dvh; max-height: 100dvh; z-index: 100; margin: 0; transform: translateX(-100%); opacity: 0; transition: transform calc(var(--_motion) * 0.25s) ease, opacity calc(var(--_motion) * 0.25s) ease, display calc(var(--_motion) * 0.25s) allow-discrete, overlay calc(var(--_motion) * 0.25s) allow-discrete; }
        .layout-app .layout-sidebar[open] { transform: translateX(0); opacity: 1; }
        .layout-app .layout-sidebar::backdrop { display: revert; background: oklch(0% 0 0 / 0.4); opacity: 0; transition: opacity calc(var(--_motion) * 0.25s) ease, display calc(var(--_motion) * 0.25s) allow-discrete, overlay calc(var(--_motion) * 0.25s) allow-discrete; }
        .layout-app .layout-sidebar[open]::backdrop { opacity: 1; }
        .layout-app .layout-toggle { display: inline-flex; }
      }

      @media (width >= 1024px) {
        .layout-doc { grid-template-columns: var(--_sidebar, 16rem) 1fr var(--_toc, 14ch); grid-template-areas: "nav nav nav" "sidebar main toc"; }
        .layout-doc .layout-toc { display: block; grid-area: toc; padding: --space(1); position: sticky; top: 0; height: 100dvh; overflow-y: auto; font-size: 0.8em; color: --contrast(0.4); }
      }
    }


    /* ── components ────────────────────────────────────────────────── */

    @layer components {
      .card        { --_surface-level: calc(var(--_surface-level) + 1); --_bg: --surface(var(--_surface-level)); background: var(--_bg); }
      .code-editor { --_surface-level: calc(var(--_surface-level) - 1); --_bg: --surface(var(--_surface-level)); background: var(--_bg); }
      .card        { padding: 1.25rem; border: 1px solid --alpha(0.15, --fill()); border-radius: 0.5rem; }

      button {
        --_bg: --fill();
        --_border: --alpha(0.2, --contrast(0.3));
        --_shadow: --shadow(1);
        background: var(--_bg);
        color: --contrast();
        border: 1px solid var(--_border);
        border-radius: 0.375rem;
        padding: 0.4rem 1rem;
        font: inherit;
        font-size: 0.85rem;
        font-weight: 500;
        cursor: pointer;
        box-shadow: var(--_shadow);
        transition: all calc(var(--_motion) * 0.15s) ease;
      }
      button:hover { --_bg: --fill(1); --_shadow: --shadow(2); }
      button:active { --_bg: --fill(2); --_shadow: none; transform: translateY(calc(var(--_motion) * 1px)); }

      input[type="color"] { width: 2.5rem; height: 2rem; border: 1px solid --alpha(0.25, --fill()); border-radius: 0.25rem; cursor: pointer; padding: 2px; }
      input[type="range"] { accent-color: --fill(); }

      [popover].popover { position: fixed; inset: auto; margin: 0; border: none; min-width: clamp(10rem, 40vw, 18rem); max-width: min(90vw, 24rem); max-height: 80vh; overflow: auto; --_bg: --surface(1); background: var(--_bg); color: --contrast(0.7); border-radius: 0.5rem; box-shadow: --shadow(5); padding: --space(1); opacity: 1; transform: scale(1); position-area: self-block-start self-inline-end; position-try-order: most-block-size; position-try-fallbacks: flip-block, flip-inline, flip-block flip-inline; position-visibility: anchors-visible; transition: opacity calc(var(--_motion) * 0.18s) ease-out, transform calc(var(--_motion) * 0.18s) ease-out, display calc(var(--_motion) * 0.18s) allow-discrete, overlay calc(var(--_motion) * 0.18s) allow-discrete; }
      [popover].popover:not(:popover-open) { opacity: 0; transform: scale(0.95); }
      [popover].popover.below-start { position-area: self-block-end self-inline-start; }
      [popover].popover.below-end { position-area: self-block-end self-inline-end; }
      [popover].popover.above-start { position-area: self-block-start self-inline-start; }
      [popover].popover.above-end { position-area: self-block-start self-inline-end; }

      .fab { position: fixed; bottom: --space(2); right: --space(2); z-index: 50; width: 3rem; height: 3rem; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 1.2rem; anchor-name: --fab; }

      /* syntax highlighting — CSS Custom Highlight API */
      ::highlight(css-comment)     { color: oklch(from var(--_color) calc(45% + var(--_dark) * 20%) 0.03 h); }
      ::highlight(css-punctuation) { color: oklch(from var(--_color) calc(55% + var(--_dark) * 15%) 0.04 h); }
      ::highlight(css-property)    { color: oklch(from var(--_color) calc(65% + var(--_dark) * 10%) 0.18 calc(h + 180)); }
      ::highlight(css-value)       { color: oklch(from var(--_color) calc(60% + var(--_dark) * 15%) 0.12 calc(h + 60)); }
      ::highlight(css-number)      { color: oklch(from var(--_color) calc(65% + var(--_dark) * 10%) 0.16 calc(h + 120)); }
      ::highlight(css-unit)        { color: oklch(from var(--_color) calc(65% + var(--_dark) * 10%) 0.16 calc(h + 120)); }
      ::highlight(css-string)      { color: oklch(from var(--_color) calc(60% + var(--_dark) * 15%) 0.14 calc(h + 90)); }
      ::highlight(css-var-name)    { color: oklch(from var(--_color) calc(65% + var(--_dark) * 10%) 0.2 h); }
      ::highlight(css-selector)    { color: oklch(from var(--_color) calc(70% + var(--_dark) * 5%) 0.2 calc(h + 240)); }
      ::highlight(css-atrule)      { color: oklch(from var(--_color) calc(65% + var(--_dark) * 10%) 0.22 calc(h - 60)); }
      ::highlight(html-comment)    { color: oklch(from var(--_color) calc(45% + var(--_dark) * 20%) 0.03 h); }
      ::highlight(html-bracket)    { color: oklch(from var(--_color) calc(55% + var(--_dark) * 15%) 0.04 h); }
      ::highlight(html-tag)        { color: oklch(from var(--_color) calc(65% + var(--_dark) * 10%) 0.22 calc(h - 60)); }
      ::highlight(html-attribute)  { color: oklch(from var(--_color) calc(65% + var(--_dark) * 10%) 0.18 calc(h + 180)); }
      ::highlight(html-value)      { color: oklch(from var(--_color) calc(60% + var(--_dark) * 15%) 0.14 calc(h + 90)); }
      ::highlight(html-entity)     { color: oklch(from var(--_color) calc(65% + var(--_dark) * 10%) 0.16 calc(h + 120)); }
      ::highlight(html-doctype)    { color: oklch(from var(--_color) calc(55% + var(--_dark) * 15%) 0.1 calc(h + 30)); }

      /* code editor — highlighted textarea overlay */
      .code-editor { display: flex; --_bg: --surface(-1); background: var(--_bg); border-radius: 0.5rem; border: 1px solid --alpha(0.15, --fill()); min-height: 8rem; overflow: hidden; }
      .code-editor-gutter { margin: 0; padding: --space(1) --space(0) --space(1) --space(1); font-family: var(--_font-mono); font-size: 0.8em; line-height: 1.6; white-space: pre; color: --contrast(0.2); text-align: right; user-select: none; pointer-events: none; overflow: hidden; min-width: 2.5em; }
      .code-editor-wrap { position: relative; flex: 1; overflow: hidden; }
      .code-editor-wrap pre { margin: 0; padding: --space(1); font-family: var(--_font-mono); font-size: 0.8em; line-height: 1.6; white-space: pre-wrap; word-wrap: break-word; color: --contrast(0.6); pointer-events: none; }
      .code-editor-input { position: absolute; inset: 0; margin: 0; padding: --space(1); font-family: var(--_font-mono); font-size: 0.8em; line-height: 1.6; white-space: pre-wrap; word-wrap: break-word; background: transparent; color: transparent; caret-color: --fill(); border: none; outline: none; resize: none; overflow: auto; }
      .code-editor:focus-within { border-color: --alpha(0.4, --fill()); box-shadow: 0 0 0 2px --alpha(0.1, --fill()); }
    }



    /* ── overrides ─────────────────────────────────────────────────── */

    @layer overrides {
      .mobile, .tablet, .desktop { display: none; }
      @media (width < 768px)           { .mobile  { display: revert-layer; } }
      @media (768px <= width < 1024px) { .tablet  { display: revert-layer; } }
      @media (width >= 1024px)         { .desktop { display: revert-layer; } }
      @media print                     { .np      { display: none; } }
      .vh { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip-path: inset(50%); white-space: nowrap; border: 0; }
    }"""
    return (UI_CSS,)


@app.cell
def _(SCOPE_JS, UI_CSS):
    def ui_head(color=None, scheme=None, density=None, size=None):
        "Emit <script> + <style> for the UI framework"
        attrs = {}
        if color: attrs['style'] = f'--_color:{color}'
        if scheme: attrs['data_ui_scheme'] = scheme
        if density: attrs['data_ui_density'] = density
        if size: attrs['data_ui_size'] = size
        return Fragment(
            tag('script', SCOPE_JS),
            tag('style', UI_CSS),
            tag('html', **attrs) if attrs else None)


    return (ui_head,)


@app.cell
def _(mo):
    # UI controls for oklch color values
    lightness = mo.ui.slider(start=0, stop=100, value=65, step=1, label="Lightness (%)")
    chroma = mo.ui.slider(start=0, stop=0.5, value=0.25, step=0.01, label="Chroma")
    hue = mo.ui.slider(start=0, stop=360, value=320, step=1, label="Hue (°)")
    return chroma, hue, lightness


@app.cell
def _(chroma, hue, lightness, mo):
    # Display controls
    mo.md("### Color Controls")
    mo.hstack([lightness, chroma, hue])
    return


@app.cell
def _(Div, H1, Hr, P, chroma, hue, lightness, ui_head):
    # Create the page with dynamic color values
    page = Fragment(
        ui_head(color=f'oklch({lightness.value}% {chroma.value} {hue.value})', scheme='light'),
        Div(style="me > * {margin: 1rem;}")(
            H1('Scoped!'),
            P('This style only applies to this div.'),
            Div(cls="surface", style="border-radius: 1rem; padding: .25rem 1rem")("Im auto nested"),
            P("|"),
            Div(cls="surface", style="border-radius: 1rem; padding:2rem;")
            (
                Div(cls="surface", style="border-radius: 1rem; padding: .25rem 1rem")("Im auto nested")
            ),
            Div(style="margin:1rem")(Hr()),
            Div(cls="surface", style="border-radius: 1rem; padding: .25rem 1rem")("Im auto nested"),
            Div(style="margin:1rem")(Hr()),
            Div(cls="surface", style="border-radius: 1rem; padding: .25rem 1rem")("Im auto nested")
        )
    )

    return (page,)


@app.cell
def _(page):
    page
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
