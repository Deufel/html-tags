import marimo

__generated_with = "0.22.0"
app = marimo.App()

with app.setup:
    # render.py

    from a_node import Node, Safe, HTML, SVG, MATH


    # Void elements per namespace.
    # HTML void elements must render as <br> not <br/>.
    # SVG and MathML have no void elements — all empty tags self-close as <tag/>.

    HTML_VOID = frozenset({
        'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
        'link', 'meta', 'param', 'source', 'track', 'wbr',
    })

    SVG_VOID  = frozenset()
    MATH_VOID = frozenset()

    VOID = {
        HTML: HTML_VOID,
        SVG:  SVG_VOID,
        MATH: MATH_VOID,
    }


    # Character escaping tables.

    TEXT_ESC = str.maketrans({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
    })

    ATTR_ESC = str.maketrans({
        '&':  '&amp;',
        '"':  '&quot;',
        '<':  '&lt;',
        '>':  '&gt;',
        "'":  '&#x27;',
    })

    NS_URI = {
        SVG:  'http://www.w3.org/2000/svg',
        MATH: 'http://www.w3.org/1998/Math/MathML',
    }

    # Tags that declare their namespace via xmlns when at a boundary
    NS_ROOT_TAGS = {
        SVG:  'svg',
        MATH: 'math',
    }


@app.function
def internal_escape_text(s: str) -> str:
    return s.translate(TEXT_ESC)


@app.function
def internal_escape_attr(s: str) -> str:
    return s.translate(ATTR_ESC)


@app.function
def internal_render_attrs(attrs: dict) -> str:
    if not attrs:
        return ''
    parts = []
    for k, v in attrs.items():
        if v is True:
            parts.append(k)
        else:
            parts.append(f'{k}="{internal_escape_attr(str(v))}"')
    return ' ' + ' '.join(parts)


@app.function
def internal_render_node(node: Node, parts: list, parent_ns: str = HTML) -> None:
    """Recursively render a node tree into a flat list of strings.

    Accumulating into a list and joining once at the end is significantly
    faster than string concatenation in a recursive function.
    """

    is_void = node.tag in VOID[node.ns]

    # Inject xmlns when crossing into a new namespace at the boundary tag.
    # e.g. <svg> inside HTML gets xmlns, <circle> inside SVG does not.
    attrs = node.attrs
    if node.ns != HTML and node.ns != parent_ns and node.tag == NS_ROOT_TAGS.get(node.ns):
        attrs = {**attrs, 'xmlns': NS_URI[node.ns]}

    parts.append(f'<{node.tag}{internal_render_attrs(attrs)}')

    if is_void:
        parts.append('>')
        return

    if not node.children:
        if node.ns == HTML:
            parts.append(f'></{node.tag}>')
        else:
            parts.append('/>')
        return

    parts.append('>')

    for child in node.children:
        if isinstance(child, Safe):
            parts.append(child)
        elif isinstance(child, str):
            parts.append(internal_escape_text(child))
        elif isinstance(child, Node):
            internal_render_node(child, parts, parent_ns=node.ns)  # pass current ns down
        else:
            parts.append(internal_escape_text(str(child)))

    parts.append(f'</{node.tag}>')


@app.function
def render(node: Node | str) -> str:
    """Render a Node tree to an HTML/SVG/MathML string."""
    if isinstance(node, Safe):
        return node
    if isinstance(node, str):
        return _escape_text(node)
    parts = []
    internal_render_node(node, parts)
    return ''.join(parts)


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
