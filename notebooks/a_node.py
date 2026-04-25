import marimo

__generated_with = "0.22.0"
app = marimo.App()

with app.setup:
    # node.py

    HTML  = 'html'
    SVG   = 'svg'
    MATH  = 'math'

    VALID_NS = (HTML, SVG, MATH)




@app.class_definition
class Node:
    """An immutable HTML/SVG/MathML tree node."""
    __slots__ = ('tag', 'ns', 'attrs', 'children')

    def __init__(self, tag: str, ns: str, attrs: dict, children: tuple):
        assert ns in VALID_NS,              f"ns must be one of {VALID_NS}, got {ns!r}"
        assert isinstance(attrs, dict),      "attrs must be a dict"
        assert isinstance(children, tuple),  "children must be a tuple"
        self.tag      = tag
        self.ns       = ns
        self.attrs    = attrs
        self.children = children

    def __repr__(self):
        return f"Node({self.tag!r}, ns={self.ns!r}, attrs={self.attrs!r}, children={self.children!r})"


@app.class_definition
class Safe(str):
    """Marks a string as pre-sanitized — renderer will not escape it."""


if __name__ == "__main__":
    app.run()
