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
    from html_tags import doc, render_pretty

    from html_tags.viz_scale import LinearScale, BandScale, HueScale, OrdinalHueScale
    from html_tags.viz_mark  import rect, circle, line, polyline, path, path_d, area_d, text, group
    from html_tags.viz_axis  import axis
    from html_tags.viz_chart import chart, Margin


    h = TagFactory(HTML)
    s = TagFactory(SVG)
    m = TagFactory(MATH)


@app.cell
def _():


    data   = [('A', 30), ('B', 80), ('C', 50), ('D', 65)]
    cats   = [d[0] for d in data]
    vals   = [d[1] for d in data]

    mar    = Margin(top=20, right=20, bottom=40, left=50)
    bm     = mar.bind(500, 300)

    x      = BandScale(domain=cats,    range_=(0, bm.inner_width),  padding=0.2)
    y      = LinearScale(domain=(0,100), range_=(bm.inner_height, 0))

    bars   = [rect(x=x(c), y=y(v), width=x.bandwidth, height=bm.inner_height - y(v),
                   cls='surface', style=f'--color:0.3')
              for c, v in data]

    demo_chart = chart(500, 300,
        *bars,
        axis(x, 'bottom'),
        axis(y, 'left'),
        margin=mar,
         )
    return (demo_chart,)


@app.cell
def _(demo_chart, mo):
    mo.Html(render_pretty(demo_chart))
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(demo_chart):


    def demo_html(chart_node) -> str:
        return doc(
            h.head(
                h.meta(charset='utf-8'),
                h.meta({"content": "width=device-width, initial-scale=1"}, name='viewport'),
                h.link(rel='stylesheet', href='https://cdn.jsdelivr.net/gh/Deufel/toolbox@latest/css/style.css'),
                h.title('chart demo'),
            ),
            h.body(
                h.div(
                    chart_node,
                    cls='surface p',
                    style='--space: 1; min-height: 100vh; display: flex; align-items: center; justify-content: center;',
                ),
            ),
        )

    html_str = demo_html(demo_chart)

    # write to file
    with open('/tmp/chart_demo.html', 'w') as f:
        f.write(html_str)

    print('open /tmp/chart_demo.html')
    return (html_str,)


@app.cell
def _(html_str, mo):

    mo.Html(f"""
    <iframe
        srcdoc="{html_str.replace('"', '&quot;')}"
        width="100%"
        height="400"
        style="border:none; border-radius:8px;"
    ></iframe>
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
