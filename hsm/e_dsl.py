import marimo

__generated_with = "0.22.0"
app = marimo.App()

with app.setup:
    # dsl.py

    from a_node  import Node, HTML, VALID_NS
    from b_attrs import normalize_attrs


    TAG_ALIASES = {
        'input_':  'input',
        'object_': 'object',
        'map_':    'map',
        'del_':    'del',
        'ins_':    'ins',
    }



@app.cell
def _(internal_make_tag):
    class TagFactory:
        """Namespace-aware factory. Attribute access returns a tag callable.

        h = TagFactory(HTML)
        s = TagFactory(SVG)
        m = TagFactory(MATH)
        """
        __slots__ = ('_ns',)

        def __init__(self, ns: str):
            assert ns in VALID_NS, f"ns must be one of {VALID_NS}, got {ns!r}"
            self._ns = ns

        def __call__(self, tag: str):
            """Escape hatch for non-identifier tag names: h('my-element')."""
            return internal_make_tag(tag, self._ns)

        def __getattr__(self, name: str):
            return internal_make_tag(TAG_ALIASES.get(name, name), self._ns)

        def __repr__(self):
            return f'TagFactory(ns={self._ns!r})'

    return


@app.function
def interal_make_tag(tag: str, ns: str):
    """Return a callable that immediately produces a Node.

    Accepts positional args in any order:
      - dict          -> verbatim attrs (no key transformation)
      - Node          -> child
      - str/int/float -> child
      - iterable      -> flattened one level into children (for generators)

    And keyword args -> normalized attrs.

    All of these are equivalent ways to express the same thing:
      h.p("lorem", cls="lead")
      h.p(cls="lead", "lorem")        # SyntaxError in Python — kwargs before positional
      h.p("lorem", {"class": "lead"}) # dict for verbatim
      h.p({"class":"lead"}, "lorem")  # dict first, child last — your preferred style
    """
    def tag_fn(*args, **kwargs):
        children, dicts = internal_split_args(args)
        attrs           = normalize_attrs(*dicts, **kwargs)
        return Node(tag, ns, attrs, tuple(children))

    tag_fn.__name__ = tag
    return tag_fn


@app.function
def internal_split_args(args: tuple) -> tuple[list, list]:
    """Separate children from verbatim attr dicts.

    Rules:
      dict             -> attrs (verbatim, no transformation)
      Node             -> child
      str/int/float    -> child
      iterable         -> flattened one level (handles generators)
      anything else    -> child (stringified at render time)

    Strings are checked before the iterable branch because str is iterable
    and would otherwise be walked character by character.
    """
    children = []
    dicts    = []
    for arg in args:
        if isinstance(arg, dict):
            dicts.append(arg)
        elif isinstance(arg, (Node, str, int, float)):
            children.append(arg)
        elif hasattr(arg, '__iter__'):
            for item in arg:
                children.append(item)
        else:
            children.append(arg)
    return children, dicts


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
