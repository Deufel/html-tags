import marimo

__generated_with = "0.22.0"
app = marimo.App()

with app.setup:
    from e_dsl    import TagFactory

    HTML  = 'html'
    SVG   = 'svg'
    MATH  = 'math'

    h = TagFactory(HTML)
    s = TagFactory(SVG)
    m = TagFactory(MATH)

    def doc(*args, lang: str = 'en') -> str:
        """Render a full HTML document with DOCTYPE declaration.

        Usage:
            doc(
                h.head(h.title('My Page')),
                h.body(h.p('Hello')),
            )

        Args are the direct children of <html>. Lang defaults to 'en'.
        """
        page = h.html(*args, lang=lang)
        return '<!DOCTYPE html>\n' + render(page)

    def render_pretty(node, indent: int = 2) -> str:
        """Render with indentation for debugging. Never use in production."""
        import xml.dom.minidom
        raw = render(node)
        try:
            return xml.dom.minidom.parseString(raw).toprettyxml(indent=' ' * indent)
        except Exception:
            return raw   # fall back to raw if malformed


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
