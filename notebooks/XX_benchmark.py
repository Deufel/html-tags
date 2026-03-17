import marimo

__generated_with = "0.20.4"
app = marimo.App()

with app.setup:
    import timeit

    from a_core import Fragment, TagNS, attrmap, flatten, is_raw, is_void, mktag, render_attrs, tag, to_html, validate_raw


@app.cell
def _():
    t = TagNS()
    Div,B,Span,Img,A,P,H1,Ul,Li,Script,Br,Input,Form,Label,Button = t.export(
    'Div','B','Span','Img','A','P','H1','Ul','Li','Script','Br','Input','Form','Label','Button')

    return A, Div, H1, Li, P, Span, Ul, t


@app.cell
def _(A, Div, H1, Li, P, Span, Ul, t):

    simple = Div('hello world', cls='test')
    medium = Div(H1('Title'), Ul([Li(f'Item {i}') for i in range(20)]), cls='container')
    deep = Div(Div(Div(Div(Div(Span('deep'))))))
    wide = Div(*[P(f'Paragraph {i}', cls=f'p-{i}') for i in range(100)])
    page = Div(
        t.Head(t.Title('Test'), t.Meta(charset='utf-8')),
        t.Body(t.Header(H1('Hello')), t.Main(Ul([Li(A(f'Link {i}', href=f'/{i}')) for i in range(50)])),
               t.Footer(P('bye'))), cls='page')

    for name, obj in [('simple', simple), ('medium', medium), ('deep', deep), ('wide', wide), ('page', page)]:
        us = timeit.timeit(lambda: to_html(obj), number=10000) / 10000 * 1e6
        print(f'{name:8s}  {us:8.1f} µs')

    return deep, medium, page, simple, wide


@app.cell
def _(deep, medium, page, simple, wide):
    from fastcore.xml import ft, to_xml, FT

    fc_simple = ft('div', 'hello world', cls='test')
    fc_medium = ft('div', ft('h1', 'Title'), ft('ul', *[ft('li', f'Item {i}') for i in range(20)]), cls='container')
    fc_deep = ft('div', ft('div', ft('div', ft('div', ft('div', ft('span', 'deep'))))))
    fc_wide = ft('div', *[ft('p', f'Paragraph {i}', cls=f'p-{i}') for i in range(100)])
    fc_page = ft('div', ft('head', ft('title', 'Test'), ft('meta', charset='utf-8')),
        ft('body', ft('header', ft('h1', 'Hello')), ft('main', ft('ul', *[ft('li', ft('a', f'Link {i}', href=f'/{i}')) for i in range(50)])),
           ft('footer', ft('p', 'bye'))), cls='page')

    ours = [('simple',simple), ('medium',medium), ('deep',deep), ('wide',wide), ('page',page)]
    fcs  = [('simple',fc_simple), ('medium',fc_medium), ('deep',fc_deep), ('wide',fc_wide), ('page',fc_page)]

    print(f'{"case":8s}  {"html-tags":>12s}  {"fastcore":>12s}  {"ratio":>8s}')
    for (_name,o), (_,fc) in zip(ours, fcs):
        ht_us = timeit.timeit(lambda o=o: to_html(o), number=10000) / 10000 * 1e6
        fc_us = timeit.timeit(lambda fc=fc: to_xml(fc), number=10000) / 10000 * 1e6
        print(f'{_name:8s}  {ht_us:10.1f} µs  {fc_us:10.1f} µs  {ht_us/fc_us:7.2f}x')
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
