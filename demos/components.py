import marimo

__generated_with = "0.22.0"
app = marimo.App()

with app.setup:
    from html_tags import svg, circle, div, button, span


@app.function
def progress_ring(value, max_value=100, size=60):
    """A circular progress indicator. value in [0, max_value]."""
    radius = (size - 8) / 2
    circumference = 2 * 3.14159 * radius
    offset = circumference * (1 - value / max_value)
    return svg(viewBox=f"0 0 {size} {size}", width=size, height=size)(
        circle(cx=size/2, cy=size/2, r=radius,
               fill="none", stroke="#eee", **{"stroke-width": "4"}),
        circle(cx=size/2, cy=size/2, r=radius,
               fill="none", stroke="currentColor", **{"stroke-width": "4"},
               **{"stroke-dasharray": circumference},
               **{"stroke-dashoffset": offset},
               transform=f"rotate(-90 {size/2} {size/2})"),
    )


@app.cell
def _(mo):
    mo.Html(progress_ring(40).__html__())
    return


@app.cell
def _():
    import marimo as mo


    return (mo,)


@app.cell
def _():
    progress_ring(40).__html__()
    return


@app.function
def card(body, *, header=None, footer=None, cls="surface"):
    return div(cls=f"card {cls}")(
        header and div(cls="card-header")(header),
        div(cls="card-body")(body),
        footer and div(cls="card-footer")(footer),
    )


@app.cell
def _(mo):
    mo.Html(card("this is a card", header="Title", footer="footer").__html__())
    return


@app.cell
def _(img):
    def avatar(name, src=None, size=40):
        initials = "".join(w[0] for w in name.split()[:2]).upper()
        style = f"width:{size}px; height:{size}px; border-radius:50%;"
        if src:
            return img(src=src, alt=name, style=style)
        return div(style=style + " display:grid; place-items:center; background:#ddd;")(
            initials
        )

    return (avatar,)


@app.cell
def _(avatar, mo):
    mo.Html(avatar("MD").__html__())
    return


@app.function
def disclosure(summary_text, body_content, sig):
    """A show/hide panel. `sig` is a Datastar signal name, unique per instance."""
    return div(cls="disclosure")(
        button(
            {"data-on:click": f"${sig} = !${sig}"},
            summary_text, " ",
            span({"data-text": f"${sig} ? '▾' : '▸'"}),
        ),
        div({"data-show": f"${sig}"}, body_content),
    )


@app.cell
def _(mo):
    mo.Html(disclosure("more information...", "this is a lot more information then you thought ", "demo").__html__())
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
