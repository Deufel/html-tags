import marimo

__generated_with = "0.22.0"
app = marimo.App()

with app.setup:
    # ns.py

    from a_node import HTML, SVG, MATH


    # Tags that switch the active namespace for all their descendants.
    # Key: (parent_ns, tag) -> child_ns
    #
    # Rules come directly from the HTML5 parsing spec:
    #   https://html.spec.whatwg.org/multipage/parsing.html#tree-construction
    #
    NS_SWITCH = {
        (HTML, 'svg'):            SVG,
        (HTML, 'math'):           MATH,
        (SVG,  'foreignObject'):  HTML,
        (SVG,  'desc'):           HTML,
        (SVG,  'title'):          HTML,
        (MATH, 'annotation-xml'): HTML,  # only when encoding="text/html" or "application/xhtml+xml"
    }


@app.function
def child_ns(parent_ns: str, tag: str) -> str:
    """Return the namespace a tag's children inherit.

    Most tags inherit their parent's namespace unchanged.
    A small set of tags (svg, math, foreignObject, etc.) switch it.
    This table is the single source of truth for that switching logic.
    """
    return NS_SWITCH.get((parent_ns, tag), parent_ns)


if __name__ == "__main__":
    app.run()
