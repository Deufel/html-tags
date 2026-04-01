import marimo

__generated_with = "0.21.1"
app = marimo.App()

with app.setup:
    """Public API: `from html_tags import Div, Span, to_html`."""
    import sys, types
    from a_node import Tag, Safe, Fragment, mktag, attrmap, flatten, SVG_NAMES
    from b_emit import to_html, pretty, render_attrs, html_to_tag





@app.class_definition
class SvgNs:
    """Svg constructor with lazy"""
    def __call__(self, *c, **kw): return mktag('svg')(*c, **kw)
    def __getattr__(self, name):
        if name.startswith('_'): raise AttributeError(name)
        real = SVG_NAMES.get(name[0].lower() + name[1:], name.lower())
        return mktag(real)


@app.class_definition
class ModuleClass(types.ModuleType):
    """Allows `from html_tags import Div, Span, MyCustomTag`."""
    def __getattr__(self, name):
        if name.startswith('_'): raise AttributeError(name)
        if name[0].isupper():
            return mktag(SVG_NAMES.get(name, name))
        raise AttributeError(f'module has no attribute {name!r}')


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
