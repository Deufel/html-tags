import marimo

__generated_with = "0.22.0"
app = marimo.App()

with app.setup:
    # test_html.py

    import pytest
    from html_tags.node  import Node, Safe, HTML, SVG, MATH
    from html_tags.attrs import normalize_attrs
    from html_tags.ns    import child_ns
    from html_tags.render import render
    from html_tags.dsl   import TagFactory
    from html_tags import doc

    from html_tags.viz_scale import LinearScale, BandScale, HueScale, OrdinalHueScale
    from html_tags.viz_mark  import rect, circle, line, polyline, path, path_d, area_d, text, group
    from html_tags.viz_axis  import axis
    from html_tags.viz_chart import chart, Margin


    h = TagFactory(HTML)
    s = TagFactory(SVG)
    m = TagFactory(MATH)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Html
    """)
    return


@app.cell
def _():
    # ALL TEST HERE 
    class TestNode:

        def test_basic_construction(self):
            n = Node('div', HTML, {'class': 'card'}, ())
            assert n.tag      == 'div'
            assert n.ns       == HTML
            assert n.attrs    == {'class': 'card'}
            assert n.children == ()

        def test_children_are_tuple(self):
            n = Node('ul', HTML, {}, (Node('li', HTML, {}, ('item',)),))
            assert isinstance(n.children, tuple)

        def test_nested_child_accessible(self):
            child = Node('li', HTML, {}, ('item',))
            n     = Node('ul', HTML, {}, (child,))
            assert n.children[0].tag == 'li'

        def test_invalid_namespace_raises(self):
            with pytest.raises(AssertionError):
                Node('div', 'xml', {}, ())

        def test_attrs_must_be_dict(self):
            with pytest.raises(AssertionError):
                Node('div', HTML, [], ())

        def test_children_must_be_tuple(self):
            with pytest.raises(AssertionError):
                Node('div', HTML, {}, [])

        def test_safe_is_str_subclass(self):
            s = Safe('<b>bold</b>')
            assert isinstance(s, str)
            assert isinstance(s, Safe)


    # ---------------------------------------------------------------------------
    # Layer 1 — normalize_attrs
    # ---------------------------------------------------------------------------

    class TestNormalizeAttrs:

        # aliases
        def test_cls_to_class(self):
            assert normalize_attrs(cls='btn') == {'class': 'btn'}

        def test_klass_to_class(self):
            assert normalize_attrs(klass='btn') == {'class': 'btn'}

        def test_fr_to_for(self):
            assert normalize_attrs(fr='email') == {'for': 'email'}

        def test_htmlfor_to_for(self):
            assert normalize_attrs(htmlfor='email') == {'for': 'email'}

        # leading underscore
        def test_leading_underscore_stripped(self):
            assert normalize_attrs(_for='email') == {'for': 'email'}

        # underscore to hyphen
        def test_single_underscore_to_hyphen(self):
            assert normalize_attrs(data_foo='bar') == {'data-foo': 'bar'}

        def test_multiple_underscores_to_hyphens(self):
            assert normalize_attrs(data_test_id='x') == {'data-test-id': 'x'}

        # dict passthrough
        def test_dict_passes_through_verbatim(self):
            result = normalize_attrs({'data-on:click': '@post("/save")'})
            assert result == {'data-on:click': '@post("/save")'}

        def test_dict_colon_key_unchanged(self):
            result = normalize_attrs({'xlink:href': '#icon'})
            assert result == {'xlink:href': '#icon'}

        # boolean values
        def test_true_kept(self):
            assert normalize_attrs(disabled=True) == {'disabled': True}

        def test_false_dropped(self):
            assert normalize_attrs(disabled=False) == {}

        def test_none_dropped(self):
            assert normalize_attrs(placeholder=None) == {}

        # merging
        def test_dict_and_kwargs_merge(self):
            result = normalize_attrs({'data-on:click': '@post("/x")'}, cls='card', disabled=True)
            assert result == {'data-on:click': '@post("/x")', 'class': 'card', 'disabled': True}

        def test_multiple_dicts_merge(self):
            result = normalize_attrs({'a': '1'}, {'b': '2'})
            assert result == {'a': '1', 'b': '2'}

        def test_kwargs_win_on_collision_with_dict(self):
            # kwargs applied after dicts — last writer wins
            result = normalize_attrs({'class': 'from-dict'}, cls='from-kwargs')
            assert result == {'class': 'from-kwargs'}

        def test_non_dict_positional_raises(self):
            with pytest.raises(AssertionError):
                normalize_attrs(['not', 'a', 'dict'])


    # ---------------------------------------------------------------------------
    # Layer 2 — child_ns
    # ---------------------------------------------------------------------------

    class TestChildNs:

        def test_html_inherits(self):
            assert child_ns(HTML, 'div') == HTML

        def test_html_to_svg(self):
            assert child_ns(HTML, 'svg') == SVG

        def test_html_to_math(self):
            assert child_ns(HTML, 'math') == MATH

        def test_svg_inherits(self):
            assert child_ns(SVG, 'circle') == SVG

        def test_svg_to_html_foreign_object(self):
            assert child_ns(SVG, 'foreignObject') == HTML

        def test_svg_desc_to_html(self):
            assert child_ns(SVG, 'desc') == HTML

        def test_svg_title_to_html(self):
            assert child_ns(SVG, 'title') == HTML

        def test_math_inherits(self):
            assert child_ns(MATH, 'mrow') == MATH

        def test_math_annotation_xml_to_html(self):
            assert child_ns(MATH, 'annotation-xml') == HTML


    # ---------------------------------------------------------------------------
    # Layer 3 — render
    # ---------------------------------------------------------------------------

    class TestRender:

        def test_basic_element(self):
            assert render(Node('p', HTML, {}, ('hello',))) == '<p>hello</p>'

        def test_empty_html_element(self):
            assert render(Node('div', HTML, {}, ())) == '<div></div>'

        def test_empty_svg_element_self_closes(self):
            assert render(Node('circle', SVG, {'r': '10'}, ())) == '<circle r="10"/>'

        def test_empty_math_element_self_closes(self):
            assert render(Node('mo', MATH, {}, ())) == '<mo/>'

        def test_html_void_br(self):
            assert render(Node('br', HTML, {}, ())) == '<br>'

        def test_html_void_input(self):
            assert render(Node('input', HTML, {}, ())) == '<input>'

        def test_html_void_img_with_attrs(self):
            assert render(Node('img', HTML, {'src': 'x.png'}, ())) == '<img src="x.png">'

        def test_boolean_attr_renders_bare(self):
            assert render(Node('input', HTML, {'disabled': True}, ())) == '<input disabled>'

        def test_multiple_attrs(self):
            out = render(Node('div', HTML, {'class': 'card', 'id': 'main'}, ()))
            assert 'class="card"' in out
            assert 'id="main"'    in out

        def test_text_escaping_lt_gt(self):
            assert render(Node('p', HTML, {}, ('<b>hi</b>',))) == '<p>&lt;b&gt;hi&lt;/b&gt;</p>'

        def test_text_escaping_ampersand(self):
            assert render(Node('p', HTML, {}, ('a & b',))) == '<p>a &amp; b</p>'

        def test_attr_value_escaping_quotes(self):
            out = render(Node('div', HTML, {'title': '"quoted"'}, ()))
            assert 'title="&quot;quoted&quot;"' in out

        def test_safe_bypasses_escaping(self):
            out = render(Node('div', HTML, {}, (Safe('<b>trusted</b>'),)))
            assert out == '<div><b>trusted</b></div>'

        def test_nested_tree(self):
            tree = Node('ul', HTML, {}, (
                Node('li', HTML, {}, ('one',)),
                Node('li', HTML, {}, ('two',)),
            ))
            assert render(tree) == '<ul><li>one</li><li>two</li></ul>'

        def test_numeric_child_int(self):
            assert render(Node('td', HTML, {}, (42,))) == '<td>42</td>'

        def test_numeric_child_float(self):
            assert render(Node('td', HTML, {}, (3.14,))) == '<td>3.14</td>'

        def test_render_bare_string(self):
            assert render('hello <world>') == 'hello &lt;world&gt;'

        def test_render_safe_string(self):
            assert render(Safe('<b>ok</b>')) == '<b>ok</b>'

        def test_svg_root_gets_xmlns_when_inside_html(self):
            node = Node('svg', SVG, {}, ())
            assert 'xmlns="http://www.w3.org/2000/svg"' in render(node)

        def test_svg_nested_in_svg_no_xmlns(self):
            inner = Node('svg', SVG, {}, ())
            outer = Node('svg', SVG, {}, (inner,))
            out   = render(outer)
            assert out.count('xmlns=') == 1

        def test_math_root_gets_xmlns(self):
            node = Node('math', MATH, {}, ())
            assert 'xmlns="http://www.w3.org/1998/Math/MathML"' in render(node)

        def test_explicit_xmlns_not_duplicated(self):
            node = Node('svg', SVG, {'xmlns': 'http://www.w3.org/2000/svg'}, ())
            out  = render(node)
            assert out.count('xmlns=') == 1


    # ---------------------------------------------------------------------------
    # Layer 4 — DSL
    # ---------------------------------------------------------------------------

    class TestDSL:

        def test_basic_tag(self):
            node = h.div(cls='card')
            assert node.tag   == 'div'
            assert node.ns    == HTML
            assert node.attrs == {'class': 'card'}

        def test_child_string(self):
            node = h.p('hello')
            assert node.children == ('hello',)

        def test_child_node(self):
            node = h.div(h.p('x'))
            assert node.children[0].tag == 'p'

        def test_attrs_and_children_together(self):
            node = h.p('lorem', cls='lead')
            assert node.attrs    == {'class': 'lead'}
            assert node.children == ('lorem',)

        def test_dict_attr_passthrough(self):
            node = h.div({'data-on:click': '@post("/x")'}, cls='btn')
            assert node.attrs['data-on:click'] == '@post("/x")'
            assert node.attrs['class']         == 'btn'

        def test_tag_alias_input(self):
            node = h.input_(type='text')
            assert node.tag == 'input'

        def test_escape_hatch_hyphenated(self):
            node = h('my-element')(cls='x')
            assert node.tag == 'my-element'

        def test_generator_children(self):
            node = h.ul(h.li(str(i)) for i in range(3))
            assert len(node.children) == 3
            assert node.children[0].tag == 'li'

        def test_svg_factory_stamps_svg_ns(self):
            node = s.circle(cx=50, cy=50, r=40)
            assert node.ns == SVG

        def test_math_factory_stamps_math_ns(self):
            node = m.mrow(m.mn('2'))
            assert node.ns == MATH

        def test_svg_nested_in_html_preserves_ns(self):
            svg_node  = s.svg(s.circle(r=10))
            html_page = h.div(h.p('before'), svg_node)
            assert html_page.ns             == HTML
            assert html_page.children[1].ns == SVG
            assert html_page.children[1].children[0].ns == SVG

        def test_dict_before_string_child(self):
            # your preferred style: dict first, content last
            node = h.p({"data-on:click": "@this"}, "lorem", cls="description")
            assert node.attrs['data-on:click'] == '@this'
            assert node.attrs['class']         == 'description'
            assert node.children               == ('lorem',)

        def test_leaf_with_attrs_is_node(self):
            # h.input_(type='text') must be a Node, not a Builder
            node = h.input_(type='text', disabled=True)
            assert isinstance(node, Node)

        def test_no_args_is_node(self):
            node = h.br()
            assert isinstance(node, Node)
            assert node.tag      == 'br'
            assert node.children == ()


    # ---------------------------------------------------------------------------
    # End to end
    # ---------------------------------------------------------------------------

    class TestEndToEnd:

        def test_html_fragment(self):
            page = h.div(
                h.h1('Hello'),
                h.p('a & b < c'),
                h.ul(h.li(str(i)) for i in range(3)),
                h.input_(type='text', disabled=True),
                h.br(),
                cls='wrapper',
            )
            out = render(page)
            assert '<div class="wrapper">'        in out
            assert '<h1>Hello</h1>'               in out
            assert 'a &amp; b &lt; c'             in out
            assert '<li>0</li>'                   in out
            assert '<input type="text" disabled>' in out
            assert '<br>'                         in out
            assert '</div>'                       in out

        def test_svg_fragment(self):
            chart = s.svg(
                {'xmlns': 'http://www.w3.org/2000/svg'},
                s.circle(cx=50, cy=50, r=40, fill='steelblue'),
                s.rect(x=10, y=10, width=80, height=80),
            )
            out = render(chart)
            assert 'xmlns="http://www.w3.org/2000/svg"' in out
            assert '<circle'                            in out
            assert 'fill="steelblue"'                  in out
            assert '/>'                                 in out

        def test_svg_in_html(self):
            page = h.div(
                h.p('chart below'),
                s.svg(s.rect(x=0, y=0, width=100, height=100)),
            )
            out = render(page)
            assert out.startswith('<div>')
            assert '<svg xmlns="http://www.w3.org/2000/svg">' in out
            assert '<rect '                                   in out
            assert '/>'                                       in out

        def test_mathml_fragment(self):
            eq = m.math(
                m.mrow(
                    m.msup(m.mi('x'), m.mn('2')),
                    m.mo('+'),
                    m.msup(m.mi('y'), m.mn('2')),
                )
            )
            out = render(eq)
            assert '<math xmlns="http://www.w3.org/1998/Math/MathML">' in out
            assert '<msup>'                                            in out
            assert '<mi>x</mi>'                                       in out

        def test_datastar_attrs_survive(self):
            btn = h.button(
                {'data-on:click': '@post("/inc")', 'data-bind:disabled': '$loading'},
                'Click',
                cls='btn',
            )
            out = render(btn)
            assert 'data-bind:disabled="$loading"' in out
            assert 'class="btn"'                   in out
            assert '>Click<'                        in out

        def test_animals_generator(self):
            animals = ['cat', 'dog', 'goat']
            node    = h.ul(h.li(a) for a in animals)
            out     = render(node)
            assert '<li>cat</li>'  in out
            assert '<li>dog</li>'  in out
            assert '<li>goat</li>' in out
            assert out.startswith('<ul>')
            assert out.endswith('</ul>')


    class TestComponentProtocol:

        def test_component_as_child(self):
            class Badge:
                def __node__(self):
                    return h.span('hello', cls='badge')

            node = h.div(Badge())
            assert node.children[0].tag   == 'span'
            assert node.children[0].attrs == {'class': 'badge'}

        def test_component_in_generator(self):
            class Item:
                def __init__(self, label): self.label = label
                def __node__(self): return h.li(self.label)

            items = [Item('a'), Item('b'), Item('c')]
            node  = h.ul(i for i in items)
            assert len(node.children)     == 3
            assert node.children[0].tag  == 'li'

        def test_component_renders(self):
            class Alert:
                def __node__(self): return h.div('warning', cls='alert')

            out = render(h.div(Alert()))
            assert '<div class="alert">warning</div>' in out

        def test_component_in_svg(self):
            class Dot:
                def __node__(self): return s.circle(cx=10, cy=10, r=5)

            node = s.svg(Dot())
            assert node.children[0].tag == 'circle'
            assert node.children[0].ns  == SVG


    class TestDoc:

        def test_starts_with_doctype(self):
            out = doc(h.head(), h.body())
            assert out.startswith('<!DOCTYPE html>')

        def test_wraps_in_html_tag(self):
            out = doc(h.head(), h.body())
            assert '<html lang="en">' in out
            assert '</html>'          in out

        def test_custom_lang(self):
            out = doc(h.head(), h.body(), lang='fr')
            assert '<html lang="fr">' in out

        def test_children_present(self):
            out = doc(
                h.head(h.title('Test')),
                h.body(h.p('hello')),
            )
            assert '<title>Test</title>' in out
            assert '<p>hello</p>'        in out

    return


@app.cell
def _():
    return


@app.cell
def _():


    def demo():
        gradient = s.defs(
            s.linearGradient(
                s.stop({"stop-color": "#6366f1"}, offset="0%"),
                s.stop({"stop-color": "#06b6d4"}, offset="100%"),
                id="grad",
                x1="0%", y1="0%", x2="100%", y2="0%",
            )
        )

        pulse = s.circle(
            s.animate(
                attributeName="r",
                values="40;55;40",
                dur="2s",
                repeatCount="indefinite",
            ),
            s.animate(
                attributeName="opacity",
                values="1;0.4;1",
                dur="2s",
                repeatCount="indefinite",
            ),
            cx="200", cy="200", r="40",
            fill="url(#grad)",
        )

        orbit = s.circle(
            s.animateTransform(
                attributeName="transform",
                type="rotate",
                values="0 200 200;360 200 200",
                dur="3s",
                repeatCount="indefinite",
            ),
            cx="280", cy="200", r="10",
            fill="#f472b6",
        )

        bar = s.rect(
            s.animate(
                attributeName="width",
                values="80;160;80",
                dur="2.5s",
                repeatCount="indefinite",
            ),
            s.animate(
                attributeName="fill",
                values="#6366f1;#06b6d4;#6366f1",
                dur="2.5s",
                repeatCount="indefinite",
            ),
            x="100", y="300", width="80", height="24",
            rx="4",
        )

        label = s.text(
            "html_tags svg demo",
            {"text-anchor": "middle", "font-family": "monospace", "font-size": "13"},
            x="200", y="380",
            fill="#94a3b8",
        )

        spoke = s.line(
            s.animateTransform(
                attributeName="transform",
                type="rotate",
                values="0 200 200;360 200 200",
                dur="3s",
                repeatCount="indefinite",
            ),
            {"stroke-width": "1", "stroke-dasharray": "4 4"},
            x1="200", y1="200", x2="280", y2="200",
            stroke="#475569",
            opacity="0.5",
        )

        svg = s.svg(
            {"xmlns": "http://www.w3.org/2000/svg"},
            gradient, spoke, pulse, orbit, bar, label,
            width="400", height="420",
            viewBox="0 0 400 420",
            style="background:#0f172a; border-radius:12px;",
        )

        page = h.html(
            h.head(
                h.meta(charset="utf-8"),
                h.title("svg demo"),
                h.style(Safe("""
                    body {
                        margin: 0;
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        background: #020617;
                        font-family: monospace;
                    }
                """)),
            ),
            h.body(svg),
        )

        return "<!DOCTYPE html>\n" + render(page)


    if __name__ == "__main__":
        with open("demo.html", "w") as f:
            f.write(demo())
        print("wrote demo.html")
    return (demo,)


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(demo, mo):
    mo.Html(demo())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Viz

    charting library built on html_tags and color.css
    """)
    return


