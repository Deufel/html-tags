import marimo

__generated_with = "0.21.1"
app = marimo.App()

with app.setup:
    import timeit

    from a_core import Tag, attrmap, render_attrs, is_void, is_raw, to_html, mktag, TagNS, Fragment, flatten, validate_raw, setup_tags, pretty, dunder_getattr
    from b_sse import patch_elements, patch_signals
    from c_svg import setup_svg

    setup_tags()
    setup_svg()


@app.cell
def _(
    A,
    Body,
    Div,
    Footer,
    H1,
    Head,
    Header,
    Li,
    Main,
    Meta,
    P,
    Span,
    Title,
    Ul,
):



    def bench(fn, n=10000): return timeit.timeit(fn, number=n) / n * 1e6

    cases = dict(
        simple=lambda: to_html(Div('hello world', cls='test')),
        medium=lambda: to_html(Div(H1('Title'), Ul(*[Li(f'Item {i}') for i in range(20)]), cls='container')),
        deep=  lambda: to_html(Div(Div(Div(Div(Div(Span('deep'))))))),
        wide=  lambda: to_html(Div(*[P(f'Paragraph {i}', cls=f'p-{i}') for i in range(100)])),
        page=  lambda: to_html(Div(Head(Title('Test'), Meta(charset='utf-8')),
                   Body(Header(H1('Hello')), Main(Ul(*[Li(A(f'Link {i}', href=f'/{i}')) for i in range(50)])),
                       Footer(P('bye'))), cls='page')),
    )

    for name,fn in cases.items():
        t = bench(fn)
        rps = 1e6/t
        print(f'{name:8s}  {t:8.1f} µs  {rps:>12,.0f} renders/sec')

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Results
    > M3 Max

    ```
    v0.0.15
    simple         2.6 µs       386,277 renders/sec
    medium        35.4 µs        28,212 renders/sec
    deep           6.9 µs       144,295 renders/sec
    wide         199.1 µs         5,022 renders/sec
    page         175.5 µs         5,699 renders/sec
    ```

    ```
    (~ v0.0.7)
    simple         1.2 µs       850,569 renders/sec
    medium        24.8 µs        40,367 renders/sec
    deep           4.5 µs       223,771 renders/sec
    wide         138.7 µs         7,212 renders/sec
    page         114.3 µs         8,746 renders/sec
    ```
    """)
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
