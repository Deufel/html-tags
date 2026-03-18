import marimo

__generated_with = "0.21.0"
app = marimo.App(width="medium")

with app.setup:
    import types, re
    from collections import namedtuple
    from html import escape

    ALL_TAGS = [ 'A','Abbr','Address','Area','Article','Aside','Audio', 'B','Base','Bdi','Bdo','Blockquote','Body','Br','Button', 'Canvas','Caption','Cite','Code','Col','Colgroup', 'Data','Datalist','Dd','Del','Details','Dfn','Dialog','Div','Dl','Dt', 'Em','Embed', 'Fieldset','Figcaption','Figure','Footer','Form', 'H1','H2','H3','H4','H5','H6','Head','Header','Hgroup','Hr','Html', 'I','Iframe','Img','Input','Ins', 'Kbd', 'Label','Legend','Li','Link', 'Main','Map','Mark','Menu','Meta','Meter', 'Nav','Noscript', 'Object','Ol','Optgroup','Option','Output', 'P','Picture','Pre','Progress', 'Q', 'Rp','Rt','Ruby', 'S','Samp','Script','Search','Section','Select','Slot','Small','Source','Span','Strong','Style','Sub','Summary','Sup', 'Table','Tbody','Td','Template','Textarea','Tfoot','Th','Thead','Time','Title','Tr','Track', 'U','Ul', 'Var','Video', 'Wbr']

    VOID_TAGS = frozenset({"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"})
    RAW_TAGS = frozenset({"script", "style"})
    RAW_CLOSE_RE = re.compile(r'</(script|style)[\s/>]', re.IGNORECASE)



@app.class_definition
class Tag(namedtuple('Tag', 'tag children attrs', defaults=((), {}))):
    def __str__(self): return to_html(self)
    __html__ = _repr_html_ = __str__
    def __call__(self, *c, **kw):
        return Tag(self.tag, self.children + tuple(flatten(c)), {**self.attrs, **kw})


@app.function
def attrmap(k):
    match k:
        case 'cls'|'klass'|'_class': return 'class'
        case '_for'|'fr': return 'for'
        case _: return k.lstrip('_').replace('_', '-')


@app.function
def render_attrs(d):
    out = ''
    for k,v in d.items():
        k = attrmap(k)
        if v is True: out += f' {k}'
        elif v not in (False, None): out += f' {k}="{escape(str(v))}"'
    return out


@app.function
def is_void(t): return t.tag in VOID_TAGS


@app.function
def is_raw(t): return t.tag in RAW_TAGS


@app.function
def to_html(t, raw=False):
    if isinstance(t, str): return escape(t.replace('\x00', ''))
    if not hasattr(t, 'tag'): return escape(str(t).replace('\x00', ''))
    attrs = render_attrs(t.attrs) if t.attrs else ''
    if is_raw(t):
        inner = ''.join(str(c).replace('\x00', '') for c in t.children)
        validate_raw(t.tag, inner)
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


@app.function
def setup_tags(
    ns=None  # Optional namespace
):
    "Create tag constructors in the given namespace (or caller's globals)"
    import inspect
    if ns is None: ns = inspect.currentframe().f_back.f_globals
    H = TagNS()
    for name in ALL_TAGS: ns[name] = getattr(H, name)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Exploratory
    """)
    return


@app.cell
def _():
    a = tag('div', 'hello', cls='foo')
    b = mktag('div')('hello', cls='foo')
    c = TagNS().div('hello', cls='foo')
    print(f"{a = }\n{b = }\n{c = }")
    print(a==b==c)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Testing
    """)
    return


@app.cell
def _():
    H = TagNS()
    t = TagNS()
    Div,P,Span,A,Img,Button,Form,Input,Label = [getattr(H, n) for n in 
        ['Div','P','Span','A','Img','Button','Form','Input','Label']]
    return A, Div, Img, P, Span, t


@app.cell
def _():
    import pytest

    return (pytest,)


@app.cell(hide_code=True)
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
def _(mo):
    mo.md(r"""
    # Future

    - pull in scoped css auto
    - same for css
    -
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Scoped CSS
    ```js
    // 🌘 CSS Scope Inline (https://github.com/gnat/css-scope-inline)
    window.cssScopeCount ??= 1
    window.cssScope ??= new MutationObserver(mutations => {
    	document?.body?.querySelectorAll('style:not([ready])').forEach(node => {
    		var scope = 'me__'+(window.cssScopeCount++)
    		node.parentNode.classList.add(scope)
    		node.textContent = node.textContent
    		.replace(/(?:^|\.|(\s|[^a-zA-Z0-9\-\_]))(me|this|self)(?![a-zA-Z])/g, '$1.'+scope)
    		.replace(/((@keyframes|animation:|animation-name:)[^{};]*)\.me__/g, '$1me__')
    		node.setAttribute('ready', '')
    	})
    }).observe(document.documentElement, {childList: true, subtree: true})
    ```
    """)
    return


@app.cell(hide_code=True)
def _():
    return


@app.cell(hide_code=True)
def _():
    return


@app.function
def ui_head(color=None, scheme=None, density=None, size=None):
    "Emit <script> + <style> for the UI framework"
    attrs = {}
    if color: attrs['style'] = f'--_color:{color}'
    if scheme: attrs['data_ui_scheme'] = scheme
    if density: attrs['data_ui_density'] = density
    if size: attrs['data_ui_size'] = size
    return Fragment(
        tag('script', src="https://cdn.jsdelivr.net/gh/gnat/css-scope-inline@main/script.js"),
        
        tag('html', **attrs) if attrs else None)


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
def _(Div, H1, Hr, P, chroma, hue, lightness):
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
