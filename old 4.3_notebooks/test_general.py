import marimo

__generated_with = "0.22.0"
app = marimo.App()


@app.cell
def _():
    """Pytest suite for html_tags.

    Organized by concern — each class tests one aspect of the library so a
    failure points at one thing. Run with:  pytest test_html_tags_pytest.py -v
    """
    import pytest

    from html_tags import (
        # core
        tag, mk_tag, render, render_attrs, html_doc, Safe, is_tag, unpack,
        # parser
        html_to_tag,
        # utility tags
        Datastar, MeCSS, Pointer, Favicon,
        # module-level __getattr__ provides arbitrary tag names
        div, p, span, ul, li, section, article, h1, input_,
        svg, circle, rect,
    )


    # ──────────────────────────────────────────────────────────────────────────
    # 1. Core construction
    # ──────────────────────────────────────────────────────────────────────────
    return (
        Datastar,
        Favicon,
        MeCSS,
        Pointer,
        Safe,
        article,
        circle,
        div,
        html_doc,
        html_to_tag,
        input_,
        is_tag,
        li,
        mk_tag,
        p,
        pytest,
        rect,
        render,
        render_attrs,
        section,
        span,
        svg,
        ul,
        unpack,
    )


@app.cell
def _(
    Datastar,
    Favicon,
    MeCSS,
    Pointer,
    Safe,
    article,
    circle,
    div,
    html_doc,
    html_to_tag,
    input_,
    is_tag,
    li,
    mk_tag,
    p,
    pytest,
    rect,
    render,
    render_attrs,
    section,
    span,
    svg,
    ul,
    unpack,
):
    class TestConstruction:
        def test_empty_tag(self):
            html = render(div())
            assert '<div>' in html and '</div>' in html

        def test_tag_with_text(self):
            assert render(p("hello")) == '<p>hello</p>'

        def test_tag_with_single_child(self):
            assert '<span>hi</span>' in render(div(span("hi")))

        def test_tag_with_kwarg_attr(self):
            assert '<div class="x">' in render(div(cls="x"))

        def test_tag_with_multiple_kwargs(self):
            html = render(div(cls="x", id="main"))
            assert 'class="x"' in html
            assert 'id="main"' in html

        def test_nested_construction(self):
            html = render(section(article(p("text"))))
            assert '<section>' in html
            assert '<article>' in html
            assert '<p>text</p>' in html

        def test_text_in_tag_is_escaped(self):
            assert render(p("<script>alert(1)</script>")) == \
                '<p>&lt;script&gt;alert(1)&lt;/script&gt;</p>'

        def test_attr_value_is_escaped(self):
            html = render(div(title='say "hi"'))
            assert 'title="say &quot;hi&quot;"' in html


    # ──────────────────────────────────────────────────────────────────────────
    # 2. Purity / non-mutation
    # ──────────────────────────────────────────────────────────────────────────

    class TestPurity:
        def test_extend_does_not_mutate_original(self):
            shell = div(cls="shell")
            a = shell(p("A"))
            b = shell(p("B"))
            assert len(shell.children) == 0
            assert len(a.children) == 1
            assert len(b.children) == 1

        def test_original_attrs_unchanged_after_extension(self):
            base = div(cls="base")
            _ = base(id="extended")
            assert base.attrs == {"class": "base"}
            assert "id" not in base.attrs

        def test_two_extensions_are_independent(self):
            shell = ul()
            a = shell(li("a"))
            b = shell(li("b"))
            # a should not contain b's children and vice versa
            a_html = render(a)
            b_html = render(b)
            assert 'a' in a_html and 'b' not in a_html
            assert 'b' in b_html and 'a' not in b_html

        def test_extension_preserves_existing_children(self):
            t = div(p("first"))
            t2 = t(p("second"))
            assert len(t2.children) == 2


    # ──────────────────────────────────────────────────────────────────────────
    # 3. The dict-vs-kwarg rule (core design decision)
    # ──────────────────────────────────────────────────────────────────────────

    class TestAttrRule:
        """Dict keys are emitted verbatim. Kwargs are Pythonified."""

        def test_kwarg_cls_becomes_class(self):
            assert 'class="x"' in render(div(cls="x"))

        def test_kwarg_underscore_for_becomes_for(self):
            assert render_attrs({"for": "email"}) == ' for="email"'
            # via kwarg channel:
            html = render(mk_tag('label')(_for="email"))
            assert 'for="email"' in html

        def test_kwarg_underscore_becomes_hyphen(self):
            html = render(div(data_test_id="x"))
            assert 'data-test-id="x"' in html

        def test_kwarg_trailing_underscore_stripped(self):
            html = render(div(class_="x"))
            assert 'class="x"' in html

        def test_dict_keys_pass_through_verbatim(self):
            html = render(div({"data-on:click": "@post('/x')"}))
            # apostrophes are escaped to &#x27; by html.escape — that's correct
            assert 'data-on:click="@post(&#x27;/x&#x27;)"' in html

        def test_dict_double_underscore_preserved(self):
            html = render(div({"data-on:click__debounce.500ms": "$x++"}))
            assert 'data-on:click__debounce.500ms="$x++"' in html

        def test_dict_colon_preserved(self):
            html = render(div({"data-signals:user.name": "'Alice'"}))
            assert 'data-signals:user.name="&#x27;Alice&#x27;"' in html

        def test_dict_with_cls_is_NOT_transformed(self):
            """Dict keys are raw — user must use 'class' not 'cls'."""
            html = render(div({"cls": "x"}))
            assert 'cls="x"' in html         # literal, no transform
            assert 'class="x"' not in html

        def test_dict_and_kwargs_merge(self):
            html = render(div({"data-on:click": "go()"}, cls="btn"))
            assert 'data-on:click="go()"' in html
            assert 'class="btn"' in html

        def test_kwargs_override_dict_after_pythonification(self):
            # {"class": "a"} + cls="b" → class="b" (kwarg wins, post-transform)
            html = render(div({"class": "a"}, cls="b"))
            assert 'class="b"' in html
            assert 'class="a"' not in html


    # ──────────────────────────────────────────────────────────────────────────
    # 4. Attribute value types
    # ──────────────────────────────────────────────────────────────────────────

    class TestAttrValues:
        def test_true_renders_bare_attr(self):
            html = render(input_(disabled=True))
            assert ' disabled' in html
            assert 'disabled=' not in html

        def test_false_omits_attr(self):
            html = render(input_(disabled=False))
            assert 'disabled' not in html

        def test_none_omits_attr(self):
            html = render(input_(disabled=None))
            assert 'disabled' not in html

        def test_integer_value_renders(self):
            html = render(input_(maxlength=10))
            assert 'maxlength="10"' in html

        def test_dict_true_value(self):
            html = render(div({"data-ignore": True}))
            assert 'data-ignore' in html
            assert 'data-ignore=' not in html


    # ──────────────────────────────────────────────────────────────────────────
    # 5. Void elements
    # ──────────────────────────────────────────────────────────────────────────

    class TestVoidElements:
        def test_html_void_has_no_closing_tag(self):
            html = render(mk_tag('br')())
            assert html == '<br>'
            assert '</br>' not in html

        def test_html_void_renders_without_self_close(self):
            html = render(input_(type="text"))
            assert html.startswith('<input')
            assert html.endswith('>')
            assert '/>' not in html

        def test_svg_void_self_closes(self):
            # circle is void only in SVG namespace — test it inside <svg>
            html = render(svg(circle(cx="5", cy="5", r="4"), viewBox="0 0 10 10"))
            assert '<circle cx="5" cy="5" r="4" />' in html


    # ──────────────────────────────────────────────────────────────────────────
    # 6. SVG / namespace handling
    # ──────────────────────────────────────────────────────────────────────────

    class TestNamespaces:
        def test_svg_gets_xmlns(self):
            html = render(svg(viewBox="0 0 10 10"))
            assert 'xmlns="http://www.w3.org/2000/svg"' in html

        def test_svg_child_does_not_get_xmlns(self):
            html = render(svg(rect(x="0", y="0")))
            # xmlns should appear exactly once, on the svg element
            assert html.count('xmlns=') == 1

        def test_math_gets_xmlns(self):
            html = render(mk_tag('math')())
            assert 'xmlns="http://www.w3.org/1998/Math/MathML"' in html

        def test_foreign_object_switches_back_to_html(self):
            # Inside a foreignObject, <br> should not self-close (HTML rules)
            fo = mk_tag('foreignObject')
            br = mk_tag('br')
            html = render(svg(fo(br())))
            # The br inside foreignObject follows HTML void rules
            assert '<br>' in html or '<br >' in html


    # ──────────────────────────────────────────────────────────────────────────
    # 7. Raw elements (script, style)
    # ──────────────────────────────────────────────────────────────────────────

    class TestRawElements:
        def test_script_content_not_escaped(self):
            script = mk_tag('script')
            html = render(script("if (x < 1) return;"))
            # Raw content — < should stay literal
            assert 'if (x < 1) return;' in html

        def test_style_content_not_escaped(self):
            style = mk_tag('style')
            html = render(style("a > b { color: red }"))
            assert 'a > b { color: red }' in html


    # ──────────────────────────────────────────────────────────────────────────
    # 8. Safe strings
    # ──────────────────────────────────────────────────────────────────────────

    class TestSafe:
        def test_safe_string_is_not_escaped(self):
            s = Safe("<b>bold</b>")
            html = render(p(s))
            assert '<b>bold</b>' in html

        def test_plain_string_IS_escaped(self):
            html = render(p("<b>bold</b>"))
            assert '&lt;b&gt;' in html

        def test_safe_passes_html_protocol(self):
            assert Safe("x").__html__() == "x"


    # ──────────────────────────────────────────────────────────────────────────
    # 9. unpack / children flattening
    # ──────────────────────────────────────────────────────────────────────────

    class TestUnpack:
        def test_flattens_nested_lists(self):
            assert unpack([1, [2, [3, 4]], 5]) == (1, 2, 3, 4, 5)

        def test_drops_none(self):
            assert unpack([1, None, 2]) == (1, 2)

        def test_drops_false(self):
            assert unpack([1, False, 2]) == (1, 2)

        def test_preserves_zero_and_empty_string(self):
            # 0 and '' are falsy but valid content
            assert unpack([0, '', 1]) == (0, '', 1)

        def test_generator_is_flattened(self):
            assert unpack([(x for x in range(3))]) == (0, 1, 2)

        def test_list_of_children_is_flattened_by_tag(self):
            items = [li(c) for c in ("a", "b", "c")]
            html = render(ul(items))
            assert html.count('<li>') == 3

        def test_list_comprehension_as_children(self):
            html = render(ul([li(c) for c in ["red", "blue"]]))
            assert '<li>red</li>' in html
            assert '<li>blue</li>' in html


    # ──────────────────────────────────────────────────────────────────────────
    # 10. Module-level __getattr__ (arbitrary tag names)
    # ──────────────────────────────────────────────────────────────────────────

    class TestDynamicImports:
        def test_standard_tag_via_import(self):
            # div was imported at module top; smoke check
            html = render(div())
            assert '<div>' in html and '</div>' in html

        def test_arbitrary_tag_name_works(self):
            import html_tags
            my_thing = html_tags.completely_made_up_tag
            assert render(my_thing("hi")) == '<completely-made-up-tag>hi</completely-made-up-tag>'

        def test_custom_element_with_underscore(self):
            import html_tags
            assert render(html_tags.data_list("x")) == '<data-list>x</data-list>'

        def test_dunder_access_raises_attribute_error(self):
            import html_tags
            with pytest.raises(AttributeError):
                html_tags.__nonexistent_dunder__


    # ──────────────────────────────────────────────────────────────────────────
    # 11. is_tag duck-typing
    # ──────────────────────────────────────────────────────────────────────────

    class TestIsTag:
        def test_tag_is_recognized(self):
            assert is_tag(div()) is True

        def test_string_is_not_tag(self):
            assert is_tag("hello") is False

        def test_safe_is_not_tag(self):
            assert is_tag(Safe("x")) is False

        def test_none_is_not_tag(self):
            assert is_tag(None) is False

        def test_plain_function_is_not_tag(self):
            assert is_tag(lambda: None) is False


    # ──────────────────────────────────────────────────────────────────────────
    # 12. html_to_tag parser
    # ──────────────────────────────────────────────────────────────────────────

    class TestHtmlToTag:
        def test_roundtrip_simple(self):
            t = html_to_tag('<div class="x"><p>hi</p></div>')
            html = render(t)
            assert '<div class="x">' in html
            assert '<p>hi</p>' in html

        def test_parses_attributes(self):
            t = html_to_tag('<input type="text" required>')
            assert t.attrs.get("type") == "text"

        def test_multiple_top_level_returns_tuple(self):
            result = html_to_tag('<p>one</p><p>two</p>')
            assert isinstance(result, tuple)
            assert len(result) == 2


    # ──────────────────────────────────────────────────────────────────────────
    # 13. html_doc
    # ──────────────────────────────────────────────────────────────────────────

    class TestHtmlDoc:
        def test_starts_with_doctype(self):
            head = mk_tag('head')
            body = mk_tag('body')
            doc = html_doc(head(), body())
            assert doc.startswith('<!DOCTYPE html>')

        def test_includes_lang_attr(self):
            head = mk_tag('head')
            body = mk_tag('body')
            doc = html_doc(head(), body(), lang='fr')
            assert 'lang="fr"' in doc

        def test_returns_safe(self):
            head = mk_tag('head')
            body = mk_tag('body')
            doc = html_doc(head(), body())
            assert isinstance(doc, Safe)


    # ──────────────────────────────────────────────────────────────────────────
    # 14. Utility tags
    # ──────────────────────────────────────────────────────────────────────────

    class TestUtilityTags:
        def test_datastar_default_is_stable(self):
            html = render(Datastar())
            assert '@1.0.0/' in html
            assert 'type="module"' in html

        def test_datastar_custom_version(self):
            html = render(Datastar('1.0.0-beta.11'))
            assert '@1.0.0-beta.11/' in html

        def test_datastar_latest_maps_to_main(self):
            html = render(Datastar('latest'))
            assert '@main/' in html

        def test_favicon_has_data_uri(self):
            html = render(Favicon('🚀'))
            assert 'data:image/svg+xml,' in html
            assert 'rel="icon"' in html

        def test_mecss_and_pointer_render(self):
            assert 'me_css.js' in render(MeCSS())
            assert 'pointer_events.js' in render(Pointer())


    # ──────────────────────────────────────────────────────────────────────────
    # 15. Integration — realistic Datastar usage
    # ──────────────────────────────────────────────────────────────────────────

    class TestDatastarIntegration:
        def test_realistic_form(self):
            form = mk_tag('form')
            button = mk_tag('button')
            html = render(form(
                {"data-signals": "{email: '', loading: false}"},
                input_({"data-bind:email": True}, type="email"),
                button("Submit", {"data-on:click": "@post('/login')"}),
                cls="login",
            ))
            # apostrophes in values escape to &#x27;
            assert 'data-signals="{email: &#x27;&#x27;, loading: false}"' in html
            assert 'data-bind:email' in html
            assert 'data-on:click="@post(&#x27;/login&#x27;)"' in html
            assert 'class="login"' in html

        def test_full_modifier_chain(self):
            html = render(div({
                "data-on:click__window__debounce.500ms.leading": "$foo = ''",
            }))
            assert 'data-on:click__window__debounce.500ms.leading="$foo = &#x27;&#x27;"' in html


    # ──────────────────────────────────────────────────────────────────────────
    # 16. Deep & dynamic trees
    # ──────────────────────────────────────────────────────────────────────────

    class TestDeepTrees:
        def test_deep_nesting_renders(self):
            node = span("leaf")
            for i in range(50):
                node = div(cls=f"lvl-{i}")(node)
            html = render(node)
            assert html.count('<div') == 50
            assert '<span>leaf</span>' in html

        def test_data_driven_construction(self):
            data = {
                'type': 'ul',
                'children': [{'type': 'li', 'children': [f'item {i}']} for i in range(5)]
            }

            def build(d):
                if isinstance(d, str):
                    return d
                children = tuple(build(c) for c in d.get('children', []))
                import html_tags
                return getattr(html_tags, d['type'])(*children)

            html = render(build(data))
            assert html.count('<li>') == 5

    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
