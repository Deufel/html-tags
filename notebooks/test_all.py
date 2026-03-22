import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full")


@app.cell
def _():
    from a_core import Tag, attrmap, render_attrs, is_void, is_raw, to_html, mktag, Fragment, flatten, validate_raw, setup_tags, pretty, dunder_getattr
    from b_sse import patch_elements, patch_signals
    from c_svg import setup_svg
    import pytest
    setup_tags()
    setup_svg()
    return (
        Fragment,
        attrmap,
        mktag,
        patch_elements,
        patch_signals,
        pretty,
        pytest,
        render_attrs,
        to_html,
    )


@app.cell(hide_code=True)
def _(
    A,
    Article,
    B,
    Br,
    Div,
    Fragment,
    Img,
    Input,
    Label,
    Li,
    P,
    Script,
    Section,
    Span,
    Style,
    Ul,
    pytest,
    render_attrs,
    to_html,
):
    def test_basic_tag(): assert to_html(Div('hello')) == '<div>hello</div>'
    def test_nested_tags(): assert to_html(Div(P('inner'))) == '<div><p>inner</p></div>'
    def test_deeply_nested(): assert to_html(Div(Ul(Li(B('deep'))))) == '<div><ul><li><b>deep</b></li></ul></div>'
    def test_multiple_children(): assert to_html(Div('a', 'b', 'c')) == '<div>abc</div>'
    def test_attrs_cls(): assert to_html(Div('hi', cls='box')) == '<div class="box">hi</div>'
    def test_attrs_multiple(): assert to_html(Div('hi', cls='box', id='main')) == '<div class="box" id="main">hi</div>'
    def test_attrs_boolean_true(): assert to_html(Input(type='text', disabled=True)) == '<input type="text" disabled>'
    def test_attrs_boolean_false(): assert 'disabled' not in to_html(Input(type='text', disabled=False))
    def test_attrs_none_skipped(): assert 'title' not in to_html(Div('hi', title=None))

    def test_render_attrs_dict(): assert render_attrs({"data-on:click__debounce.500ms": "@get('/endpoint', {contentType: 'form'})"}) == ' data-on:click__debounce.500ms="@get(\'/endpoint\', {contentType: \'form\'})"'

    def test_render_attrs_bool(): assert render_attrs(dict(disabled=True)) == ' disabled'
    def test_render_attrs_false(): assert render_attrs(dict(disabled=False)) == ''
    def test_render_attrs_none(): assert render_attrs(dict(disabled=None)) == ''
    def test_render_attrs_cls(): assert render_attrs(dict(cls='foo')) == ' cls="foo"'
    def test_render_attrs_for(): assert render_attrs(dict(_for='myid')) == ' _for="myid"'

    def test_render_attrs_amp(): assert render_attrs(dict(title='a&b')) == ' title="a&amp;b"'
    def test_render_attrs_lt(): assert render_attrs(dict(title='a<b')) == ' title="a&lt;b"'

    def test_attrs_for(): assert to_html(Label('Name', _for='name')) == '<label for="name">Name</label>'

    def test_void_br(): assert to_html(Br()) == '<br>'
    def test_void_img(): assert to_html(Img(src='cat.jpg', alt='cat')) == '<img src="cat.jpg" alt="cat">'
    def test_void_no_children(): assert to_html(Br()) == '<br>'

    def test_escape_text(): assert to_html(Div('<script>alert("xss")</script>')) == '<div>&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;</div>'
    def test_escape_ampersand(): assert to_html(P('a & b')) == '<p>a &amp; b</p>'

    def test_raw_script(): assert to_html(Script('let x = 1 < 2;')) == '<script>let x = 1 < 2;</script>'
    def test_raw_style(): assert to_html(Style('body { color: red; }')) == '<style>body { color: red; }</style>'

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
    def test_tagns_any_tag(): assert to_html(Article(Section('hi'))) == '<article><section>hi</section></article>'
    def test_empty_tag(): assert to_html(Div()) == '<div></div>'
    def test_mixed_children(): assert to_html(Div('text', B('bold'), ' more')) == '<div>text<b>bold</b> more</div>'
    def test_null_byte_stripped_raw(): assert to_html(Script('alert\x00("hi")')) == '<script>alert("hi")</script>'
    def test_null_byte_stripped_raw_style(): assert to_html(Style('body\x00 { color: red; }')) == '<style>body { color: red; }</style>'
    def test_null_byte_escaped_normal(): assert to_html(Div('hello\x00world')) == '<div>helloworld</div>'
    def test_raw_str_not_escaped(): assert to_html(Script('1 < 2 && 3 > 1')) == '<script>1 < 2 && 3 > 1</script>'
    def test_raw_validates_script():
        with pytest.raises(ValueError): to_html(Script('</script>'))
    def test_raw_validates_style():
        with pytest.raises(ValueError): to_html(Style('</style >'))
    def test_raw_validates_case_insensitive():
        with pytest.raises(ValueError): to_html(Script('</SCRIPT>'))
    def test_non_tag_escaped(): assert to_html(Div(42)) == '<div>42</div>'
    def test_fragment_renders_inner_only(): assert to_html(Fragment(Div('a'), Div('b'))) == '<div>a</div><div>b</div>'
    def test_void_no_closing(): assert to_html(Br()) == '<br>'
    def test_void_with_attrs(): assert to_html(Img(src='x.png')) == '<img src="x.png">'
    def test_empty_string_child(): assert to_html(Div('')) == '<div></div>'



    return