@app.class_definition
class TestAxis:

    def test_returns_node_protocol(self):
        x  = LinearScale(domain=(0, 100), range_=(0, 400))
        ax = axis(x, 'bottom')
        assert hasattr(ax, '__node__')

    def test_node_is_g_element(self):
        x    = LinearScale(domain=(0, 100), range_=(0, 400))
        node = axis(x, 'bottom').__node__()
        assert node.tag == 'g'
        assert node.ns  == SVG

    def test_bad_orientation_raises(self):
        x = LinearScale(domain=(0, 100), range_=(0, 400))
        with pytest.raises(AssertionError):
            axis(x, 'diagonal')

    def test_bottom_axis_has_ticks(self):
        x    = LinearScale(domain=(0, 100), range_=(0, 400))
        node = axis(x, 'bottom', tick_count=5).__node__()
        assert len(node.children) == 6   # baseline + 5 tick groups

    def test_left_axis_has_ticks(self):
        y    = LinearScale(domain=(0, 50), range_=(300, 0))
        node = axis(y, 'left', tick_count=3).__node__()
        assert len(node.children) == 4   # baseline + 3

    def test_band_axis_uses_all_categories(self):
        x    = BandScale(domain=['A', 'B', 'C'], range_=(0, 300))
        node = axis(x, 'bottom').__node__()
        assert len(node.children) == 4   # baseline + 3

    def test_custom_tick_format(self):
        x    = LinearScale(domain=(0, 1), range_=(0, 100))
        node = axis(x, 'bottom', tick_count=2,
                    tick_format=lambda v: f'{v:.0%}').__node__()
        out  = render(node)
        assert '0%'   in out
        assert '100%' in out

    def test_default_format_integer(self):
        x    = LinearScale(domain=(0, 5), range_=(0, 100))
        node = axis(x, 'bottom', tick_count=2).__node__()
        out  = render(node)
        assert '>5<'   in out
        assert '>5.0<' not in out

    def test_default_format_float(self):
        x    = LinearScale(domain=(0, 1), range_=(0, 100))
        node = axis(x, 'bottom', tick_count=3).__node__()
        out  = render(node)
        assert '>0.5<' in out

    def test_default_format_strips_trailing_zeros(self):
        x    = LinearScale(domain=(0, 3.14), range_=(0, 100))
        node = axis(x, 'bottom', tick_count=2).__node__()
        out  = render(node)
        assert '>3.14<' in out
        assert '3.1400' not in out

    def test_cls_applied_to_group(self):
        x    = LinearScale(domain=(0, 100), range_=(0, 400))
        node = axis(x, 'bottom', cls='axis').__node__()
        assert node.attrs.get('class') == 'axis'

    def test_renders_without_error(self):
        x   = LinearScale(domain=(0, 100), range_=(0, 400))
        out = render(axis(x, 'bottom').__node__())
        assert '<g>'   in out
        assert '<line' in out
        assert '<text' in out


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## viz_charts.py
    """)
    return


@app.class_definition
class TestChart:

    def test_returns_node_protocol(self):
        c = chart(500, 300)
        assert hasattr(c, '__node__')

    def test_outer_is_svg(self):
        node = chart(500, 300).__node__()
        assert node.tag == 'svg'
        assert node.ns  == SVG

    def test_dimensions(self):
        node = chart(500, 300).__node__()
        assert node.attrs['width']  == 500
        assert node.attrs['height'] == 300

    def test_viewbox(self):
        node = chart(500, 300).__node__()
        assert node.attrs['viewBox'] == '0 0 500 300'

    def test_inner_g_translated(self):
        m    = Margin(top=20, right=20, bottom=40, left=50)
        node = chart(500, 300, margin=m).__node__()
        g    = node.children[0]
        assert g.tag                   == 'g'
        assert 'translate(50,20)'      in g.attrs['transform']

    def test_margin_inner_dimensions(self):
        m = Margin(top=20, right=20, bottom=40, left=50).bind(500, 300)
        assert m.inner_width  == 430
        assert m.inner_height == 240

    def test_layers_inside_inner_g(self):
        r    = rect(x=0, y=0, width=10, height=10)
        node = chart(500, 300, r).__node__()
        g    = node.children[0]
        assert g.children[0].tag == 'rect'

    def test_node_protocol_layers_resolved(self):
        x    = LinearScale(domain=(0,100), range_=(0,400))
        node = chart(500, 300, axis(x, 'bottom')).__node__()
        g    = node.children[0]
        assert g.children[0].tag == 'g'   # axis renders as <g>

    def test_cls_on_svg(self):
        node = chart(500, 300, cls='my-chart').__node__()
        assert node.attrs['class'] == 'my-chart'

    def test_default_margin(self):
        m = Margin().bind(500, 300)
        assert m.inner_width  == 500 - 20 - 50
        assert m.inner_height == 300 - 40 - 40


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
