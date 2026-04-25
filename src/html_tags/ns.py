from .node import HTML, SVG, MATH

NS_SWITCH = {(HTML, 'svg'): SVG, (HTML, 'math'): MATH, (SVG, 'foreignObject'): HTML, (SVG, 'desc'): HTML, (SVG, 'title'): HTML, (MATH, 'annotation-xml'): HTML}

def child_ns(parent_ns: str, tag: str) -> str:
    """Return the namespace a tag's children inherit.

    Most tags inherit their parent's namespace unchanged.
    A small set of tags (svg, math, foreignObject, etc.) switch it.
    This table is the single source of truth for that switching logic.
    """
    return NS_SWITCH.get((parent_ns, tag), parent_ns)