@app.cell(hide_code=True)
def _(Div, P, Span, patch_elements, patch_signals, to_html):
    def test_xss_attr(): assert to_html(Div(href='"><script>alert(1)</script>')) == '<div href="&quot;>&lt;script>alert(1)&lt;/script>"></div>'
    def test_class_alias(): assert to_html(Div('hi', _class='box')) == '<div class="box">hi</div>'
    def test_curry_call(): assert str(Div(cls='box')('hello')) == '<div class="box">hello</div>'
    def test_dict_attrs_positional(): assert to_html(Div({'id': 'main'}, 'hi')) == '<div id="main">hi</div>'
    def test_curry_attrs_first(): assert str(Div(cls='container')(P('hello'))) == '<div class="container"><p>hello</p></div>'
    def test_curry_chained(): assert str(Div(id='a')(Span(cls='b')('hi'))) == '<div id="a"><span class="b">hi</span></div>'
    def test_curry_multiple_children(): assert str(Div(cls='box')('a', 'b', 'c')) == '<div class="box">abc</div>'
    def test_patch_elements_basic(): assert 'event: datastar-patch-elements' in patch_elements('<div>hi</div>')
    def test_patch_elements_selector(): assert 'data: selector #foo' in patch_elements('<div>hi</div>', selector='#foo')
    def test_patch_elements_tag(): assert '<div>hi</div>' in patch_elements(Div('hi'))
    def test_patch_signals_basic(): assert 'event: datastar-patch-signals' in patch_signals('{"foo": 1}')
    def test_patch_signals_only_if_missing(): assert 'data: onlyIfMissing true' in patch_signals('{"foo": 1}', only_if_missing=True)

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Testing pretty printing & attribute escaping & html tag handeling
    """)
    return


@app.cell(hide_code=True)
def _(Body, Br, Div, Fragment, Html, P, Script, Style, pretty, pytest):

    def test_root_html_has_doctype(): assert str(Html(Body("hi"))).startswith("<!DOCTYPE html>")

    def test_nested_html_raises():
        with pytest.raises(ValueError): Div(Html())

    def test_partial_no_doctype(): assert not str(Div("hi")).startswith("<!DOCTYPE")

    def test_fragment_wrapping_html_has_doctype(): assert str(Fragment(Html(Body("hi")))).startswith("<!DOCTYPE html>")

    def test_pretty_basic_indentation(): assert "  <p>a</p>" in pretty(Div(P("a"), P("b")))

    def test_pretty_single_text_inline(): assert pretty(P("hello")) == "<p>hello</p>"

    def test_pretty_void_tag(): assert pretty(Br()) == "<br>"

    def test_pretty_style_indented(): assert "  body" in pretty(Style("body { color: red; }"))

    def test_pretty_script_not_indented(): assert "  let" not in pretty(Script("let x = 1;"))

    def test_pretty_script_indented_opt_in(): assert "  let" in pretty(Script("let x = 1;"), indent_script=True)

    def test_pretty_nested_html_raises():
        with pytest.raises(ValueError): pretty(Div(Html()))

    def test_pretty_has_doctype(): assert pretty(Html(Body("hi"))).startswith("<!DOCTYPE html>")

    def test_pretty_xss_escaped():
        out = pretty(Div("<script>alert(1)</script>"))
        assert "<script>" not in out
        assert "&lt;script&gt;" in out


    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Custom import testing
    """)
    return


