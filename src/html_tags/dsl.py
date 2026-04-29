from .node import Node, HTML, VALID_NS
from .attrs import normalize_attrs
from .ns import child_ns

TAG_ALIASES = {'input_': 'input', 'object_': 'object', 'map_': 'map', 'del_': 'del', 'ins_': 'ins'}

class TagFactory:
    """A namespace-aware factory producing Node callables.

    h  = TagFactory(HTML)   # for HTML documents
    s  = TagFactory(SVG)    # for standalone SVG fragments
    mx = TagFactory(MATH)   # for standalone MathML fragments

    Each factory only knows its own namespace. Namespace switching
    is handled by creating a new factory and passing it explicitly,
    or by using the h.svg / h.math convenience which does this for you.
    """
    __slots__ = ('_ns',)

    def __init__(self, ns: str):
        assert ns in VALID_NS, f"ns must be one of {VALID_NS}, got {ns!r}"
        self._ns = ns

    def __call__(self, tag: str):
        """For tag names not valid as Python identifiers: h('xlink:href')."""
        return _make_tag(tag, self._ns)

    def __getattr__(self, name: str):
        tag = TAG_ALIASES.get(name, name)
        return _make_tag(tag, self._ns)

    def __repr__(self):
        return f'TagFactory(ns={self._ns!r})'

def _make_tag(tag: str, ns: str):
    """Return a callable that builds Nodes for the given tag + namespace.

    The callable signature:
      tag_fn(*args, **kwargs) -> Node

    args may be:
      - Node or str or int or float   -> children
      - dict                          -> verbatim attrs (bypass normalization)
      - iterable of Node/str          -> flattened into children

    kwargs -> normalized attrs via Layer 1.

    The returned Node is immediately usable. Chained calls are supported:
      h.div(cls='card')(h.p('hello'))
    because Node.__call__ extends children (see Node in node.py).
    """
    def tag_fn(*args, **kwargs):
        children, dicts = _split_args(args)
        attrs           = normalize_attrs(*dicts, **kwargs)
        return Node(tag, ns, attrs, tuple(children))

    tag_fn.__name__ = tag
    return tag_fn

def _split_args(args: tuple) -> tuple[list, list]:
    """Separate children from verbatim attr dicts in a tag call's args.

    Returns (children, dicts).
    """
    children = []
    dicts    = []
    for arg in args:
        if isinstance(arg, dict):
            dicts.append(arg)
        elif isinstance(arg, (Node, str, int, float)):
            children.append(arg)
        elif hasattr(arg, '__node__'):          # component protocol
            children.append(arg.__node__())
        elif hasattr(arg, '__iter__'):
            for item in arg:
                if hasattr(item, '__node__'):   # comps. inside generators too
                    children.append(item.__node__())
                else:
                    children.append(item)
        else:
            children.append(arg)
    return children, dicts
