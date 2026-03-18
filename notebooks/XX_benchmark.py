import marimo

__generated_with = "0.21.0"
app = marimo.App()

with app.setup:
    import timeit
    from html import escape
    from fastcore.xml import ft, to_xml
    import rusty_tags as rt

    from a_core import Fragment, TagNS, attrmap, flatten, is_raw, is_void, mktag, render_attrs, tag, to_html, validate_raw


@app.cell
def _():


    def bench(fn, n=10000): return timeit.timeit(fn, number=n) / n * 1e6

    cases = dict(
        simple=lambda: to_html(tag('div', 'hello world', cls='test')),
        medium=lambda: to_html(tag('div', tag('h1', 'Title'), tag('ul', *[tag('li', f'Item {i}') for i in range(20)]), cls='container')),
        deep=  lambda: to_html(tag('div', tag('div', tag('div', tag('div', tag('div', tag('span', 'deep'))))))),
        wide=  lambda: to_html(tag('div', *[tag('p', f'Paragraph {i}', cls=f'p-{i}') for i in range(100)])),
        page=  lambda: to_html(tag('div', tag('head', tag('title','Test'), tag('meta', charset='utf-8')),
                    tag('body', tag('header', tag('h1','Hello')), tag('main', tag('ul', *[tag('li', tag('a', f'Link {i}', href=f'/{i}')) for i in range(50)])),
                        tag('footer', tag('p','bye'))), cls='page')),
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
    simple         1.2 µs       850,569 renders/sec
    medium        24.8 µs        40,367 renders/sec
    deep           4.5 µs       223,771 renders/sec
    wide         138.7 µs         7,212 renders/sec
    page         114.3 µs         8,746 renders/sec
    ```

    ```
    case          html-tags       fastcore     rusty-tags
    simple           1.6 µs         4.7 µs         0.6 µs
    medium          18.9 µs        53.0 µs         7.2 µs
    deep             3.8 µs        13.1 µs         1.3 µs
    wide           110.4 µs       338.7 µs        64.3 µs
    page           102.5 µs       305.8 µs        41.3 µs
    ```
    """)
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