@app.cell
def _(Div, P, mktag, pytest):
    def test_custom_tag_via_mktag():
        MyWidget = mktag('my-widget')
        assert str(MyWidget("hello", {"class": "x"})) == '<my-widget class="x">hello</my-widget>'

    def test_custom_tag_via_mktag_simple():
        assert str(mktag('my-widget')("hello")) == '<my-widget>hello</my-widget>'

    def test_custom_tag_with_children():
        assert str(mktag('app-header')(Div("inside"))) == '<app-header><div>inside</div></app-header>'

    def test_custom_tag_module_getattr():
        from html_tags.core import My_Widget
        assert str(My_Widget("hi")) == '<my-widget>hi</my-widget>'

    def test_custom_tag_module_getattr_nested():
        from html_tags.core import App_Header
        assert str(App_Header(P("nav"), {"id": "top"})) == '<app-header id="top"><p>nav</p></app-header>'

    def test_custom_tag_lowercase_raises():
        with pytest.raises(ImportError): from html_tags.core import nonexistent

    def test_custom_tag_escapes_content():
        assert "&lt;script&gt;" in str(mktag('x-card')("<script>alert(1)</script>"))

    def test_custom_tag_void_not_assumed():
        assert str(mktag('x-icon')()) == '<x-icon></x-icon>'


    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## SVG
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Basic SVG
    """)
    return


@app.cell
def _(
    Circle,
    ClipPath,
    Defs,
    FeGaussianBlur,
    G,
    Line,
    LinearGradient,
    Path,
    Rect,
    Stop,
    Svg,
    pytest,
):
    # Basic SVG
    def test_svg_circle(): assert str(Circle(cx="10", cy="10", r="5")) == '<circle cx="10" cy="10" r="5" />'
    def test_svg_rect(): assert str(Rect(x="0", y="0", width="100", height="50")) == '<rect x="0" y="0" width="100" height="50" />'
    def test_svg_wrapper(): assert str(Svg(G())) == '<svg><g></g></svg>'
    def test_svg_path(): assert str(Path(d="M0 0 L10 10")) == '<path d="M0 0 L10 10" />'
    def test_svg_line(): assert str(Line(x1="0", y1="0", x2="10", y2="10")) == '<line x1="0" y1="0" x2="10" y2="10" />'


    # Case Sensitive SVG
    def test_svg_clippath(): assert str(ClipPath(Rect(x="0", y="0", width="10", height="10"))) == '<clipPath><rect x="0" y="0" width="10" height="10" /></clipPath>'
    def test_svg_linear_gradient(): assert str(LinearGradient(Stop(offset="0%"))) == '<linearGradient><stop offset="0%" /></linearGradient>'
    def test_svg_fe_gaussian_blur(): assert str(FeGaussianBlur(stdDeviation="5")) == '<feGaussianBlur stdDeviation="5" />'

    # Void validation and nesting
    def test_svg_void_rejects_children():
        with pytest.raises(ValueError): Stop("child")

    def test_svg_nested(): assert str(Svg(Defs(ClipPath(Rect(width="10", height="10"))))) == '<svg><defs><clipPath><rect width="10" height="10" /></clipPath></defs></svg>'

    # Attributes
    def test_svg_viewbox(): assert 'viewBox="0 0 24 24"' in str(Svg({"viewBox": "0 0 24 24"}))
    def test_svg_xmlns(): assert 'xmlns="http://www.w3.org/2000/svg"' in str(Svg({"xmlns": "http://www.w3.org/2000/svg"}))





    return


@app.cell
def _(Div):
    # SVG simulating a __html__ protocol
    def test_html_protocol_in_children():
        class SafeStr:
            def __html__(self): return '<b>safe</b>'
        assert str(Div(SafeStr())) == '<div><b>safe</b></div>'


    return


@app.cell
def _(AnimateTransform, Div, FeBlend, attrmap):
    def test_attrmap_cls(): assert attrmap('cls') == 'class'
    def test_attrmap_class(): assert attrmap('_class') == 'class'
    def test_attrmap_for(): assert attrmap('_for') == 'for'
    def test_attrmap_from(): assert attrmap('_from') == 'from'
    def test_attrmap_in(): assert attrmap('_in') == 'in'
    def test_attrmap_is(): assert attrmap('_is') == 'is'
    def test_attrmap_underscore_to_hyphen(): assert attrmap('data_value') == 'data-value'
    def test_attrmap_stroke_width(): assert attrmap('stroke_width') == 'stroke-width'
    def test_attrmap_no_underscore(): assert attrmap('id') == 'id'
    def test_attrmap_double_underscore(): assert attrmap('__weird') == '--weird'
    def test_attrmap_passthrough(): assert attrmap('viewBox') == 'viewBox'

    def test_e2e_from(): assert str(AnimateTransform(_from="0 200 200", to="360 200 200")) == '<animateTransform from="0 200 200" to="360 200 200" />'
    def test_e2e_in(): assert str(FeBlend(_in="SourceGraphic")) == '<feBlend in="SourceGraphic" />'
    def test_e2e_dict_verbatim(): assert str(Div({"data-on:click__once": "@post('/api')"})) == '<div data-on:click__once="@post(\'/api\')"></div>'

    return


@app.cell
def _(Button):
    print(Button({"data-on:click":"@get('/endpoint')"}, cls="btn")("Click here"))
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
