import marimo

__generated_with = "0.22.0"
app = marimo.App()

with app.setup:
    from e_dsl import TagFactory

    h = TagFactory(HTML)
    s = TagFactory(SVG)
    m = TagFactory(MATH)


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
