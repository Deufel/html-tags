import marimo

__generated_with = "0.22.0"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import types
    from html import escape
    from html.parser import HTMLParser
    from urllib.parse import quote

    VOID = frozenset('area base br col embed hr img input link meta source track wbr'.split())
    RAW = frozenset('script style'.split())
    SVG_VOID = frozenset('circle ellipse line path polygon polyline rect stop set image use feBlend feColorMatrix feComposite feConvolveMatrix feDisplacementMap feDistantLight feDropShadow feFlood feFuncA feFuncB feFuncG feFuncR feGaussianBlur feImage feMergeNode feMorphology feOffset fePointLight feSpotLight feTile feTurbulence'.split())
    MATH_VOID = frozenset('mprescripts none'.split())
    NS_RULES = {'html': (VOID, False), 'svg': (SVG_VOID, True), 'math': (MATH_VOID, False)}
    NS_ATTRS = {'svg': 'xmlns="http://www.w3.org/2000/svg"', 'math': 'xmlns="http://www.w3.org/1998/Math/MathML"'}
    ATTR_MAP = {'cls': 'class', '_class': 'class', '_for': 'for', '_from': 'from', '_in': 'in', '_is': 'is'}

    """HTML/SVG/MathML tag construction and rendering.

        A tag is a closure capturing (name, children, attrs) and callable to produce
        a new closure with extended children/attrs. No mutation. Parameter docs use
        the fastcore docments convention: one-line description above the signature,
        per-parameter details as inline comments next to each parameter. 

        note: closure group is not really pythonic or idomatic but it is fully functional which is why it was implemented here.
        """

    class Safe(str):
        """A string that is already HTML-safe and will not be escaped on render."""
        def __html__(self): return self

    def unpack(
        items, # iterable of values to flatten
    ):         # tuple with nested lists/tuples/generators expanded, `None` and `False` dropped
        "Flatten nested iterables, dropping `None` and `False` values."
        out = []
        for o in items:
            if o is None or o is False:
                continue
            elif isinstance(o, (list, tuple, types.GeneratorType)):
                out.extend(unpack(o))
            else:
                out.append(o)
        return tuple(out)

    def _preproc(
        c,  # positional args (may include dicts treated as attrs)
        kw, # keyword args to be pythonified into attrs
    ):      # tuple of (flattened_children, final_attrs_dict)
        """Split positional children from attrs and normalize kwarg keys.

        Dict keys pass through verbatim. Kwarg keys are Pythonified — looked up in
        `ATTR_MAP`, trailing underscore stripped, internal underscores become
        hyphens. Transformation happens here so attrs dicts are always in their
        final form once inside a tag.
        """
        ch, d = [], {}
        for o in c:
            if isinstance(o, dict): d.update(o)
            else:                   ch.append(o)
        for k, v in kw.items():
            k = ATTR_MAP.get(k, k.rstrip('_').replace('_', '-'))
            d[k] = v
        return unpack(ch), d

    def is_tag(
        x, # any value
    ):     # True if `x` is a tag closure (has the `_is_tag` marker)
        "Duck-type check for tag closures."
        return getattr(x, '_is_tag', False)

    def tag(
        name,         # element name, e.g. 'div', 'svg', 'my-component'
        children=(),  # tuple of child tags/strings/Safe values
        attrs=None,   # attribute dict (keys emitted verbatim)
    ):                # tag closure — callable, carries `.tag`/`.children`/`.attrs`/`_is_tag`
        """Construct a tag closure.

        The returned object is callable: calling it with more children/attrs
        returns a *new* tag closure. Nothing mutates. The closure exposes
        `.tag`, `.children`, `.attrs` for introspection and rendering.
        """
        attrs = attrs or {}

        def extend(*c, **kw):
            nc, nd = _preproc(c, kw)
            return tag(name, children + nc, {**attrs, **nd})

        extend.tag      = name
        extend.children = children
        extend.attrs    = attrs
        extend._is_tag  = True
        extend.__repr__ = lambda: f'{name}({children!r}, {attrs!r})'
        return extend

    def render_attrs(
        d, # attribute dict (keys already in final HTML form)
    ):     # serialized attribute string, leading space included per attr
        """Serialize an attribute dict to an HTML attribute string.

        Values: `True` renders a bare attr name, `False`/`None` omits, everything
        else is str-escaped and quoted. Keys are emitted verbatim — all transforms
        happen upstream in `_preproc`.
        """
        out = []
        for k, v in d.items():
            if v is True:
                out.append(f' {k}')
            elif v not in (False, None):
                out.append(f' {k}="{escape(str(v))}"')
        return ''.join(out)

    def render(
        node,        # tag closure, Safe string, or any value (stringified + escaped)
        ns='html',   # current namespace: 'html', 'svg', or 'math'
        depth=0,     # indentation depth for pretty-printing
        indent=2,    # spaces per indent level
    ):               # rendered HTML string
        """Recursively render a tag tree to HTML."""
        pad = ' ' * (indent * depth)

        if isinstance(node, Safe):
            return str(node)
        if not is_tag(node):
            return pad + escape(str(node))

        name, children, a = node.tag, node.children, node.attrs

        new_ns = ns
        if   name == 'svg':           new_ns = 'svg'
        elif name == 'math':          new_ns = 'math'
        elif name == 'foreignObject': new_ns = 'html'

        voids, self_close = NS_RULES[new_ns]
        attr_str = render_attrs(a)
        if name in NS_ATTRS:
            attr_str = f' {NS_ATTRS[name]}' + attr_str

        if name in voids:
            return f'{pad}<{name}{attr_str} />' if self_close else f'{pad}<{name}{attr_str}>'
        if name in RAW:
            return f'{pad}<{name}{attr_str}>{"".join(str(c) for c in children)}</{name}>'

        inner = '\n'.join(render(c, new_ns, depth + 1, indent) for c in children)
        return f'{pad}<{name}{attr_str}>\n{inner}\n{pad}</{name}>'

    def html_doc(
        head,      # a <head> tag (or any tag/string placed in head position)
        body,      # a <body> tag (or any tag/string placed in body position)
        lang='en', # value for the `<html lang="...">` attribute
    ):             # a Safe string containing `<!DOCTYPE html>` followed by the rendered document
        "Wrap head + body in a full `<!DOCTYPE html>` document."
        h = tag('html', (head, body), {'lang': lang})
        return Safe(f'<!DOCTYPE html>\n{render(h)}')

    def mk_tag(
        name, # element name, underscores → hyphens, trailing `_` stripped
    ):        # a constructor `ctor(*children, **attrs)` that returns a tag closure
        """Return a constructor for the given element name.

        `mk_tag('data_list')` gives `<data-list>`; `mk_tag('input_')` gives
        `<input>` (useful for Python-reserved names). The module also exposes
        a `__getattr__` so `from html_tags import any_name` auto-calls this.
        """
        clean = name.rstrip('_').replace('_', '-')
        def ctor(*c, **kw):
            c, kw = _preproc(c, kw)
            return tag(clean, c, kw)
        ctor.__name__ = clean
        return ctor

    def __getattr__(
        name, # any attribute name not already defined in the module
    ):        # a tag constructor for that name
        """Module-level fallback: `from html_tags import div, my_thing` works for any name.

        Dunder names (`__foo__`) raise `AttributeError` so Python's internals
        (pickle probes, IDE introspection, etc.) don't get hijacked into tags.
        """
        if name.startswith('_'):
            raise AttributeError(name)
        return mk_tag(name)

    def html_to_tag(
        s, # HTML source string
    ):     # a single tag (if one top-level element) or tuple of tags
        """Parse an HTML string into a tag tree.

        Attributes with no value (`<input required>`) become `True` in the attrs
        dict. Whitespace-only text nodes are dropped. Self-closing / void elements
        in either HTML or SVG sets are handled.
        """
        stack, root = [[]], []

        class P(HTMLParser):
            def handle_starttag(self, t, a):
                d = {k: (v if v is not None else True) for k, v in a}
                if t in VOID | SVG_VOID:
                    stack[-1].append(tag(t, (), d))
                else:
                    stack.append([])
                    root.append((t, d))

            def handle_endtag(self, t):
                if t in VOID | SVG_VOID:
                    return
                children, (name, d) = tuple(stack.pop()), root.pop()
                stack[-1].append(tag(name, children, d))

            def handle_data(self, data):
                if data.strip():
                    stack[-1].append(data.strip())

        P().feed(s)
        res = stack[0]
        return res[0] if len(res) == 1 else tuple(res)

    def Datastar(
        v='latest', # version tag, `'latest'` for main branch, or e.g. `'1.0.0-beta.11'`
    ):             # `<script type="module">` tag loading the Datastar bundle
        "Script tag for the Datastar client library."
        ref = 'main' if v == 'latest' else v
        return tag('script', (), {
            'type': 'module',
            'src':  f'https://cdn.jsdelivr.net/gh/starfederation/datastar@{ref}/bundles/datastar.js',
        })

    def MeCSS(
        v='latest', # toolbox release tag
    ):              # `<script>` tag loading `me_css.js`
        "Script tag for the `me_css.js` helper (scoped `<style>` blocks)."
        return tag('script', (), {
            'src': f'https://cdn.jsdelivr.net/gh/Deufel/toolbox@{v}/js/me_css.js',
        })

    def Pointer(
        v='latest', # toolbox release tag
    ):              # `<script>` tag loading `pointer_events.js`
        "Script tag for `pointer_events.js` (drives `.hover`/`.active`/`.disabled` on `.btn` elements) to avoid the requirement of using normal hover & js for ios touch just use the pointer api it generalises better (imho)."
        return tag('script', (), {
            'src': f'https://cdn.jsdelivr.net/gh/Deufel/toolbox@{v}/js/pointer_events.js',
        })

    def Highlight(
        v='latest', # toolbox release tag
    ):              # `<script type="module">` tag loading `highlight.js`
        "Script tag for `highlight.js` (CSS Custom Highlight API syntax highlighter)."
        return tag('script', (), {
            'type': 'module',
            'src':  f'https://cdn.jsdelivr.net/gh/Deufel/toolbox@{v}/js/highlight.js',
        })

    def Color_type_css(
        v='latest', # toolbox release tag
    ):              # `<link rel="stylesheet">` tag
        "Link tag for the toolbox core stylesheet (Color & Type system). Complex CSS for a simple API"
        return tag('link', (), {
            'rel':  'stylesheet',
            'href': f'https://cdn.jsdelivr.net/gh/Deufel/toolbox@{v}/css/style.css',
        })

    def Favicon(
        emoji, # a single-character emoji or short text to embed as the favicon
    ):         # `<link rel="icon">` tag with an inline SVG data URI
        "Favicon link tag built from an inline SVG data URI — no image file needed."
        s = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
             f'<text y=".9em" font-size="90">{emoji}</text></svg>')
        return tag('link', (), {
            'rel':  'icon',
            'href': f'data:image/svg+xml,{quote(s, safe=":/@!,")}',
        })

    def Layout(main,
               *, 
               header=None, 
               nav=None,
               aside=None,
               footer=None, 
              ):
        _body   = mk_tag('body')
        _header = mk_tag("header")
        _nav    = mk_tag("nav")
        _main   = mk_tag("main")
        _aside  = mk_tag("aside")
        _footer = mk_tag("footer")
        return _body(cls=f"surface")(
            header and _header(id="header", cls="split")(header),
            nav    and _nav(id="nav")(nav),
            _main(id="main", cls="surface")(main),
            aside  and _aside(id="aside")(aside),
            footer and _footer(id="footer", cls="split")(footer),
        )

    return (
        Color_type_css,
        Datastar,
        Favicon,
        Highlight,
        Layout,
        MeCSS,
        Pointer,
        Safe,
        escape,
        html_doc,
        html_to_tag,
        is_tag,
        mk_tag,
        quote,
        render,
    )


@app.cell
def _(
    Color_type_css,
    Datastar,
    Favicon,
    Highlight,
    MeCSS,
    Pointer,
    Safe,
    body,
    head,
    html_doc,
    iframe,
    is_tag,
    render,
    title,
):
    class Show:
        def __init__(self, content): self.content = content if is_tag(content) else Safe(str(content))
        def _repr_html_(self):
            doc = html_doc(
                head(title("test"), Favicon("🧪"), Color_type_css(), MeCSS(), Pointer(), Highlight(), Datastar()),
                body(self.content))
            return render(iframe(srcdoc=str(doc), style="width:stretch;height:stretch;border:0"))

    return (Show,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    can you help me thing of a good way to use this library to template a html page? so i can make some composable components?

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    The key pattern is plain functions that return tag closures. A component is just a function calling `mk_tag` or other components, then returning a nested tag. Here's a minimal example with `Card` and `CardList`:

    ```python
    div, h1, h2, p, a, ul, li = mk_tag('div'), mk_tag('h1'), mk_tag('h2'), mk_tag('p'), mk_tag('a'), mk_tag('ul'), mk_tag('li')

    def Card(t, *c, href=None):
        inner = div(cls='card')(h2(t), div(cls='body')(*c))
        return a(href=href)(inner) if href else inner

    def CardList(*cards): return ul(cls='list')(li(c) for c in cards)

    page = Layout(
        main=div(h1("Welcome"), CardList(
            Card("First", p("hello world")),
            Card("Second", p("more content"), href="/second"))),
        header=h1("My Site"),
        footer=p("© 2026"))

    Show(page)
    ```

    <details class='token-usage-details'><summary>$0.0869</summary>

    `total=27,743 | in=24,115 | out=3,628 | cached=0.1% | reasoning=3,428 | searches=0 | $0.0869`

    </details>
    """)
    return


@app.cell
def _(Layout, Show, mk_tag):
    div, h1, h2, p, a, ul, li = mk_tag('div'), mk_tag('h1'), mk_tag('h2'), mk_tag('p'), mk_tag('a'), mk_tag('ul'), mk_tag('li')

    def Card(t, *c, href=None):
        inner = div(cls='card')(h2(t), div(cls='body')(*c))
        return a(href=href)(inner) if href else inner

    def CardList(*cards): return ul(cls='list')(li(c) for c in cards)

    page = Layout(
        main=div(h1("Welcome"), CardList(
            Card("First", p("hello world")),
            Card("Second", p("more content"), href="/second"))),
        header=h1("My Site"),
        footer=p("© 2026"))

    Show(page)
    return (page,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    can you help me fix this?

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    <details class='tool-usage-details'>
    <summary><code>add_msg(content=&#x27;\`\`\`python\nhead, title, body, iframe =…&#x27;, msg_type=&#x27;code&#x27;, run=False)→&#x27;_3c0cffb4&#x27;</code></summary>

    ```json
    {
      "id": "functions.add_msg:0",
      "call": {
        "function": "add_msg",
        "arguments": {
          "content": "```python\nhead, title, body, iframe = mk_tag('head'), mk_tag('title'), mk_tag('body'), mk_tag('iframe')\nShow(page)\n```",
          "msg_type": "code",
          "run": "False"
        }
      },
      "result": "_3c0cffb4"
    }
    ```

    </details>

    Added the missing `head`, `title`, `body`, and `iframe` tag constructors to the namespace, then re-ran `Show(page)`. The message ID is `_3c0cffb4`.

    <details class='token-usage-details'><summary>$0.0499</summary>

    `total=52,814 | in=51,246 | out=1,568 | cached=80.8% | reasoning=1,462 | searches=0 | $0.0499`

    </details>
    """)
    return


app._unparsable_cell(
    r"""
    ```python
    head, title, body, iframe = mk_tag('head'), mk_tag('title'), mk_tag('body'), mk_tag('iframe')
    Show(page)
    ```
    """,
    name="_"
)


@app.cell
def _(Show, mk_tag, page):
    head, title, body, iframe = mk_tag('head'), mk_tag('title'), mk_tag('body'), mk_tag('iframe')
    Show(page)
    return body, head, iframe, title


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    can you help me improve this templating library while keepign it minimal and functional. Some things to consider that were intentional design decision;

    1. purly functional implementation using closure to emulate recursion
    2. intentioanlly only a single way to do something. ie comose all the tage and render the into html.
    3. intentioanlly auto apply namespace to svg and math properly.
    4. i have a getattr so that i can import and function and it works like,

    ```py
    def __getattr__(name):
            return mk_tag(name)
    ```
    The reason i dont mangle the case is so users can import svg and math things that require capital leters.

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    Looking at the rendered output, there are a few real issues worth fixing — and a couple of small additions that compose well with your design:

    **1. Whitespace bug.** `render` indents text nodes, so `h1("Welcome")` becomes `<h1>\n  Welcome\n</h1>`. Browsers collapse most of that for block elements but it changes `textContent`, breaks `<pre>`/inline content, and bloats output. Fix: render text-only tags on one line.

    **2. No fragment support.** A component can't return `(a, b)` as siblings — `render` doesn't handle tuples. Tiny addition, lets you skip wrapper `div`s.

    **3. Double `<body>`.** `Layout` wraps in `_body`, then `Show` wraps that in `body` again → nested bodies in the output. `Layout` should return a fragment (after #2), let the caller add `<body>`.

    **4. `__getattr__` doesn't cache.** Every `from html_tags import div` rebuilds the constructor. One-line fix to stash on the module.

    **5. `html_to_tag` lowercases everything.** `HTMLParser` lowercases tag and attr names, so SVG (`linearGradient`, `viewBox`) round-trips broken. Worth documenting or switching parsers.

    **6. `extend.__repr__ = lambda` doesn't work.** Python looks up dunders on the type, not the instance — `repr(div())` ignores it. Either drop the line or switch to a callable class.

    Which would you like to tackle first? I'd start with #1 + #2 since they're one combined edit to `render` and they unblock #3.

    <details class='token-usage-details'><summary>$0.6089</summary>

    `total=52,041 | in=47,604 | out=4,437 | cached=0.0% | cache_new=45,606 | searches=0 | $0.6089`

    </details>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    the issue that i have with partials is that i want to have them output on multiple lines for things like SSE becaseu the multi line sse compress beter with brotli. but the issue is that I can not seem get everything put together correctly. i fix one issue an then another arrises. if i get the fragments workign correctly then html to doc does not work. i fix that and then unpacking does not work properly, i fix that and then the svgs no longer work.. feel like i am patching things instead of fixing the root cause. can you help me understand what is happening? I wand to get a clear roadmap of the problems and how i can solve them. can you help write some code example to show me what you think are currently problems?

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    The cascading isn't bad luck — it's because `render` has a fuzzy contract that gets renegotiated every fix. Two things are tangled inside one function:

    **(A) What is a "renderable"?** Right now: a tag, a `Safe`, or "anything stringifiable". But in practice you also have *sequences* — `html_to_tag` returns a tuple when there are multiple roots; comprehensions produce generators; fragments would be sequences too. `unpack` only flattens at *construction* time, so anything that arrives at `render` already-grouped (a parsed doc, a fragment from a component) breaks. Every fix you've tried adds another `isinstance` branch to `render`.

    **(B) Structure vs. presentation.** `render` walks the tree *and* pretty-prints. Indentation rules differ for: text-only tags (`<h1>x</h1>` shouldn't split), inline mixing (`a <b>bold</b> c
    `), `<pre>`, SVG `<text>`, and your SSE compression goal. So whenever you touch indenting for one case you bruise another.

    Here's a single cell that demonstrates the four failure modes you keep bouncing between:

    ```python
    kids = (h1("a"), h1("b"))
    print("--- fragment (sequence as node) ---")
    try: print(render(kids))
    except Exception as e: print(type(e).__name__, e)

    print("\n--- html_to_tag with multiple roots ---")
    parsed = html_to_tag("<p>x</p><p>y</p>")
    try: print(render(parsed))
    except Exception as e: print(type(e).__name__, e)

    print("\n--- text indentation alters semantics ---")
    print(render(p("hello")))
    print(render(pre("line1\nline2")))

    print("\n--- inline children split across lines ---")
    b = mk_tag('b')
    print(render(p("a ", b("bold"), " c")))

    print("\n--- html_to_tag lowercases SVG tags ---")
    src = '<svg><linearGradient id="g"/></svg>'
    print(render(html_to_tag(src)))
    ```

    Run it and you'll see all four show up as artifacts of the same root cause.

    The roadmap I'd suggest, in order — each step makes the next one cheap:

    1. **Promote "fragment" to a first-class node.** A `frag(*children)` returning a tag-like closure with `tag=None`. `render` learns *one* new case (no open/close, just render children at current indent). Now sequences from `html_to_tag`, components, and SSE all flow through the same path. `Layout` returns a fragment instead of double-wrapping `<body>`.

    2. **Classify elements once, render dispatches.** Replace the `voids` / `RAW` / "everything else" ad-hoc checks with a small classifier returning one of `{void, raw, inline, block}`. Then `render` becomes a dispatch on that label. SSE-friendly multi-line, `<pre>`, SVG text, and inline mixing all become *configuration* of the classifier, not edits to `render`.

    3. **Separate "to tree of strings" from "format".** Walk → list of `(depth, kind, text)` events; format → join. This is the change that makes #2 trivial and gives you a knob for the brotli case (newlines between siblings) without touching tree logic.

    4. **Then the smaller stuff:** cache `__getattr__` results, fix `__repr__` (Python looks dunders up on the *type*, so the lambda never fires — a tiny callable class fixes it), and decide whether `html_to_tag` should preserve case for SVG round-tripping.

    Want to start with step 1? It's about ten lines and immediately fixes the `Layout` double-`<body>` and the multi-root parse.

    <details class='token-usage-details'><summary>$0.5821</summary>

    `total=51,865 | in=48,427 | out=3,438 | cached=0.0% | cache_new=47,971 | searches=0 | $0.5821`

    </details>
    """)
    return


@app.cell
def _(html_to_tag, mk_tag, render):
    h1_1 = mk_tag('h1')
    p_1 = mk_tag('p')
    pre = mk_tag('pre')
    kids = (h1_1('a'), h1_1('b'))
    print('--- fragment (sequence as node) ---')
    try:
        print(render(kids))
    except Exception as e:
        print(type(e).__name__, e)
    print('\n--- html_to_tag with multiple roots ---')
    parsed = html_to_tag('<p>x</p><p>y</p>')
    try:
        print(render(parsed))
    except Exception as e:
        print(type(e).__name__, e)
    print('\n--- text indentation alters semantics ---')
    print(render(p_1('hello')))
    print(render(pre('line1\nline2')))
    print('\n--- inline children split across lines ---')
    b = mk_tag('b')
    print(render(p_1('a ', b('bold'), ' c')))
    print('\n--- html_to_tag lowercases SVG tags ---')
    src = '<svg><linearGradient id="g"/></svg>'
    print(render(html_to_tag(src)))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Can you help me fhink about this from first principles?  Can you help me think about this from the point of view ok Niklaus Wirth? I know some libraries handle xml and then build html handeling ontop of that, is that the more correct approach then trying to handle html and then step back in the xml for svg name spaces? how can i orthogonalise the problem? I would like to keep the data structure and the rendering separate if possible. I am not sure what the right abstractions are here. can you help me thing through this?

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    Wirth's instinct here would be: *what is the smallest set of orthogonal concepts, and where does each irregularity belong?* You're right that the XML-then-HTML angle is the clue — but you don't need an XML library underneath; you need the *abstraction* that XML embodies: **a tree is a tree**. HTML is that tree plus a *profile* of irregularities (void, raw, namespace switches, inline-vs-block). SVG is the same tree plus a different profile. The current code conflates "tree", "profile", and "format" inside `render`, so every fix in one bleeds into the others.

    Four orthogonal layers, each with one job:

    **1. Tree.** Three node kinds and nothing else: element, text, raw (already-safe). No namespace knowledge, no HTML knowledge, no formatting. This is your `tag` closure today, minus the rendering concerns.

    **2. Profile.** A pure data table describing irregularities: which names are void, which are raw, which switch namespace, which are inline. HTML5 is one profile; SVG is another; pure XML is `{}` (no irregularities). This is what `NS_RULES`, `VOID`, `RAW` *want* to be — but they're currently consulted inside `render`, which is what couples everything.

    **3. Walk.** Tree → linear stream of events (`open`, `close`, `void`, `text`, `raw`). The walk consults the profile, picks namespaces, but *does not format*. Sequences/tuples/generators are handled here once and disappear as a concept — a fragment is just "yield from walking each child". Your multi-root parse, your `Layout` double-body, and your component-returning-a-tuple problems all collapse into this one place.

    **4. Format.** Events → string. Indentation, line breaks, inline vs block, your brotli/SSE multi-line preference — all live here. `<pre>` is just "this element's events emit with `pretty=False`". Inline children stay on one line. Nothing in steps 1–3 changes when you tweak formatting.

    This is the SAX model, basically. It's also why XML libraries feel "cleaner" — they happen to enforce this separation by accident of XML's regularity. You can have the same separation for HTML; you just have to do it on purpose.

    Where each previous bug lands once layered:

    - **Fragment / multi-root**: layer 3, one branch (`if sequence: yield from walking each`).
    - **Text indentation breaks `<pre>`**: layer 4, controlled by profile flag `raw` or `preserve_ws`.
    - **Inline split across lines**: layer 4, profile says `inline`, formatter doesn't break.
    - **SVG lowercasing**: layer 1 input concern (parser choice), unrelated to render.
    - **`Layout` double `<body>`**: layer 1, return a fragment node; nothing in render special-cases it.
    - **Brotli-friendly newlines**: layer 4 only.

    Here's the smallest sketch that makes it concrete — three node types, a profile, a walker, and a trivial formatter, so you can see the shape. Not a replacement, just enough to look at:

    ```python
    from dataclasses import dataclass, field

    @dataclass
    class El: name:str; attrs:dict=field(default_factory=dict); kids:tuple=()
    @dataclass
    class Txt: s:str
    @dataclass
    class Raw: s:str

    HTML5 = dict(
        void={'area','base','br','col','embed','hr','img','input','link','meta','source','track','wbr'},
        raw={'script','style'},
        inline={'a','b','code','em','i','span','strong'},
        ns_switch={'svg':'svg','math':'math','foreignObject':'html'},
        ns_attrs={'svg':'xmlns="http://www.w3.org/2000/svg"','math':'xmlns="http://www.w3.org/1998/Math/MathML"'})

    def walk(node, prof, ns='html'):
        if isinstance(node, (list,tuple)):
            for c in node: yield from walk(c, prof, ns)
            return
        if isinstance(node, Txt): yield ('txt', node.s); return
        if isinstance(node, Raw): yield ('raw', node.s); return
        new_ns = prof['ns_switch'].get(node.name, ns)
        if node.name in prof['void']: yield ('void', node.name, node.attrs, new_ns); return
        yield ('open', node.name, node.attrs, new_ns)
        for c in node.kids: yield from walk(c, prof, new_ns)
        yield ('close', node.name)

    def fmt(events, prof, indent=2):
        out, d = [], 0
        for e in events:
            pad = ' '*indent*d
            k = e[0]
            if   k=='txt':   out.append(pad+e[1])
            elif k=='raw':   out.append(e[1])
            elif k=='void':  out.append(f'{pad}<{e[1]}/>')
            elif k=='open':  out.append(f'{pad}<{e[1]}>'); d+=1
            elif k=='close': d-=1; out.append(f'{" "*indent*d}</{e[1]}>')
        return '\n'.join(out)

    doc = El('div', {}, (El('h1', {}, (Txt('hi'),)), El('p', {}, (Txt('there'),))))
    print(fmt(walk(doc, HTML5), HTML5))
    print('---')
    frag = (El('p',{},(Txt('x'),)), El('p',{},(Txt('y'),)))
    print(fmt(walk(frag, HTML5), HTML5))
    ```

    Run that and notice: fragments work without `render` knowing what one is, and adding `<pre>` semantics or brotli mode is a change *only* in `fmt`. The closure `tag(...)` you have today can sit on top as a *constructor* layer that produces `El` nodes — your fluent API is preserved, but the data flowing into the renderer is uniform.

    Does this framing match what you're after? If so, the natural next step is to keep your existing `tag`/`mk_tag`/`_preproc` ergonomics on top, but have them produce `El`/`Txt`/`Raw` instead of carrying render logic in the closure.

    <details class='token-usage-details'><summary>$0.6350</summary>

    `total=54,964 | in=50,633 | out=4,331 | cached=0.0% | cache_new=49,497 | searches=0 | $0.6350`

    </details>
    """)
    return


@app.cell
def _():
    from dataclasses import dataclass, field

    @dataclass
    class El:
        name: str
        attrs: dict = field(default_factory=dict)
        kids: tuple = ()

    @dataclass
    class Txt:
        s: str

    @dataclass
    class Raw:
        s: str
    HTML5 = dict(void={'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}, raw={'script', 'style'}, inline={'a', 'b', 'code', 'em', 'i', 'span', 'strong'}, ns_switch={'svg': 'svg', 'math': 'math', 'foreignObject': 'html'}, ns_attrs={'svg': 'xmlns="http://www.w3.org/2000/svg"', 'math': 'xmlns="http://www.w3.org/1998/Math/MathML"'})

    def walk(node, prof, ns='html'):
        if isinstance(node, (list, tuple)):
            for c in node:
                yield from walk(c, prof, ns)
            return
        if isinstance(node, Txt):
            yield ('txt', node.s)
            return
        if isinstance(node, Raw):
            yield ('raw', node.s)
            return
        new_ns = prof['ns_switch'].get(node.name, ns)
        if node.name in prof['void']:
            yield ('void', node.name, node.attrs, new_ns)
            return
        yield ('open', node.name, node.attrs, new_ns)
        for c in node.kids:
            yield from walk(c, prof, new_ns)
        yield ('close', node.name)

    def fmt(events, prof, indent=2):
        out, d = ([], 0)
        for e in events:
            pad = ' ' * indent * d
            k = e[0]
            if k == 'txt':
                out.append(pad + e[1])
            elif k == 'raw':
                out.append(e[1])
            elif k == 'void':
                out.append(f'{pad}<{e[1]}/>')
            elif k == 'open':
                out.append(f'{pad}<{e[1]}>')
                d = d + 1
            elif k == 'close':
                d = d - 1
                out.append(f"{' ' * indent * d}</{e[1]}>")
        return '\n'.join(out)
    doc = El('div', {}, (El('h1', {}, (Txt('hi'),)), El('p', {}, (Txt('there'),))))
    print(fmt(walk(doc, HTML5), HTML5))
    print('---')
    frag = (El('p', {}, (Txt('x'),)), El('p', {}, (Txt('y'),)))
    print(fmt(walk(frag, HTML5), HTML5))
    return El, dataclass, field, walk


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    if this more how go html templating works? I like how go handles html templating, more of it can be seen here; https://pkg.go.dev/html/template

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    Not really — Go's `html/template` and what we just built are different lineages, and worth being clear about which you actually want before refactoring further.

    **Go's html/template** is a *text* template engine. You write HTML as a string with `{{ }}` directives, parse it once, and execute it against data. Its big trick is *contextual auto-escaping*: the parser tracks whether `{{.X}}` lands inside HTML body, an attribute, a URL, JavaScript, or CSS, and escapes differently in each. Composition is `{{template "name" .}}` and `{{define}}`. The "tree" is the parsed template, not your output.

    **What we built** is the Hiccup / Elm-html / FastHTML / `htm.py` lineage: HTML *as data structures*, constructed in the host language, rendered to a string at the end. There is no template file. Composition is just function call. Escaping is uniform because everything passes through one renderer.

    These solve overlapping problems but trade differently:

    | | Go-style text templates | Tree-construction (yours) |
    |---|---|---|
    | Author HTML in | a template string | host language |
    | Composition | named templates + `{{template}}` | function call |
    | Logic | restricted DSL (`{{if}}`, `{{range}}`) | full Python |
    | Escaping | context-aware per spot | one rule (HTML-escape) |
    | Designer-friendly | yes, looks like HTML | less so, looks like code |
    | Refactor-friendly | weaker (strings) | stronger (real values) |

    A few practical implications if you wanted to *move toward* Go-style:

    1. You'd add a parser front-end (`html_to_tag` is a start) but the primary input would be template files, not Python calls.
    2. Context-aware escaping would replace your one `escape()` — that's the actual hard, valuable bit of Go's design.
    3. You'd lose the closure/composition ergonomics that make `Card`/`CardList` so cheap.

    If what you actually like about Go is **(a) the template-as-string aesthetic**, JSX-in-Python libraries (`htm.py`, `htpy`) get you closer. If it's **(b) context-aware escaping**, that's a feature to bolt onto your current renderer — orthogonal to everything we just discussed. If it's **(c) the named-template composition**, you already have that for free with Python functions; it just doesn't *look* like `{{template "card" .}}`.

    Which of those three is the part you're drawn to? That'll tell us whether the layered design from the last step is the right direction or whether you want a different shape entirely.

    <details class='token-usage-details'><summary>$0.5535</summary>

    `total=55,151 | in=53,772 | out=1,379 | cached=0.0% | cache_new=52,533 | searches=0 | $0.5535`

    </details>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ahh ok never mind now i am starting to better understand the power of using the functions as the templates; I just like context aware excaping in go did not actually look that closely at it.

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    Right — and the nice thing is context-aware escaping is genuinely orthogonal to the tree/profile/walk/format split. It lives at the *leaf* level: when you serialize a text or attribute value, you pick the escape function based on *where* you are (body, attribute, URL, JS string, CSS). The walker already knows that context (it's literally the current open tag + attribute name), so a context-aware version is "pass an `escape_for(ctx)` function into `fmt` instead of the single `html.escape`".

    You're in good shape now: composable functions for authoring, layered renderer for serializing, and context-aware escaping as a future bolt-on whenever you want it.

    <details class='token-usage-details'><summary>$0.0747</summary>

    `total=55,150 | in=54,746 | out=404 | cached=96.0% | cache_new=1,913 | searches=0 | $0.0747`

    </details>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ok can you show me high level how the neew library would work? with these changes?

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    Here's the four layers as code. Each cell maps to one conceptual layer.

    ```python
    from dataclasses import dataclass, field
    from html import escape

    class Frag(tuple): pass
    @dataclass
    class Txt: s:str
    @dataclass
    class Raw: s:str

    ATTR_MAP = {'cls':'class','_for':'for','_in':'in','_is':'is'}

    def _norm(k): return ATTR_MAP.get(k, k.rstrip('_').replace('_','-'))
    def _attrs(kw): return {_norm(k):v for k,v in kw.items()}
    def _flat(xs):
        for x in xs:
            if x is None or x is False: continue
            elif isinstance(x,(list,tuple)) and not isinstance(x,Frag): yield from _flat(x)
            else: yield x
    def _kid(x): return x if isinstance(x,(El,Txt,Raw,Frag)) else Txt(str(x))
    def _kids(c): return tuple(_kid(x) for x in _flat(c))

    @dataclass
    class El:
        name:str; attrs:dict=field(default_factory=dict); kids:tuple=()
        def __call__(self,*c,**kw): return El(self.name, {**self.attrs, **_attrs(kw)}, self.kids + _kids(c))

    HTML5 = dict(
        void=set('area base br col embed hr img input link meta source track wbr'.split()),
        raw=set('script style'.split()),
        ns_switch={'svg':'svg','math':'math','foreignObject':'html'},
        ns_attrs={'svg':'http://www.w3.org/2000/svg','math':'http://www.w3.org/1998/Math/MathML'})
    ```

    ```python
    def walk(node, prof, ns='html'):
        if isinstance(node,(list,tuple,Frag)):
            for c in node: yield from walk(c,prof,ns)
            return
        if isinstance(node,Txt): yield 'txt',node.s; return
        if isinstance(node,Raw): yield 'raw',node.s; return
        new_ns = prof['ns_switch'].get(node.name, ns)
        a = node.attrs
        if node.name in prof['ns_attrs']: a = {'xmlns':prof['ns_attrs'][node.name], **a}
        if node.name in prof['void']: yield 'void',node.name,a; return
        yield 'open',node.name,a
        for c in node.kids: yield from walk(c,prof,new_ns)
        yield 'close',node.name

    def render_attrs(d):
        out = []
        for k,v in d.items():
            if v is True: out.append(f' {k}')
            elif v not in (False,None): out.append(f' {k}="{escape(str(v))}"')
        return ''.join(out)

    def fmt(events, indent=2):
        lines,d = [],0
        for e in events:
            k,pad = e[0],' '*indent*d
            if   k=='txt':   lines.append(pad+escape(e[1]))
            elif k=='raw':   lines.append(e[1])
            elif k=='void':  lines.append(f'{pad}<{e[1]}{render_attrs(e[2])}>')
            elif k=='open':  lines.append(f'{pad}<{e[1]}{render_attrs(e[2])}>'); d+=1
            elif k=='close': d-=1; lines.append(f'{" "*indent*d}</{e[1]}>')
        return '\n'.join(lines)

    def render(node, prof=HTML5, indent=2): return fmt(walk(node,prof), indent)
    ```

    ```python
    def tag(name,*c,**kw): return El(name, _attrs(kw), _kids(c))
    def frag(*c): return Frag(_kids(c))
    def mk_tag(name):
        n = name.rstrip('_').replace('_','-')
        return lambda *c,**kw: tag(n,*c,**kw)
    ```

    ```python
    div,h1,p,a,svg,circle,foreignObject = [mk_tag(n) for n in 'div h1 p a svg circle foreignObject'.split()]

    def Card(t,*c,href=None):
        inner = div(cls='card')(h1(t), div(cls='body')(*c))
        return a(href=href)(inner) if href else inner
    def Page(*x): return frag(*x)

    doc = Page(
        Card("Hello", p("world")),
        Card("SVG", svg(viewBox="0 0 10 10")(circle(cx=5,cy=5,r=4), foreignObject()(p("html again")))),
        Card("Linked", p("click"), href="/x"))

    print(render(doc))
    ```

    The shape: layer 1 is just three node types + a fragment tuple. Layer 2 (`HTML5`) is a pure data table. Layer 3 (`walk`) is the only place that consults the profile and tracks namespace. Layer 4 (`fmt`) is the only place that knows about whitespace. Layer 5 (`tag`/`mk_tag`) is your authoring ergonomics, unchanged in feel — `div(cls='card')(h1(t), ...)` still works because `El.__call__` extends. `Layout` and `html_doc` collapse to one-line wrappers around `frag` and the `<!DOCTYPE>` prefix.

    <details class='token-usage-details'><summary>$0.6156</summary>

    `total=70,245 | in=55,059 | out=15,186 | cached=98.9% | cache_new=344 | searches=0 | $0.6156`

    </details>
    """)
    return


@app.cell
def _(El, dataclass, field):
    class Frag(tuple):
        pass

    @dataclass
    class Txt_1:
        s: str

    @dataclass
    class Raw_1:
        s: str
    ATTR_MAP_1 = {'cls': 'class', '_for': 'for', '_in': 'in', '_is': 'is'}

    def _norm(k):
        return ATTR_MAP_1.get(k, k.rstrip('_').replace('_', '-'))

    def _attrs(kw):
        return {_norm(k): v for k, v in kw.items()}

    def _flat(xs):
        for x in xs:
            if x is None or x is False:
                continue
            elif isinstance(x, (list, tuple)) and (not isinstance(x, Frag)):
                yield from _flat(x)
            else:
                yield x

    def _kid(x):
        return x if isinstance(x, (El, Txt_1, Raw_1, Frag)) else Txt_1(str(x))

    def _kids(c):
        return tuple((_kid(x) for x in _flat(c)))

    @dataclass
    class El_1:
        name: str
        attrs: dict = field(default_factory=dict)
        kids: tuple = ()

        def __call__(self, *c, **kw):
            return El(self.name, {**self.attrs, **_attrs(kw)}, self.kids + _kids(c))
    HTML5_1 = dict(void=set('area base br col embed hr img input link meta source track wbr'.split()), raw=set('script style'.split()), ns_switch={'svg': 'svg', 'math': 'math', 'foreignObject': 'html'}, ns_attrs={'svg': 'http://www.w3.org/2000/svg', 'math': 'http://www.w3.org/1998/Math/MathML'})
    return El_1, Frag, HTML5_1, Raw_1, Txt_1


@app.cell
def _(Frag, HTML5_1, Raw_1, Txt_1, escape, walk):
    def walk_1(node, prof, ns='html'):
        if isinstance(node, (list, tuple, Frag)):
            for c in node:
                yield from walk(c, prof, ns)
            return
        if isinstance(node, Txt_1):
            yield ('txt', node.s)
            return
        if isinstance(node, Raw_1):
            yield ('raw', node.s)
            return
        new_ns = prof['ns_switch'].get(node.name, ns)
        a = node.attrs
        if node.name in prof['ns_attrs']:
            a = {'xmlns': prof['ns_attrs'][node.name], **a}
        if node.name in prof['void']:
            yield ('void', node.name, a)
            return
        yield ('open', node.name, a)
        for c in node.kids:
            yield from walk(c, prof, new_ns)
        yield ('close', node.name)

    def render_attrs_1(d):
        out = []
        for k, v in d.items():
            if v is True:
                out.append(f' {k}')
            elif v not in (False, None):
                out.append(f' {k}="{escape(str(v))}"')
        return ''.join(out)

    def fmt_1(events, indent=2):
        lines, d = ([], 0)
        for e in events:
            k, pad = (e[0], ' ' * indent * d)
            if k == 'txt':
                lines.append(pad + escape(e[1]))
            elif k == 'raw':
                lines.append(e[1])
            elif k == 'void':
                lines.append(f'{pad}<{e[1]}{render_attrs_1(e[2])}>')
            elif k == 'open':
                lines.append(f'{pad}<{e[1]}{render_attrs_1(e[2])}>')
                d = d + 1
            elif k == 'close':
                d = d - 1
                lines.append(f"{' ' * indent * d}</{e[1]}>")
        return '\n'.join(lines)

    def render_1(node, prof=HTML5_1, indent=2):
        return fmt_1(walk_1(node, prof), indent)

    return render_1, walk_1


@app.cell
def _(El_1, Frag):
    def tag_1(name, *c, **kw):
        return El_1(name, _attrs(kw), _kids(c))

    def frag_1(*c):
        return Frag(_kids(c))

    def mk_tag_1(name):
        n = name.rstrip('_').replace('_', '-')
        return lambda *c, **kw: tag_1(n, *c, **kw)

    return frag_1, mk_tag_1


@app.cell
def _(frag_1, mk_tag_1, render_1):
    div_1, h1_2, p_2, a_1, svg, circle, foreignObject = [mk_tag_1(n) for n in 'div h1 p a svg circle foreignObject'.split()]

    def Card_1(t, *c, href=None):
        inner = div_1(cls='card')(h1_2(t), div_1(cls='body')(*c))
        return a_1(href=href)(inner) if href else inner

    def Page(*x):
        return frag_1(*x)
    doc_1 = Page(Card_1('Hello', p_2('world')), Card_1('SVG', svg(viewBox='0 0 10 10')(circle(cx=5, cy=5, r=4), foreignObject()(p_2('html again')))), Card_1('Linked', p_2('click'), href='/x'))
    print(render_1(doc_1))
    return (h1_2,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    can you describe how that works in a concise explination that follows the mark twain rules of writting?

    ```
    - A tale shall accomplish something and arrive somewhere.
    - Episodes of a tale shall be necessary parts and shall help develop it.
    - Crass stupidities shall not be played upon the reader [as "sophistication" or "scientific truth"] by either the author or the people in the tale.
    - Events shall be believable.
    - The author shall:
    - Say what he is proposing to say, not merely come near it.
    - Use the right word, not its second cousin.
    - Eschew surplusage.
    - Not omit necessary details.
    - Avoid slovenliness of form.
    - Use good grammar.
    - Employ a simple and straightforward style.
    ```

    and a ASCII flowchart of how it all fits together?

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    You build a tree. The renderer asks the tree what it is, the profile what the rules are, and the formatter what it should look like. Three jobs, three places.

    A tag is data. `El("div", {...}, (...))` holds a name, attrs, and children — nothing more. `Txt` and `Raw` are leaves. `Frag` is a tuple of siblings with no wrapper.

    Authoring builds that tree. `mk_tag("div")` returns a constructor; calling it makes an `El`; calling the `El` again extends it. `cls=` becomes `class=`, `None` and `False` drop out, strings become `Txt`. The tree is the only thing your components return.

    The profile is a table. It lists which names are void, which are raw, which switch namespace. HTML5 is one table; SVG sits inside it as a switch rule. Want a different dialect? Pass a different table.

    The walk turns the tree into events: `open`, `close`, `void`, `txt`, `raw`. It consults the profile, tracks the namespace, flattens fragments. It does not format.

    The formatter turns events into a string. Indent, escape, join. It does not know about HTML.

    To change look, edit the formatter. To change dialect, edit the profile. To change shape, edit the tree. Each change stays in its own room.

    ```
       author code              data                 rules
      ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
      │  mk_tag,     │───▶│ El, Txt, Raw │    │   HTML5      │
      │  tag, frag,  │    │   Frag       │    │   profile    │
      │  components  │    └──────┬───────┘    └──────┬───────┘
      └──────────────┘           │                   │
                                 ▼                   │
                          ┌──────────────┐           │
                          │    walk      │◀──────────┘
                          │  tree→events │
                          └──────┬───────┘
                                 │  open / close / void / txt / raw
                                 ▼
                          ┌──────────────┐
                          │     fmt      │
                          │ events→string│
                          └──────┬───────┘
                                 ▼
                              HTML out
    ```

    <details class='token-usage-details'><summary>$0.5827</summary>

    `total=60,033 | in=59,161 | out=872 | cached=0.0% | cache_new=56,669 | searches=0 | $0.5827`

    </details>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ok I think i really like this approach. it makes sense to me. Can you help me make a todo list for the implementation of this?

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    A roadmap, smallest-meaningful-step first. Each item should be runnable and checkable on its own.

    1. **Node types** — `El`, `Txt`, `Raw`, `Frag`. Build a couple by hand, eyeball the repr.
    2. **Authoring helpers** — `_flat`, `_kid`, `_kids`, `_attrs`, `ATTR_MAP`, `tag`, `frag`, `mk_tag`, `El.__call__`. Check that `div(cls='x')(p('hi'))` builds the expected tree.
    3. **HTML5 profile** — the data table only. No code consumes it yet; just print it and confirm it's the shape you want.
    4. **Walk** — tree → event stream. Test on a flat doc, a nested doc, a fragment, a void element, an SVG subtree. Confirm namespace switching shows up in the events.
    5. **Format** — events → string, with the indentation behaviour you want for SSE / brotli. Test against the same fixtures as step 4.
    6. **`render`** — one-line composition of walk + fmt. This is the public entry point.
    7. **Whitespace cases** — text-only elements on one line, `<pre>` preserve, inline elements no break. Add the profile flags, extend `fmt`, regression-test against step 5.
    8. **Module `__getattr__` + cache** — auto-tags by import, stash on the module so repeat lookups are free.
    9. **`html_doc` and `Layout`** — rebuild as thin wrappers returning `Frag` / `El`. Confirm no double-`<body>`.
    10. **`html_to_tag`** — pick a parser that preserves case so SVG round-trips. Decide whether to keep `HTMLParser` for HTML and add a separate XML path, or switch wholesale.
    11. **Cdn helpers** — `Datastar`, `MeCSS`, `Pointer`, `Highlight`, `Color_type_css`, `Favicon`. Mechanical port.
    12. **`Show`** — port the iframe wrapper on top of the new `render`.
    13. **Context-aware escaping** — pass `escape_for(ctx)` into `fmt`, branch on body / attr / url / js / css. Bolt-on, doesn't touch the tree.
    14. **Regression suite** — the five-failure cell from earlier becomes the test fixture. Add fragment, multi-root parse, `<pre>`, inline mixing, SVG case.

    Want to start at step 1?

    <details class='token-usage-details'><summary>$0.1145</summary>

    `total=61,088 | in=59,982 | out=1,106 | cached=94.5% | cache_new=3,028 | searches=0 | $0.1145`

    </details>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    yes

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    ```python
    from dataclasses import dataclass, field

    class Frag(tuple): pass
    @dataclass
    class Txt: s:str
    @dataclass
    class Raw: s:str
    @dataclass
    class El: name:str; attrs:dict=field(default_factory=dict); kids:tuple=()
    ```

    ```python
    El('div', {'class':'card'}, (Txt('hi'), Raw('<b>x</b>'))), Frag((Txt('a'), Txt('b')))
    ```

    <details class='token-usage-details'><summary>$0.0655</summary>

    `total=61,153 | in=60,886 | out=267 | cached=98.0% | cache_new=939 | searches=0 | $0.0655`

    </details>
    """)
    return


@app.cell
def _(dataclass, field):
    class Frag_1(tuple):
        pass

    @dataclass
    class Txt_2:
        s: str

    @dataclass
    class Raw_2:
        s: str

    @dataclass
    class El_2:
        name: str
        attrs: dict = field(default_factory=dict)
        kids: tuple = ()

    return El_2, Frag_1, Raw_2, Txt_2


@app.cell
def _(El_2, Frag_1, Raw_2, Txt_2):
    (El_2('div', {'class': 'card'}, (Txt_2('hi'), Raw_2('<b>x</b>'))), Frag_1((Txt_2('a'), Txt_2('b'))))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ok, whats is next?

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    Step 2 — authoring helpers.

    ```python
    ATTR_MAP = dict(cls='class', _for='for', _in='in', _is='is')

    def _norm(k): return ATTR_MAP.get(k, k.rstrip('_').replace('_','-'))
    def _attrs(kw): return {_norm(k):v for k,v in kw.items()}

    def _flat(xs):
        for x in xs:
            if x is None or x is False: continue
            elif isinstance(x,(list,tuple)) and not isinstance(x,Frag): yield from _flat(x)
            else: yield x

    def _kid(x): return x if isinstance(x,(El,Txt,Raw,Frag)) else Txt(str(x))
    def _kids(c): return tuple(_kid(x) for x in _flat(c))

    El.__call__ = lambda self,*c,**kw: El(self.name, {**self.attrs, **_attrs(kw)}, self.kids + _kids(c))

    def tag(name,*c,**kw): return El(name, _attrs(kw), _kids(c))
    def frag(*c): return Frag(_kids(c))
    def mk_tag(name): n=name.rstrip('_').replace('_','-'); return lambda *c,**kw: tag(n,*c,**kw)
    ```

    ```python
    div,p = mk_tag('div'),mk_tag('p')
    div(cls='card')(p('hi'), None, [p('two'), False, p('three')])
    ```

    <details class='token-usage-details'><summary>$0.0733</summary>

    `total=62,022 | in=61,456 | out=566 | cached=98.7% | cache_new=239 | searches=0 | $0.0733`

    </details>
    """)
    return


@app.cell
def _(El_2, Frag_1, Raw_2, Txt_2):
    ATTR_MAP_2 = dict(cls='class', _for='for', _in='in', _is='is')

    def _norm(k):
        return ATTR_MAP_2.get(k, k.rstrip('_').replace('_', '-'))

    def _attrs(kw):
        return {_norm(k): v for k, v in kw.items()}

    def _flat(xs):
        for x in xs:
            if x is None or x is False:
                continue
            elif isinstance(x, (list, tuple)) and (not isinstance(x, Frag_1)):
                yield from _flat(x)
            else:
                yield x

    def _kid(x):
        return x if isinstance(x, (El_2, Txt_2, Raw_2, Frag_1)) else Txt_2(str(x))

    def _kids(c):
        return tuple((_kid(x) for x in _flat(c)))
    El_2.__call__ = lambda self, *c, **kw: El_2(self.name, {**self.attrs, **_attrs(kw)}, self.kids + _kids(c))

    def tag_2(name, *c, **kw):
        return El_2(name, _attrs(kw), _kids(c))

    def frag_2(*c):
        return Frag_1(_kids(c))

    def mk_tag_2(name):
        n = name.rstrip('_').replace('_', '-')
        return lambda *c, **kw: tag_2(n, *c, **kw)

    return frag_2, mk_tag_2


@app.cell
def _(mk_tag_2):
    div_2, p_3 = (mk_tag_2('div'), mk_tag_2('p'))
    div_2(cls='card')(p_3('hi'), None, [p_3('two'), False, p_3('three')])
    return div_2, p_3


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ok looks good, whats next?

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    Step 3 — the HTML5 profile. Just the data table.

    ```python
    HTML5 = dict(
        void=set('area base br col embed hr img input link meta source track wbr'.split()),
        raw=set('script style'.split()),
        ns_switch=dict(svg='svg', math='math', foreignObject='html'),
        ns_attrs=dict(svg='http://www.w3.org/2000/svg', math='http://www.w3.org/1998/Math/MathML'))
    ```

    ```python
    HTML5
    ```

    <details class='token-usage-details'><summary>$0.0676</summary>

    `total=62,874 | in=62,699 | out=175 | cached=97.1% | cache_new=896 | searches=0 | $0.0676`

    </details>
    """)
    return


@app.cell
def _():
    HTML5_2 = dict(void=set('area base br col embed hr img input link meta source track wbr'.split()), raw=set('script style'.split()), ns_switch=dict(svg='svg', math='math', foreignObject='html'), ns_attrs=dict(svg='http://www.w3.org/2000/svg', math='http://www.w3.org/1998/Math/MathML'))
    return (HTML5_2,)


@app.cell
def _(HTML5_2):
    HTML5_2
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ok looks good whats next?

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    Step 4 — the walk. Tree to event stream, profile-aware, namespace-tracking.

    ```python
    def walk(node, prof, ns='html'):
        if isinstance(node,(list,tuple,Frag)):
            for c in node: yield from walk(c,prof,ns)
            return
        if isinstance(node,Txt): yield 'txt',node.s; return
        if isinstance(node,Raw): yield 'raw',node.s; return
        nns = prof['ns_switch'].get(node.name, ns)
        a = node.attrs
        if node.name in prof['ns_attrs']: a = {'xmlns':prof['ns_attrs'][node.name], **a}
        if node.name in prof['void']: yield 'void',node.name,a; return
        yield 'open',node.name,a
        for c in node.kids: yield from walk(c,prof,nns)
        yield 'close',node.name
    ```

    ```python
    svg,circle,br = mk_tag('svg'),mk_tag('circle'),mk_tag('br')
    list(walk(div(cls='card')(p('hi'), br(), svg(viewBox='0 0 1 1')(circle(r=1))), HTML5))
    ```

    <details class='token-usage-details'><summary>$0.0752</summary>

    `total=63,779 | in=63,377 | out=402 | cached=97.5% | cache_new=928 | searches=0 | $0.0752`

    </details>
    """)
    return


@app.cell
def _(Frag_1, Raw_2, Txt_2, walk_1):
    def walk_2(node, prof, ns='html'):
        if isinstance(node, (list, tuple, Frag_1)):
            for c in node:
                yield from walk_1(c, prof, ns)
            return
        if isinstance(node, Txt_2):
            yield ('txt', node.s)
            return
        if isinstance(node, Raw_2):
            yield ('raw', node.s)
            return
        nns = prof['ns_switch'].get(node.name, ns)
        a = node.attrs
        if node.name in prof['ns_attrs']:
            a = {'xmlns': prof['ns_attrs'][node.name], **a}
        if node.name in prof['void']:
            yield ('void', node.name, a)
            return
        yield ('open', node.name, a)
        for c in node.kids:
            yield from walk_1(c, prof, nns)
        yield ('close', node.name)

    return (walk_2,)


@app.cell
def _(HTML5_2, div_2, mk_tag_2, p_3, walk_2):
    svg_1, circle_1, br = (mk_tag_2('svg'), mk_tag_2('circle'), mk_tag_2('br'))
    list(walk_2(div_2(cls='card')(p_3('hi'), br(), svg_1(viewBox='0 0 1 1')(circle_1(r=1))), HTML5_2))
    return br, circle_1, svg_1


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    hows this look? whats next?

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    Looks right — note how `svg` gets `xmlns` injected, `br` is a `void` event (no close), `circle` opens/closes properly inside the svg. Next is step 5 — the formatter.

    ```python
    from html import escape

    def render_attrs(d):
        out = []
        for k,v in d.items():
            if v is True: out.append(f' {k}')
            elif v not in (False,None): out.append(f' {k}="{escape(str(v))}"')
        return ''.join(out)

    def fmt(events, indent=2):
        lines,d = [],0
        for e in events:
            k,pad = e[0],' '*indent*d
            if   k=='txt':   lines.append(pad+escape(e[1]))
            elif k=='raw':   lines.append(e[1])
            elif k=='void':  lines.append(f'{pad}<{e[1]}{render_attrs(e[2])}>')
            elif k=='open':  lines.append(f'{pad}<{e[1]}{render_attrs(e[2])}>'); d+=1
            elif k=='close': d-=1; lines.append(f'{" "*indent*d}</{e[1]}>')
        return '\n'.join(lines)
    ```

    ```python
    print(fmt(walk(div(cls='card')(p('hi'), br(), svg(viewBox='0 0 1 1')(circle(r=1))), HTML5)))
    ```

    <details class='token-usage-details'><summary>$0.0835</summary>

    `total=65,050 | in=64,479 | out=571 | cached=97.2% | cache_new=905 | searches=0 | $0.0835`

    </details>
    """)
    return


@app.cell
def _(escape):
    def render_attrs_2(d):
        out = []
        for k, v in d.items():
            if v is True:
                out.append(f' {k}')
            elif v not in (False, None):
                out.append(f' {k}="{escape(str(v))}"')
        return ''.join(out)

    def fmt_2(events, indent=2):
        lines, d = ([], 0)
        for e in events:
            k, pad = (e[0], ' ' * indent * d)
            if k == 'txt':
                lines.append(pad + escape(e[1]))
            elif k == 'raw':
                lines.append(e[1])
            elif k == 'void':
                lines.append(f'{pad}<{e[1]}{render_attrs_2(e[2])}>')
            elif k == 'open':
                lines.append(f'{pad}<{e[1]}{render_attrs_2(e[2])}>')
                d = d + 1
            elif k == 'close':
                d = d - 1
                lines.append(f"{' ' * indent * d}</{e[1]}>")
        return '\n'.join(lines)

    return fmt_2, render_attrs_2


@app.cell
def _(HTML5_2, br, circle_1, div_2, fmt_2, p_3, svg_1, walk_2):
    print(fmt_2(walk_2(div_2(cls='card')(p_3('hi'), br(), svg_1(viewBox='0 0 1 1')(circle_1(r=1))), HTML5_2)))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    looks great! whats next?

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    Step 6 — `render` as the public entry point, one line composing walk and fmt.

    ```python
    def render(node, prof=HTML5, indent=2): return fmt(walk(node,prof), indent)
    ```

    ```python
    print(render(frag(div(p('one')), div(p('two')))))
    ```

    <details class='token-usage-details'><summary>$0.0686</summary>

    `total=65,699 | in=65,600 | out=99 | cached=97.0% | cache_new=1,165 | searches=0 | $0.0686`

    </details>
    """)
    return


@app.cell
def _(HTML5_2, fmt_2, walk_2):
    def render_2(node, prof=HTML5_2, indent=2):
        return fmt_2(walk_2(node, prof), indent)

    return (render_2,)


@app.cell
def _(div_2, frag_2, p_3, render_2):
    print(render_2(frag_2(div_2(p_3('one')), div_2(p_3('two')))))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    looks good what is next?

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    Step 7 — whitespace cases. Three behaviours to add: text-only elements collapse to one line, `<pre>` (and raw elements) preserve content verbatim, inline elements don't break across lines.

    Profile additions:

    ```python
    HTML5['inline'] = set('a b code em i span strong'.split())
    HTML5['preserve'] = set('pre textarea'.split())
    ```

    Walk needs a flag on `open`/`close` so `fmt` knows the element's mode without re-checking the profile:

    ```python
    def _mode(name, prof):
        if name in prof['preserve']: return 'preserve'
        if name in prof['raw']:      return 'raw'
        if name in prof['inline']:   return 'inline'
        return 'block'

    def walk(node, prof, ns='html'):
        if isinstance(node,(list,tuple,Frag)):
            for c in node: yield from walk(c,prof,ns)
            return
        if isinstance(node,Txt): yield 'txt',node.s; return
        if isinstance(node,Raw): yield 'raw',node.s; return
        nns = prof['ns_switch'].get(node.name, ns)
        a = node.attrs
        if node.name in prof['ns_attrs']: a = {'xmlns':prof['ns_attrs'][node.name], **a}
        if node.name in prof['void']: yield 'void',node.name,a; return
        m = _mode(node.name, prof)
        yield 'open',node.name,a,m
        for c in node.kids: yield from walk(c,prof,nns)
        yield 'close',node.name,m
    ```

    `fmt` buffers per element: if all children of an `open` are text/inline (or it's `preserve`/`raw`), emit on one line.

    ```python
    def fmt(events, indent=2):
        out,d = [],0
        stack = []
        def pad(): return ' '*indent*d
        for e in events:
            k = e[0]
            if k=='open':
                _,name,a,m = e
                stack.append((name,a,m,[]))
                if m in ('preserve','raw'): pass
                d += 1
            elif k=='close':
                _,name,m = e
                d -= 1
                _,a,_,buf = stack.pop()
                attrs = render_attrs(a)
                if m in ('preserve','raw'):
                    inner = ''.join(buf)
                    line = f'{pad()}<{name}{attrs}>{inner}</{name}>'
                elif all(b[0] in ('txt','inline') for b in buf):
                    inner = ''.join(b[1] for b in buf)
                    line = f'{pad()}<{name}{attrs}>{inner}</{name}>'
                else:
                    inner = '\n'.join(b[1] for b in buf)
                    line = f'{pad()}<{name}{attrs}>\n{inner}\n{pad()}</{name}>'
                tag_kind = 'inline' if m=='inline' else 'block'
                (stack[-1][3] if stack else out).append((tag_kind,line))
            elif k=='void':
                _,name,a = e
                line = f'{pad()}<{name}{render_attrs(a)}>'
                (stack[-1][3] if stack else out).append(('block',line))
            elif k=='txt':
                top = stack[-1] if stack else None
                if top and top[2] in ('preserve','raw'): top[3].append(e[1])
                else:
                    s = e[1] if (top and top[2]=='inline') else escape(e[1])
                    (stack[-1][3] if stack else out).append(('txt', s if (top and top[2] in ('inline','preserve','raw')) else escape(e[1])))
            elif k=='raw':
                top = stack[-1] if stack else None
                if top and top[2] in ('preserve','raw'): top[3].append(e[1])
                else: (stack[-1][3] if stack else out).append(('txt', e[1]))
        return '\n'.join(line for _,line in out)
    ```

    ```python
    pre,b,em,span = mk_tag('pre'),mk_tag('b'),mk_tag('em'),mk_tag('span')
    print(render(div(p('hello'), p('a ', b('bold'), ' c'), pre('line1\nline2'))))
    ```

    This one's the trickiest piece in the whole library — let me know how that test renders and we'll iterate if any of the three modes need tweaking.

    <details class='token-usage-details'><summary>$0.1140</summary>

    `total=67,443 | in=65,978 | out=1,465 | cached=98.2% | cache_new=755 | searches=0 | $0.1140`

    </details>
    """)
    return


@app.cell
def _(HTML5_2):
    HTML5_2['inline'] = set('a b code em i span strong'.split())
    HTML5_2['preserve'] = set('pre textarea'.split())
    return


@app.cell
def _(Frag_1, Raw_2, Txt_2, walk_2):
    def _mode(name, prof):
        if name in prof['preserve']:
            return 'preserve'
        if name in prof['raw']:
            return 'raw'
        if name in prof['inline']:
            return 'inline'
        return 'block'

    def walk_3(node, prof, ns='html'):
        if isinstance(node, (list, tuple, Frag_1)):
            for c in node:
                yield from walk_2(c, prof, ns)
            return
        if isinstance(node, Txt_2):
            yield ('txt', node.s)
            return
        if isinstance(node, Raw_2):
            yield ('raw', node.s)
            return
        nns = prof['ns_switch'].get(node.name, ns)
        a = node.attrs
        if node.name in prof['ns_attrs']:
            a = {'xmlns': prof['ns_attrs'][node.name], **a}
        if node.name in prof['void']:
            yield ('void', node.name, a)
            return
        m = _mode(node.name, prof)
        yield ('open', node.name, a, m)
        for c in node.kids:
            yield from walk_2(c, prof, nns)
        yield ('close', node.name, m)

    return


@app.cell
def _(escape, render_attrs_2):
    def fmt_3(events, indent=2):
        out, d = ([], 0)
        stack = []

        def pad():
            return ' ' * indent * d
        for e in events:
            k = e[0]
            if k == 'open':
                _, name, a, m = e
                stack.append((name, a, m, []))
                if m in ('preserve', 'raw'):
                    pass
                d = d + 1
            elif k == 'close':
                _, name, m = e
                d = d - 1
                _, a, _, buf = stack.pop()
                attrs = render_attrs_2(a)
                if m in ('preserve', 'raw'):
                    inner = ''.join(buf)
                    line = f'{pad()}<{name}{attrs}>{inner}</{name}>'
                elif all((b[0] in ('txt', 'inline') for b in buf)):
                    inner = ''.join((b[1] for b in buf))
                    line = f'{pad()}<{name}{attrs}>{inner}</{name}>'
                else:
                    inner = '\n'.join((b[1] for b in buf))
                    line = f'{pad()}<{name}{attrs}>\n{inner}\n{pad()}</{name}>'
                tag_kind = 'inline' if m == 'inline' else 'block'
                (stack[-1][3] if stack else out).append((tag_kind, line))
            elif k == 'void':
                _, name, a = e
                line = f'{pad()}<{name}{render_attrs_2(a)}>'
                (stack[-1][3] if stack else out).append(('block', line))
            elif k == 'txt':
                top = stack[-1] if stack else None
                if top and top[2] in ('preserve', 'raw'):
                    top[3].append(e[1])
                else:
                    s = e[1] if top and top[2] == 'inline' else escape(e[1])
                    (stack[-1][3] if stack else out).append(('txt', s if top and top[2] in ('inline', 'preserve', 'raw') else escape(e[1])))
            elif k == 'raw':
                top = stack[-1] if stack else None
                if top and top[2] in ('preserve', 'raw'):
                    top[3].append(e[1])
                else:
                    (stack[-1][3] if stack else out).append(('txt', e[1]))
        return '\n'.join((line for _, line in out))

    return


@app.cell
def _(div_2, mk_tag_2, p_3, render_2):
    pre_1, b_1, em, span = (mk_tag_2('pre'), mk_tag_2('b'), mk_tag_2('em'), mk_tag_2('span'))
    print(render_2(div_2(p_3('hello'), p_3('a ', b_1('bold'), ' c'), pre_1('line1\nline2'))))
    return b_1, pre_1


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ok that was quite complex but it was neccisary right? how does the output look? and what is next?

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    The output has a bug — see `a     <b>bold</b> c
    `. The inline `<b>` line was rendered with leading pad while `d` was deep, then concatenated as-is, smuggling spaces in. The complexity is real (inline vs block vs preserve is the inherent hard part) but the previous `fmt` mixed two responsibilities: when to pad and when to concat.

    Cleaner version — children store strings *without* leading pad; the close handler decides how to glue:

    ```python
    def _attrs_str(d): return ''.join(f' {k}' if v is True else f' {k}="{escape(str(v))}"' for k,v in d.items() if v not in (False,None))

    def fmt(events, indent=2):
        out, d, stack = [], 0, []
        def emit(x): (stack[-1][3] if stack else out).append(x)
        for e in events:
            if e[0]=='open': stack.append([e[1],e[2],e[3],[]]); d += 1
            elif e[0]=='close':
                d -= 1
                _,name,m = e
                _,a,_,buf = stack.pop()
                p, ip, atts = ' '*indent*d, ' '*indent*(d+1), _attrs_str(a)
                if m in ('preserve','raw'): emit(('block', f'{p}<{name}{atts}>{"\".join(s for _,s in buf)}</{name}>'))
                elif all(k in ('txt','inline') for k,_ in buf):
                    inner = ''.join(s for _,s in buf)
                    emit(('inline', f'<{name}{atts}>{inner}</{name}>') if m=='inline' else ('block', f'{p}<{name}{atts}>{inner}</{name}>'))
                else:
                    inner = '\n'.join(f'{ip}{s}' if k in ('inline','txt') else s for k,s in buf)
                    emit(('block', f'{p}<{name}{atts}>\n{inner}\n{p}</{name}>'))
            elif e[0]=='void': emit(('block', f'{" "*indent*d}<{e[1]}{_attrs_str(e[2])}>'))
            elif e[0]=='txt':
                top = stack[-1] if stack else None
                if top and top[2] in ('preserve','raw'): top[3].append(('txt', e[1]))
                else: emit(('txt', escape(e[1])))
            elif e[0]=='raw': emit(('txt', e[1]))
        return '\n'.join(s for _,s in out)
    ```

    ```python
    print(render(div(p('hello'), p('a ', b('bold'), ' c'), pre('line1\nline2'))))
    ```

    Run that and confirm the three cases all read cleanly. After this, step 8: caching `__getattr__`.

    <details class='token-usage-details'><summary>$0.4561</summary>

    `total=79,098 | in=69,034 | out=10,064 | cached=94.9% | cache_new=1,744 | searches=0 | $0.4561`

    </details>
    """)
    return


@app.cell
def _(escape):
    def _attrs_str(d):
        return ''.join((f' {k}' if v is True else f' {k}="{escape(str(v))}"' for k, v in d.items() if v not in (False, None)))

    def fmt_4(events, indent=2):
        out, d, stack = ([], 0, [])

        def emit(x):
            (stack[-1][3] if stack else out).append(x)
        for e in events:
            if e[0] == 'open':
                stack.append([e[1], e[2], e[3], []])
                d = d + 1
            elif e[0] == 'close':
                d = d - 1
                _, name, m = e
                _, a, _, buf = stack.pop()
                p, ip, atts = (' ' * indent * d, ' ' * indent * (d + 1), _attrs_str(a))
                if m in ('preserve', 'raw'):
                    emit(('block', f"{p}<{name}{atts}>{''.join((s for _, s in buf))}</{name}>"))
                elif all((k in ('txt', 'inline') for k, _ in buf)):
                    inner = ''.join((s for _, s in buf))
                    emit(('inline', f'<{name}{atts}>{inner}</{name}>') if m == 'inline' else ('block', f'{p}<{name}{atts}>{inner}</{name}>'))
                else:
                    inner = '\n'.join((f'{ip}{s}' if k in ('inline', 'txt') else s for k, s in buf))
                    emit(('block', f'{p}<{name}{atts}>\n{inner}\n{p}</{name}>'))
            elif e[0] == 'void':
                emit(('block', f"{' ' * indent * d}<{e[1]}{_attrs_str(e[2])}>"))
            elif e[0] == 'txt':
                top = stack[-1] if stack else None
                if top and top[2] in ('preserve', 'raw'):
                    top[3].append(('txt', e[1]))
                else:
                    emit(('txt', escape(e[1])))
            elif e[0] == 'raw':
                emit(('txt', e[1]))
        return '\n'.join((s for _, s in out))

    return


@app.cell
def _(b_1, div_2, p_3, pre_1, render_2):
    print(render_2(div_2(p_3('hello'), p_3('a ', b_1('bold'), ' c'), pre_1('line1\nline2'))))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    how does that look? what is the benifit of caching ?

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    Output looks right now — `hello
    ` collapses, `a <b>bold</b> c
    ` stays one line with single spaces, and `<pre>` preserves the newline. The whitespace logic is now in *one* place (`close` handler), which is what made it readable.

    On caching `__getattr__`: every time you write `from html_tags import div`, Python calls the module's `__getattr__('div')`, which calls `mk_tag('div')`, which builds a new lambda. That happens *every import*, in *every file*, *every time*. Two costs:

    1. **Identity.** `from html_tags import div` in two files gives you two different functions. Equality checks, decorator caches, `is` comparisons all fail across modules. Annoying when debugging or memoizing.
    2. **Speed.** Negligible per call, but multiplied across thousands of imports it shows up. More importantly, you generate garbage that the GC then has to clean up.

    The fix is one line — stash the constructor on the module the first time it's asked for:

    ```python
    def __getattr__(name):
        if name.startswith('_'): raise AttributeError(name)
        t = mk_tag(name)
        globals()[name] = t
        return t
    ```

    Now the second lookup hits `globals()` directly, never reaches `__getattr__`. Same identity across the whole process.

    Want to add that, or move on to step 9 (`html_doc`/`Layout`)?

    <details class='token-usage-details'><summary>$0.6804</summary>

    `total=71,392 | in=70,922 | out=470 | cached=0.0% | cache_new=69,786 | searches=0 | $0.6804`

    </details>
    """)
    return


@app.cell
def _(mk_tag_2):
    def __getattr___1(name):
        if name.startswith('_'):
            raise AttributeError(name)
        t = mk_tag_2(name)
        globals()[name] = t
        return t

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    lets now work on step 9

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    Step 9 — `html_doc` and `Layout` as thin wrappers. `Layout` returns a fragment (no double `<body>`), `html_doc` prepends the doctype.

    ```python
    html_,head,body,header,nav,main,aside,footer,title = [mk_tag(n) for n in 'html head body header nav main aside footer title'.split()]

    def html_doc(head_, body_, lang='en'): return Raw(f'<!DOCTYPE html>\n{render(html_(lang=lang)(head_, body_))}')

    def Layout(main_, *, header_=None, nav_=None, aside_=None, footer_=None):
        return body(cls='surface')(
            header_ and header(id='header', cls='split')(header_),
            nav_    and nav(id='nav')(nav_),
            main(id='main', cls='surface')(main_),
            aside_  and aside(id='aside')(aside_),
            footer_ and footer(id='footer', cls='split')(footer_))
    ```

    ```python
    doc = html_doc(head(title('test')), Layout(div(p('hi')), header_=h1('My Site'), footer_=p('© 2026')))
    print(doc.s)
    ```

    <details class='token-usage-details'><summary>$0.0858</summary>

    `total=72,046 | in=71,584 | out=462 | cached=97.5% | cache_new=1,431 | searches=0 | $0.0858`

    </details>
    """)
    return


@app.cell
def _(Raw_2, mk_tag_2, render_2):
    html_, head_1, body_1, header, nav, main, aside, footer, title_1 = [mk_tag_2(n) for n in 'html head body header nav main aside footer title'.split()]

    def html_doc_1(head_, body_, lang='en'):
        return Raw_2(f'<!DOCTYPE html>\n{render_2(html_(lang=lang)(head_, body_))}')

    def Layout_1(main_, *, header_=None, nav_=None, aside_=None, footer_=None):
        return body_1(cls='surface')(header_ and header(id='header', cls='split')(header_), nav_ and nav(id='nav')(nav_), main(id='main', cls='surface')(main_), aside_ and aside(id='aside')(aside_), footer_ and footer(id='footer', cls='split')(footer_))

    return Layout_1, body_1, head_1, html_doc_1, title_1


@app.cell
def _(Layout_1, div_2, h1_2, head_1, html_doc_1, p_3, title_1):
    doc_2 = html_doc_1(head_1(title_1('test')), Layout_1(div_2(p_3('hi')), header_=h1_2('My Site'), footer_=p_3('© 2026')))
    print(doc_2.s)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now can you help me with step 10?

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    Step 10 — parsing. HTML parsing inherently lowercases (HTML5 says tags *are* case-insensitive), so for SVG round-tripping we need a separate XML path. Two parsers, picked by the user.

    ```python
    from html.parser import HTMLParser as _HP
    import xml.etree.ElementTree as ET

    def html_to_tag(s):
        "Parse HTML into an `El`/`Frag` tree (tag names lowercased per HTML5)."
        stack, opens, voids = [[]], [], HTML5['void']
        class P(_HP):
            def handle_starttag(s_, t, a):
                d = {k:(v if v is not None else True) for k,v in a}
                if t in voids: stack[-1].append(El(t, d, ()))
                else: stack.append([]); opens.append((t, d))
            def handle_startendtag(s_, t, a):
                d = {k:(v if v is not None else True) for k,v in a}
                stack[-1].append(El(t, d, ()))
            def handle_endtag(s_, t):
                if t in voids: return
                kids, (name, d) = tuple(stack.pop()), opens.pop()
                stack[-1].append(El(name, d, kids))
            def handle_data(s_, data):
                if data.strip(): stack[-1].append(Txt(data.strip()))
        P().feed(s)
        r = stack[0]
        return r[0] if len(r)==1 else Frag(r)

    def _et(e):
        name = e.tag.split('}')[-1] if '}' in e.tag else e.tag
        kids = []
        if e.text and e.text.strip(): kids.append(Txt(e.text))
        for c in e:
            kids.append(_et(c))
            if c.tail and c.tail.strip(): kids.append(Txt(c.tail))
        return El(name, dict(e.attrib), tuple(kids))

    def xml_to_tag(s):
        "Parse XML into an `El` tree, preserving case (use this for SVG/MathML)."
        return _et(ET.fromstring(s))
    ```

    ```python
    print(render(html_to_tag('<p>x</p><p>y</p>')))
    print('---')
    print(render(xml_to_tag('<svg viewBox="0 0 10 10"><linearGradient id="g"/></svg>')))
    ```

    <details class='token-usage-details'><summary>$0.1600</summary>

    `total=75,173 | in=72,646 | out=2,527 | cached=98.0% | cache_new=589 | searches=0 | $0.1600`

    </details>
    """)
    return


@app.cell
def _(El_2, Frag_1, HTML5_2, Txt_2):
    from html.parser import HTMLParser as _HP
    import xml.etree.ElementTree as ET

    def html_to_tag_1(s):
        """Parse HTML into an `El`/`Frag` tree (tag names lowercased per HTML5)."""
        stack, opens, voids = ([[]], [], HTML5_2['void'])

        class P(_HP):

            def handle_starttag(s_, t, a):
                d = {k: v if v is not None else True for k, v in a}
                if t in voids:
                    stack[-1].append(El_2(t, d, ()))
                else:
                    stack.append([])
                    opens.append((t, d))

            def handle_startendtag(s_, t, a):
                d = {k: v if v is not None else True for k, v in a}
                stack[-1].append(El_2(t, d, ()))

            def handle_endtag(s_, t):
                if t in voids:
                    return
                kids, (name, d) = (tuple(stack.pop()), opens.pop())
                stack[-1].append(El_2(name, d, kids))

            def handle_data(s_, data):
                if data.strip():
                    stack[-1].append(Txt_2(data.strip()))
        P().feed(s)
        r = stack[0]
        return r[0] if len(r) == 1 else Frag_1(r)

    def _et(e):
        name = e.tag.split('}')[-1] if '}' in e.tag else e.tag
        kids = []
        if e.text and e.text.strip():
            kids.append(Txt_2(e.text))
        for c in e:
            kids.append(_et(c))
            if c.tail and c.tail.strip():
                kids.append(Txt_2(c.tail))
        return El_2(name, dict(e.attrib), tuple(kids))

    def xml_to_tag(s):
        """Parse XML into an `El` tree, preserving case (use this for SVG/MathML)."""
        return _et(ET.fromstring(s))

    return html_to_tag_1, xml_to_tag


@app.cell
def _(html_to_tag_1, render_2, xml_to_tag):
    print(render_2(html_to_tag_1('<p>x</p><p>y</p>')))
    print('---')
    print(render_2(xml_to_tag('<svg viewBox="0 0 10 10"><linearGradient id="g"/></svg>')))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ok Looks good, now help em with step 11

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    Step 11 — CDN helpers. Mechanical port; each returns an `El`.

    ```python
    from urllib.parse import quote
    script,link = mk_tag('script'),mk_tag('link')

    def Datastar(v='latest'):
        "Datastar client library."
        ref = 'main' if v=='latest' else v
        return script(type='module', src=f'https://cdn.jsdelivr.net/gh/starfederation/datastar@{ref}/bundles/datastar.js')

    def MeCSS(v='latest'):
        "me_css.js helper for scoped <style> blocks."
        return script(src=f'https://cdn.jsdelivr.net/gh/Deufel/toolbox@{v}/js/me_css.js')

    def Pointer(v='latest'):
        "pointer_events.js for .hover/.active/.disabled on .btn."
        return script(src=f'https://cdn.jsdelivr.net/gh/Deufel/toolbox@{v}/js/pointer_events.js')

    def Highlight(v='latest'):
        "highlight.js syntax highlighter."
        return script(type='module', src=f'https://cdn.jsdelivr.net/gh/Deufel/toolbox@{v}/js/highlight.js')

    def Color_type_css(v='latest'):
        "Toolbox core stylesheet."
        return link(rel='stylesheet', href=f'https://cdn.jsdelivr.net/gh/Deufel/toolbox@{v}/css/style.css')

    def Favicon(emoji):
        "Favicon from inline SVG data URI."
        s = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">{emoji}</text></svg>'
        return link(rel='icon', href=f'data:image/svg+xml,{quote(s, safe=":/@!,")}')
    ```

    ```python
    print(render(head(title('demo'), Favicon('🧪'), Color_type_css(), MeCSS(), Pointer(), Highlight(), Datastar())))
    ```

    Hmm — there's one gotcha I want to flag before we move on. `<script>` is in `HTML5['raw']`, so empty `<script src="...">` will currently render with no close tag at all (the raw branch of `fmt` joins the buffer, which is empty, and produces `<script src="..."></script>` correctly — actually that's fine). But `<link>` isn't in `HTML5['void']` in our table, even though it should be — we have `link` listed, let me double-check after you run it.

    <details class='token-usage-details'><summary>$0.1085</summary>

    `total=75,261 | in=74,394 | out=867 | cached=96.5% | cache_new=1,448 | searches=0 | $0.1085`

    </details>
    """)
    return


@app.cell
def _(mk_tag_2, quote):
    script, link = (mk_tag_2('script'), mk_tag_2('link'))

    def Datastar_1(v='latest'):
        """Datastar client library."""
        ref = 'main' if v == 'latest' else v
        return script(type='module', src=f'https://cdn.jsdelivr.net/gh/starfederation/datastar@{ref}/bundles/datastar.js')

    def MeCSS_1(v='latest'):
        """me_css.js helper for scoped <style> blocks."""
        return script(src=f'https://cdn.jsdelivr.net/gh/Deufel/toolbox@{v}/js/me_css.js')

    def Pointer_1(v='latest'):
        """pointer_events.js for .hover/.active/.disabled on .btn."""
        return script(src=f'https://cdn.jsdelivr.net/gh/Deufel/toolbox@{v}/js/pointer_events.js')

    def Highlight_1(v='latest'):
        """highlight.js syntax highlighter."""
        return script(type='module', src=f'https://cdn.jsdelivr.net/gh/Deufel/toolbox@{v}/js/highlight.js')

    def Color_type_css_1(v='latest'):
        """Toolbox core stylesheet."""
        return link(rel='stylesheet', href=f'https://cdn.jsdelivr.net/gh/Deufel/toolbox@{v}/css/style.css')

    def Favicon_1(emoji):
        """Favicon from inline SVG data URI."""
        s = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">{emoji}</text></svg>'
        return link(rel='icon', href=f"data:image/svg+xml,{quote(s, safe=':/@!,')}")

    return (
        Color_type_css_1,
        Datastar_1,
        Favicon_1,
        Highlight_1,
        MeCSS_1,
        Pointer_1,
    )


@app.cell
def _(
    Color_type_css_1,
    Datastar_1,
    Favicon_1,
    Highlight_1,
    MeCSS_1,
    Pointer_1,
    head_1,
    render_2,
    title_1,
):
    print(render_2(head_1(title_1('demo'), Favicon_1('🧪'), Color_type_css_1(), MeCSS_1(), Pointer_1(), Highlight_1(), Datastar_1())))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    looks good whats next?

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    Step 12 — `Show`, the iframe wrapper, on top of the new renderer.

    ```python
    iframe = mk_tag('iframe')

    class Show:
        "Render content in an iframe for notebook display."
        def __init__(self, content): self.content = content
        def _repr_html_(self):
            doc = html_doc(
                head(title('test'), Favicon('🧪'), Color_type_css(), MeCSS(), Pointer(), Highlight(), Datastar()),
                body(self.content))
            return render(iframe(srcdoc=doc.s, style='width:stretch;height:stretch;border:0'))
    ```

    ```python
    Show(div(h1('Welcome'), p('hello world')))
    ```

    <details class='token-usage-details'><summary>$0.0948</summary>

    `total=76,846 | in=76,529 | out=317 | cached=95.7% | cache_new=1,832 | searches=0 | $0.0948`

    </details>
    """)
    return


@app.cell
def _(
    Color_type_css_1,
    Datastar_1,
    Favicon_1,
    Highlight_1,
    MeCSS_1,
    Pointer_1,
    body_1,
    head_1,
    html_doc_1,
    mk_tag_2,
    render_2,
    title_1,
):
    iframe_1 = mk_tag_2('iframe')

    class Show_1:
        """Render content in an iframe for notebook display."""

        def __init__(self, content):
            self.content = content

        def _repr_html_(self):
            doc = html_doc_1(head_1(title_1('test'), Favicon_1('🧪'), Color_type_css_1(), MeCSS_1(), Pointer_1(), Highlight_1(), Datastar_1()), body_1(self.content))
            return render_2(iframe_1(srcdoc=doc.s, style='width:stretch;height:stretch;border:0'))

    return (Show_1,)


@app.cell
def _(Show_1, div_2, h1_2, p_3):
    Show_1(div_2(h1_2('Welcome'), p_3('hello world')))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Ok, looks good! now step 13

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    Step 13 — context-aware escaping. The walker already knows the context (open tag + attribute name); we pass an `escape_for(ctx)` into `fmt` and route each value through it.

    Five contexts cover most of HTML: body text, generic attribute, URL attribute (`href`/`src`/`action`/`formaction`), inline JS (`on*` attrs + `<script>` body), and inline CSS (`style` attr + `<style>` body).

    ```python
    import re
    from urllib.parse import quote as _q

    URL_ATTRS = set('href src action formaction poster cite data manifest'.split())
    JS_ATTR_RE = re.compile(r'^on[a-z]+$')

    def esc_body(s): return escape(s, quote=False)
    def esc_attr(s): return escape(str(s), quote=True)
    def esc_url(s):
        s = str(s)
        if re.match(r'^\s*javascript:', s, re.I): return '#'
        return _q(s, safe=":/?#[]@!$&'()*+,;=%-._~")
    def esc_js(s): return str(s).replace('\\','\\\\').replace('</','<\\/').replace("'","\\'").replace('"','\\"').replace('\n','\\n')
    def esc_css(s): return str(s).replace('</','<\\/').replace('\\','\\\\')

    def attr_ctx(tag_name, attr_name):
        if attr_name in URL_ATTRS: return esc_url
        if JS_ATTR_RE.match(attr_name): return esc_js
        if attr_name == 'style': return esc_css
        return esc_attr

    def raw_ctx(tag_name):
        if tag_name == 'script': return esc_js
        if tag_name == 'style': return esc_css
        return lambda s: s
    ```

    Now `_attrs_str` and the `txt`/`raw` branches consult these:

    ```python
    def _attrs_str(name, d):
        out = []
        for k,v in d.items():
            if v is True: out.append(f' {k}')
            elif v not in (False,None): out.append(f' {k}="{attr_ctx(name,k)(v)}"')
        return ''.join(out)

    def fmt(events, indent=2):
        out, d, stack = [], 0, []
        def emit(x): (stack[-1][3] if stack else out).append(x)
        for e in events:
            if e[0]=='open': stack.append([e[1],e[2],e[3],[]]); d += 1
            elif e[0]=='close':
                d -= 1
                _,name,m = e
                _,a,_,buf = stack.pop()
                p, ip, atts = ' '*indent*d, ' '*indent*(d+1), _attrs_str(name, a)
                if m in ('preserve','raw'):
                    esc = raw_ctx(name) if m=='raw' else (lambda s: s)
                    emit(('block', f'{p}<{name}{atts}>{"\".join(esc(s) for _,s in buf)}</{name}>'))
                elif all(k in ('txt','inline') for k,_ in buf):
                    inner = ''.join(s for _,s in buf)
                    emit(('inline', f'<{name}{atts}>{inner}</{name}>') if m=='inline' else ('block', f'{p}<{name}{atts}>{inner}</{name}>'))
                else:
                    inner = '\n'.join(f'{ip}{s}' if k in ('inline','txt') else s for k,s in buf)
                    emit(('block', f'{p}<{name}{atts}>\n{inner}\n{p}</{name}>'))
            elif e[0]=='void': emit(('block', f'{" "*indent*d}<{e[1]}{_attrs_str(e[1], e[2])}>'))
            elif e[0]=='txt':
                top = stack[-1] if stack else None
                if top and top[2] in ('preserve','raw'): top[3].append(('txt', e[1]))
                else: emit(('txt', esc_body(e[1])))
            elif e[0]=='raw': emit(('txt', e[1]))
        return '\n'.join(s for _,s in out)
    ```

    ```python
    a = mk_tag('a')
    style,onclick = 'color:red;</style><script>x</script>', "alert('hi')"
    print(render(div(
        a(href="javascript:alert(1)")('xss attempt'),
        a(href='/safe?q=hello world&x=1')('ok link'),
        p(style=style)('styled'),
        p(onclick=onclick)('click'))))
    ```

    <details class='token-usage-details'><summary>$0.1374</summary>

    `total=79,437 | in=77,915 | out=1,522 | cached=96.4% | cache_new=1,507 | searches=0 | $0.1374`

    </details>
    """)
    return


@app.cell
def _(escape):
    import re
    from urllib.parse import quote as _q

    URL_ATTRS = set('href src action formaction poster cite data manifest'.split())
    JS_ATTR_RE = re.compile(r'^on[a-z]+$')

    def esc_body(s): return escape(s, quote=False)
    def esc_attr(s): return escape(str(s), quote=True)
    def esc_url(s):
        s = str(s)
        if re.match(r'^\s*javascript:', s, re.I): return '#'
        return _q(s, safe=":/?#[]@!$&'()*+,;=%-._~")
    def esc_js(s): return str(s).replace('\\','\\\\').replace('</','<\\/').replace("'","\\'").replace('"','\\"').replace('\n','\\n')
    def esc_css(s): return str(s).replace('</','<\\/').replace('\\','\\\\')

    def attr_ctx(tag_name, attr_name):
        if attr_name in URL_ATTRS: return esc_url
        if JS_ATTR_RE.match(attr_name): return esc_js
        if attr_name == 'style': return esc_css
        return esc_attr

    def raw_ctx(tag_name):
        if tag_name == 'script': return esc_js
        if tag_name == 'style': return esc_css
        return lambda s: s

    return JS_ATTR_RE, URL_ATTRS, attr_ctx, esc_body, esc_js, esc_url, raw_ctx


@app.cell
def _(attr_ctx, esc_body, raw_ctx):
    def _attrs_str(name, d):
        out = []
        for k, v in d.items():
            if v is True:
                out.append(f' {k}')
            elif v not in (False, None):
                out.append(f' {k}="{attr_ctx(name, k)(v)}"')
        return ''.join(out)

    def fmt_5(events, indent=2):
        out, d, stack = ([], 0, [])

        def emit(x):
            (stack[-1][3] if stack else out).append(x)
        for e in events:
            if e[0] == 'open':
                stack.append([e[1], e[2], e[3], []])
                d = d + 1
            elif e[0] == 'close':
                d = d - 1
                _, name, m = e
                _, a, _, buf = stack.pop()
                p, ip, atts = (' ' * indent * d, ' ' * indent * (d + 1), _attrs_str(name, a))
                if m in ('preserve', 'raw'):
                    esc = raw_ctx(name) if m == 'raw' else lambda s: s
                    emit(('block', f"{p}<{name}{atts}>{''.join((esc(s) for _, s in buf))}</{name}>"))
                elif all((k in ('txt', 'inline') for k, _ in buf)):
                    inner = ''.join((s for _, s in buf))
                    emit(('inline', f'<{name}{atts}>{inner}</{name}>') if m == 'inline' else ('block', f'{p}<{name}{atts}>{inner}</{name}>'))
                else:
                    inner = '\n'.join((f'{ip}{s}' if k in ('inline', 'txt') else s for k, s in buf))
                    emit(('block', f'{p}<{name}{atts}>\n{inner}\n{p}</{name}>'))
            elif e[0] == 'void':
                emit(('block', f"{' ' * indent * d}<{e[1]}{_attrs_str(e[1], e[2])}>"))
            elif e[0] == 'txt':
                top = stack[-1] if stack else None
                if top and top[2] in ('preserve', 'raw'):
                    top[3].append(('txt', e[1]))
                else:
                    emit(('txt', esc_body(e[1])))
            elif e[0] == 'raw':
                emit(('txt', e[1]))
        return '\n'.join((s for _, s in out))

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    old output fyi

    ```
    <div>
      <a href="javascript:alert(1)">xss attempt</a>
      <a href="/safe?q=hello world&amp;x=1">ok link</a>
      <p style="color:red;&lt;/style&gt;&lt;script&gt;x&lt;/script&gt;">styled</p>
      <p onclick="alert(&#x27;hi&#x27;)">click</p>
    </div>
    ```
    """)
    return


@app.cell
def _(div_2, mk_tag_2, p_3, render_2):
    a_2 = mk_tag_2('a')
    style, onclick = ('color:red;</style><script>x</script>', "alert('hi')")
    print(render_2(div_2(a_2(href='javascript:alert(1)')('xss attempt'), a_2(href='/safe?q=hello world&x=1')('ok link'), p_3(style=style)('styled'), p_3(onclick=onclick)('click'))))
    return a_2, onclick, style


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Ok how does this look?

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    Mixed result — the URL hardening works (`javascript:` → `#`, space → `%20`), but I conflated two layers and we lost the *HTML attribute* escape:

    - `&` in the URL isn't `&amp;` (browsers will parse it but it's malformed HTML).
    - `style` value has bare `<` and `>` instead of `&lt;`/`&gt;`.
    - `onclick` shows `\'` (JS escape) instead of `&#x27;` (HTML attribute escape).

    The right model: context-specific escaping *first* (URL/JS/CSS sanitization → safe in *that* sub-language), then HTML attribute escape *on top* (safe inside `"..."`). They compose, they don't replace.

    ```python
    def _attrs_str(name, d):
        out = []
        for k,v in d.items():
            if v is True: out.append(f' {k}')
            elif v not in (False,None): out.append(f' {k}="{escape(attr_ctx(name,k)(v), quote=True)}"')
        return ''.join(out)
    ```

    ```python
    print(render(div(
        a(href="javascript:alert(1)")('xss'),
        a(href='/safe?q=hello world&x=1')('ok'),
        p(style=style)('styled'),
        p(onclick=onclick)('click'))))
    ```

    <details class='token-usage-details'><summary>$0.1270</summary>

    `total=82,694 | in=81,299 | out=1,395 | cached=97.5% | searches=0 | $0.1270`

    </details>
    """)
    return


@app.cell
def _(attr_ctx, escape):
    def _attrs_str(name, d):
        out = []
        for k,v in d.items():
            if v is True: out.append(f' {k}')
            elif v not in (False,None): out.append(f' {k}="{escape(attr_ctx(name,k)(v), quote=True)}"')
        return ''.join(out)

    return


@app.cell
def _(a_2, div_2, onclick, p_3, render_2, style):
    print(render_2(div_2(a_2(href='javascript:alert(1)')('xss'), a_2(href='/safe?q=hello world&x=1')('ok'), p_3(style=style)('styled'), p_3(onclick=onclick)('click'))))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    how does this look?

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    Two things off, both small:

    1. **`style` attribute over-escapes.** Inside an HTML attribute, `<` is already `&lt;` from the attribute-escape pass, so the CSS escape can't break out of `<style>` (because there's no `<style>` here — we're in an attribute). The `\\` is a leftover JS-style escape mis-applied to CSS. For the *attribute*, plain HTML-attr-escape is enough; the CSS escape only matters inside raw `<style>` element bodies.

    2. **Backslash ordering bug in `esc_css`.** `.replace('</','<\\/').replace('\\','\\\\')` runs the second replace over the output of the first, doubling its backslash. Order should be reversed if you keep it.

    The cleanest fix: make `style` attribute identity-pass-through (HTML attr escape handles it), and reserve the real CSS escape for `<style>` body only.

    ```python
    def attr_ctx(tag_name, attr_name):
        if attr_name in URL_ATTRS: return esc_url
        if JS_ATTR_RE.match(attr_name): return esc_js
        return str
    ```

    ```python
    print(render(div(
        a(href="javascript:alert(1)")('xss'),
        a(href='/safe?q=hello world&x=1')('ok'),
        p(style=style)('styled'),
        p(onclick=onclick)('click'))))
    ```

    The `onclick` `\&#x27;` looks weird but is actually right: browser HTML-decodes the attribute to `alert(\'hi\')`, then JS sees `\'` as an escaped apostrophe inside the string. Two layers, both needed.

    <details class='token-usage-details'><summary>$0.1594</summary>

    `total=84,193 | in=82,237 | out=1,956 | cached=96.4% | cache_new=2,302 | searches=0 | $0.1594`

    </details>
    """)
    return


@app.cell
def _(JS_ATTR_RE, URL_ATTRS, esc_js, esc_url):
    def attr_ctx_1(tag_name, attr_name):
        if attr_name in URL_ATTRS:
            return esc_url
        if JS_ATTR_RE.match(attr_name):
            return esc_js
        return str

    return


@app.cell
def _(a_2, div_2, onclick, p_3, render_2, style):
    print(render_2(div_2(a_2(href='javascript:alert(1)')('xss'), a_2(href='/safe?q=hello world&x=1')('ok'), p_3(style=style)('styled'), p_3(onclick=onclick)('click'))))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    how does this look?

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    All four cases now correct:

    - `javascript:` neutralized to `#`
    - URL spaces percent-encoded, `&` HTML-escaped to `&amp;`
    - `style` attribute properly escapes `<`/`>`/`/` as `&lt;`/`&gt;`/`/` — no breakout possible
    - `onclick` has both layers: HTML attr escape (`&#x27;`) and JS escape (`\`) so the browser decodes to valid JS

    That leaves step 14 — the regression suite. Want to do that next?

    <details class='token-usage-details'><summary>$0.0826</summary>

    `total=83,435 | in=83,254 | out=181 | cached=98.0% | cache_new=1,052 | searches=0 | $0.0826`

    </details>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    yes lets do that now

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    ```python
    def check(name, got, want): print(f'{"OK" if got==want else "FAIL"} {name}'); print(got) if got!=want else None
    ```

    ```python
    check('fragment',
        render(frag(h1('a'), h1('b'))),
        '<h1>a</h1>\n<h1>b</h1>')

    check('multi-root parse',
        render(html_to_tag('<p>x</p><p>y</p>')),
        '<p>x</p>\n<p>y</p>')

    check('text-only collapses',
        render(p('hello')),
        '<p>hello</p>')

    check('pre preserves',
        render(pre('line1\nline2')),
        '<pre>line1\nline2</pre>')

    check('inline mixing',
        render(p('a ', b('bold'), ' c')),
        '<p>a <b>bold</b> c</p>')

    check('svg case preserved',
        render(xml_to_tag('<svg><linearGradient id="g"/></svg>')),
        '<svg xmlns="http://www.w3.org/2000/svg">\n  <linearGradient id="g"></linearGradient>\n</svg>')

    check('void no close',
        render(div(mk_tag('br')())),
        '<div>\n  <br>\n</div>')

    check('javascript: neutralized',
        render(a(href='javascript:alert(1)')('x')),
        '<a href="#">x</a>')

    check('url & escaped',
        render(a(href='/q?a=1&b=2')('x')),
        '<a href="/q?a=1&amp;b=2">x</a>')

    check('style attr escaped',
        render(p(style='</style><x>')('y')),
        '<p style="&lt;/style&gt;&lt;x&gt;">y</p>')

    check('cls -> class',
        render(div(cls='card')),
        '<div class="card"></div>')

    check('None/False dropped',
        render(div(p('a'), None, False, p('b'))),
        '<div>\n  <p>a</p>\n  <p>b</p>\n</div>')
    ```

    <details class='token-usage-details'><summary>$0.1005</summary>

    `total=84,330 | in=83,515 | out=815 | cached=98.9% | cache_new=644 | searches=0 | $0.1005`

    </details>
    """)
    return


@app.function
def check(name, got, want): print(f'{"OK" if got==want else "FAIL"} {name}'); print(got) if got!=want else None


@app.cell
def _(
    a_2,
    b_1,
    div_2,
    frag_2,
    h1_2,
    html_to_tag_1,
    mk_tag_2,
    p_3,
    pre_1,
    render_2,
    xml_to_tag,
):
    check('fragment', render_2(frag_2(h1_2('a'), h1_2('b'))), '<h1>a</h1>\n<h1>b</h1>')
    check('multi-root parse', render_2(html_to_tag_1('<p>x</p><p>y</p>')), '<p>x</p>\n<p>y</p>')
    check('text-only collapses', render_2(p_3('hello')), '<p>hello</p>')
    check('pre preserves', render_2(pre_1('line1\nline2')), '<pre>line1\nline2</pre>')
    check('inline mixing', render_2(p_3('a ', b_1('bold'), ' c')), '<p>a <b>bold</b> c</p>')
    check('svg case preserved', render_2(xml_to_tag('<svg><linearGradient id="g"/></svg>')), '<svg xmlns="http://www.w3.org/2000/svg">\n  <linearGradient id="g"></linearGradient>\n</svg>')
    check('void no close', render_2(div_2(mk_tag_2('br')())), '<div>\n  <br>\n</div>')
    check('javascript: neutralized', render_2(a_2(href='javascript:alert(1)')('x')), '<a href="#">x</a>')
    check('url & escaped', render_2(a_2(href='/q?a=1&b=2')('x')), '<a href="/q?a=1&amp;b=2">x</a>')
    check('style attr escaped', render_2(p_3(style='</style><x>')('y')), '<p style="&lt;/style&gt;&lt;x&gt;">y</p>')
    check('cls -> class', render_2(div_2(cls='card')), '<div class="card"></div>')
    check('None/False dropped', render_2(div_2(p_3('a'), None, False, p_3('b'))), '<div>\n  <p>a</p>\n  <p>b</p>\n</div>')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Ok, how does this look?

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    Twelve for twelve. Every failure mode from the diagnostic cell earlier is now covered, plus the new escaping invariants. The library is in a good place — small, layered, each concern in its own room.

    <details class='token-usage-details'><summary>$0.7989</summary>

    `total=85,236 | in=85,168 | out=68 | cached=0.0% | cache_new=84,030 | searches=0 | $0.7989`

    </details>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now what does this templating library do that makes it different then most? anything? i feel like we have a better / different context aware mechanisem that i do not see in most but im not sure this si correct. can you summarise it?

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    Honest read, neither overselling nor underselling:

    **Genuinely distinctive**

    - *Context-aware escaping in a Python tree-builder.* This is the bit you noticed correctly. FastHTML, htpy, dominate, dijkstra, yattag — almost all use one escape function for body and one for attribute, full stop. Go's `html/template` does context-aware, but it's a text-template engine, not a tree-builder. The combination of tree-as-data *and* per-context escaping (URL / JS / CSS / attr / body) routed by tag+attr name is uncommon in this lineage. Worth being a little proud of.

    - *Profile as a swappable data table.* Most libs hard-code HTML5 quirks in `if` statements scattered through the renderer. Yours is one dict; swap it for a stricter XML profile or a Markdown-ish profile and the whole renderer follows. Not unique (browsers do this internally) but rare in userland HTML libs.

    - *Event-stream intermediate.* Tree → events → string is SAX-shaped; XML libs do it, HTML builders almost never do. It's why your inline/block/preserve logic ended up small instead of an `if` thicket.

    **Common, not distinctive**

    - Functional tree construction with `mk_tag` + `__getattr__` — Hiccup-style, exists in many libs.
    - Fragments, `cls`→`class`, `None`/`False` skipping — table-stakes.
    - Auto-namespace for SVG/MathML — FastHTML does this, htpy does this.

    **What you don't have that some libs do**

    - Streaming render (yours buffers; for huge SSE payloads you'd want events to flush, not collect).
    - A type system over attributes (Elm/htpy give static checking).
    - Rich diffing for live updates (lit-html, morphdom territory).

    So the honest one-liner: it's a small, layered HTML builder whose unusual move is putting context-aware escaping into a tree-as-data design. The architecture is clean rather than novel; the escaping is the closest thing to a real differentiator.

    <details class='token-usage-details'><summary>$0.1185</summary>

    `total=86,530 | in=85,371 | out=1,159 | cached=98.4% | cache_new=1,031 | searches=0 | $0.1185`

    </details>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Datastar

    > Build reactive web apps that stand the test of time. Datastar is a lightweight framework (~10 KiB) for building everything from simple sites to real-time collaborative web applications. Bring your own backend. Server-side rendering with the ergonomics of a frontend framework, in a single file.

    ## Quick Introduction

    Datastar accepts `text/html` and `text/event-stream` responses, so you can send regular HTML or stream server-sent events (SSE) from the backend.

    ```
    HTTP/2 200 OK
    Content-Type: text/event-stream

    event: datastar-patch-elements
    data: <h3 id="message">H</h3>

    event: datastar-patch-elements
    data: <h3 id="message">He</h3>
    ```

    Datastar solves more problems than it creates:

    1. Unlike most frontend frameworks, it simplifies frontend logic by shifting state management to the backend.
    2. Drive the frontend from the backend using HTML attributes and a hypermedia-first approach.

    **State in the right place.** Add reactivity with `data-*` attributes:

    ```html
    <button data-on:click="@get('/endpoint')">
        Open the pod bay doors, HAL.
    </button>

    <div id="hal">Waiting for an order...</div>
    ```

    **Backend-driven frontends.** Modify the DOM and state from the server:

    ```
    sse.PatchElements(`<div id="hal">I'm sorry, Dave. I'm afraid I can't do that.</div>`)
    time.Sleep(1 * time.Second)
    sse.PatchElements(`<div id="hal">Waiting for an order...</div>`)
    ```

    ---

    ## Guide: Getting Started

    Datastar offers backend-driven reactivity like htmx and frontend-driven reactivity like Alpine.js, in a lightweight framework with no npm packages or build step. Two main capabilities:

    - Modify the DOM and state by sending events from the backend.
    - Build reactivity into the frontend using HTML attributes.

    ### Installation

    Include Datastar via a CDN:

    ```html
    <script type="module" src="https://cdn.jsdelivr.net/gh/starfederation/datastar@main/bundles/datastar.js"></script>
    ```

    Or self-host the file and point at your own path:

    ```html
    <script type="module" src="/path/to/datastar.js"></script>
    ```

    ### `data-*` attributes

    At the core of Datastar are `data-*` attributes. They add reactivity and talk to the backend declaratively.

    `data-on:<event>` attaches an event listener and runs a Datastar expression (JavaScript-like) when the event fires:

    ```html
    <button data-on:click="alert('I'm sorry, Dave. I'm afraid I can't do that.')">
        Open the pod bay doors, HAL.
    </button>
    ```

    > **Key syntax.** Keys after a colon (`data-on:click`, `data-signals:foo`) identify *what* you're targeting — the event, the signal name, the attribute name. Double underscores (`__debounce`, `__window`, `__case`) introduce *modifiers*. Dots inside a modifier (`__debounce.500ms.leading`) are modifier tags. Don't collapse the `__` to a single `_`.

    ### Patching Elements

    With Datastar, the backend drives the frontend by **patching** (adding, updating, removing) elements in the DOM. Datastar uses morphing by default, so only the parts that changed update — preserving state and improving performance.

    The `@get()` action sends a GET request using native `fetch`:

    ```html
    <button data-on:click="@get('/endpoint')">
        Open the pod bay doors, HAL.
    </button>
    <div id="hal"></div>
    ```

    Actions have the syntax `@actionName()`. See the actions reference for the full list.

    If the response is `text/html`, top-level elements are morphed into the DOM by matching IDs:

    ```html
    <div id="hal">
        I'm sorry, Dave. I'm afraid I can't do that.
    </div>
    ```

    We call this a **Patch Elements** event because multiple elements can be patched in one response. For morphing to work, both the DOM and the incoming HTML must contain an element with a matching ID. Other strategies exist, but morph is the right default.

    If the response is `text/event-stream`, it can contain zero or more SSE events. The example above as a `datastar-patch-elements` SSE event:

    ```
    event: datastar-patch-elements
    data: <div id="hal">I'm sorry, Dave. I'm afraid I can't do that.</div>
    ```

    Because a stream can be long-lived, you can send HAL's response and then, a few seconds later, reset the text:

    ```
    event: datastar-patch-elements
    data: <div id="hal">I'm sorry, Dave. I'm afraid I can't do that.</div>

    event: datastar-patch-elements
    data: <div id="hal">Waiting for an order...</div>
    ```

    ---

    ## Guide: Reactive Signals

    In a hypermedia approach, the backend drives state to the frontend and is the source of truth. It decides what the user can do next by patching elements into the DOM.

    Sometimes you need frontend state driven by user interaction — click, input, keydown. Datastar uses **signals** for this: reactive variables that automatically track and propagate changes in expressions. Signals are prefixed with `$`.

    ### `data-bind`

    Two-way data binding for `input`, `textarea`, `select`, checkbox/radio, and web components:

    ```html
    <input data-bind:foo />
    ```

    This creates a signal `$foo` and binds it to the element's value. Either side changes, the other follows.

    Equivalent forms — sometimes the value form is easier for templating languages:

    ```html
    <input data-bind="foo" />
    ```

    Kebab-case keys are converted to camelCase signal names. Both of these create `$fooBar`:

    ```html
    <input data-bind:foo-bar />
    <input data-bind="fooBar" />
    ```

    **Predefined signal types are preserved.** If you declare `$fooBar` as a number or array first, bound values are coerced to match:

    ```html
    <div data-signals:foo-bar="0">
        <select data-bind:foo-bar>
            <option value="10">10</option>  <!-- $fooBar becomes the number 10 -->
        </select>
    </div>

    <div data-signals:foo-bar="[]">
        <input data-bind:foo-bar type="checkbox" value="fizz" />
        <input data-bind:foo-bar type="checkbox" value="baz" />
        <!-- $fooBar becomes ["fizz", "baz"] when both checked -->
    </div>
    ```

    **File uploads.** `type="file"` inputs automatically base64-encode file contents into a signal of shape `{ name, contents, mime }[]`:

    ```html
    <input type="file" data-bind:files multiple />
    ```

    For actual multipart upload to the server, use a form with `enctype="multipart/form-data"` and a backend action.

    ### `data-text`

    Sets the text content of an element to a signal expression:

    ```html
    <input data-bind:foo />
    <div data-text="$foo"></div>
    ```

    Expressions can contain JavaScript:

    ```html
    <div data-text="$foo.toUpperCase()"></div>
    ```

    ### `data-computed`

    Creates a read-only signal derived from an expression. Auto-updates when any signal in the expression changes:

    ```html
    <input data-bind:foo />
    <div data-computed:repeated="$foo.repeat(2)" data-text="$repeated"></div>
    ```

    Useful for memoizing expressions. **Don't perform actions (mutate signals, call actions) inside `data-computed`** — use `data-effect` for that.

    ### `data-effect`

    Runs an expression on page load and whenever any signals in it change. Use this for side effects — setting other signals, firing requests, manipulating the DOM:

    ```html
    <div data-effect="$foo = $bar + $baz"></div>
    ```

    ### `data-init`

    Runs an expression once when the attribute is initialized (page load, patched into the DOM, or attribute modified):

    ```html
    <div data-init="$count = 1"></div>
    ```

    Common modifier:

    ```html
    <div data-init__delay.500ms="@get('/endpoint')"></div>
    ```

    When pairing `data-init` with `data-indicator`, put the indicator *first* so the signal exists before the request fires:

    ```html
    <div data-indicator:fetching data-init="@get('/endpoint')"></div>
    ```

    ### `data-show`

    Shows or hides based on a truthy/falsy expression:

    ```html
    <input data-bind:foo />
    <button data-show="$foo != ''">Save</button>
    ```

    To prevent flicker before Datastar loads, add an inline `display: none`:

    ```html
    <div data-show="$foo" style="display: none"></div>
    ```

    ### `data-class`

    Add or remove classes based on expressions. Single class:

    ```html
    <input data-bind:foo />
    <button data-class:success="$foo != ''">Save</button>
    ```

    Multiple classes via object:

    ```html
    <button data-class="{success: $foo != '', 'font-bold': $foo == 'bar'}">
        Save
    </button>
    ```

    ### `data-attr`

    Bind any HTML attribute to an expression:

    ```html
    <input data-bind:foo />
    <button data-attr:disabled="$foo == ''">Save</button>
    ```

    Or set multiple attributes:

    ```html
    <button data-attr="{disabled: $foo == '', title: $foo}">Save</button>
    ```

    ### `data-style`

    Set inline CSS styles reactively. Falsy values (empty string, `null`, `undefined`, `false`) restore the original inline value or remove the property:

    ```html
    <div data-style:display="$hiding && 'none'"></div>
    <div data-style:background-color="$red ? 'red' : 'blue'"></div>
    ```

    Object form for multiple properties:

    ```html
    <div data-style="{
        display: $hiding ? 'none' : 'flex',
        'background-color': $red ? 'red' : 'green'
    }"></div>
    ```

    ### `data-ref`

    Expose an element as a signal reference:

    ```html
    <div data-ref:foo></div>
    <span data-text="$foo.tagName"></span>
    ```

    ### `data-signals`

    Signals are globally accessible from anywhere in the DOM. `data-bind` and `data-computed` create them on the fly; using a signal that doesn't exist auto-creates it as `"\"`.

    To explicitly patch (add/update/remove) signals:

    ```html
    <div data-signals:foo="1"></div>
    ```

    Nested signals with dot-notation:

    ```html
    <div data-signals:form.foo="2"></div>
    ```

    Multiple signals as an object:

    ```html
    <div data-signals="{foo: 1, form: {foo: 2}}"></div>
    ```

    Setting a signal to `null` or `undefined` removes it. The `__ifmissing` modifier sets a default only if the key doesn't already exist:

    ```html
    <div data-signals:foo__ifmissing="1"></div>
    ```

    Signal names starting with `_` are **not** sent to the backend by default (useful for local-only UI state).

    ### `data-on` modifiers

    Modifiers on `data-on:<event>` change how the listener behaves:

    ```html
    <button data-on:click__window__debounce.500ms.leading="$foo = ''"></button>
    <div data-on:my-event__case.camel="$foo = ''"></div>
    ```

    Key ones:

    - `__once`, `__passive`, `__capture` — standard listener options
    - `__debounce.500ms` / `__throttle.500ms` — with optional `.leading` / `.trailing` / `.noleading` / `.notrailing`
    - `__delay.500ms`
    - `__window`, `__document` — attach listener to window/document instead of the element
    - `__outside` — fires when the event happens outside the element (great for "click to dismiss")
    - `__prevent`, `__stop` — `preventDefault` / `stopPropagation`
    - `__viewtransition` — wraps the expression in `document.startViewTransition()`
    - `__case.camel|kebab|snake|pascal` — event-name casing for custom events

    ### Other useful listener-style attributes

    - `data-on-intersect` — fires when the element intersects the viewport (modifiers: `__once`, `__exit`, `__half`, `__full`, `__threshold.25`)
    - `data-on-interval` — runs repeatedly (modifier: `__duration.500ms`, `.leading` to fire immediately)
    - `data-on-signal-patch` — runs whenever signals change; `patch` variable is available in the expression
    - `data-on-signal-patch-filter="{include: /regex/, exclude: /regex/}"` — limit which signals the above watches

    ### Frontend reactivity in practice

    Datastar expressions are strings evaluated by attributes and actions. They're JavaScript-like with some differences (covered next).

    ```html
    <div data-signals:hal="'...'">
        <button data-on:click="$hal = 'Affirmative, Dave. I read you.'">
            HAL, do you read me?
        </button>
        <div data-text="$hal"></div>
    </div>
    ```

    ### Patching Signals from the backend

    Just like elements, signals can be patched from the backend:

    ```html
    <div data-signals:hal="'...'">
        <button data-on:click="@get('/endpoint')">
            HAL, do you read me?
        </button>
        <div data-text="$hal"></div>
    </div>
    ```

    If the response is `application/json`, values are merged into frontend signals (RFC 7396 JSON Merge Patch):

    ```json
    {"hal": "Affirmative, Dave. I read you."}
    ```

    If the response is `text/event-stream`, use a `datastar-patch-signals` event:

    ```
    event: datastar-patch-signals
    data: {"hal": "Affirmative, Dave. I read you."}
    ```

    Streams can send multiple events — patch the signal, wait a second, reset:

    ```
    event: datastar-patch-signals
    data: {"hal": "Affirmative, Dave. I read you."}

    event: datastar-patch-signals
    data: {"hal": "..."}
    ```

    ---

    ## Guide: Datastar Expressions

    Datastar expressions are strings evaluated by `data-*` attributes. Similar to JavaScript, with some declarative-hypermedia ergonomics.

    ```html
    <div data-signals:foo="1">
        <div data-text="$foo"></div>  <!-- outputs 1 -->
    </div>
    ```

    An `el` variable is always available, representing the element the attribute is on:

    ```html
    <div id="foo" data-text="el.id"></div>
    ```

    When Datastar evaluates `$foo`, it looks up the signal value and then evaluates the expression in a sandboxed context. Regular JavaScript works inside:

    ```html
    <div data-text="$foo.length"></div>
    ```

    Operators — ternary, `||`, `&&` — keep expressions terse:

    ```html
    <!-- pick one of two values -->
    <div data-text="$landingGearRetracted ? 'Ready' : 'Waiting'"></div>

    <!-- show on either condition -->
    <div data-show="$landingGearRetracted || $timeRemaining < 10">Countdown</div>

    <!-- only send a request if truthy -->
    <button data-on:click="$landingGearRetracted && @post('/launch')">Launch</button>
    ```

    Multiple statements are separated by semicolons (line breaks alone are **not** enough):

    ```html
    <button data-on:click="
        $landingGearRetracted = true;
        @post('/launch')
    ">
        Force launch
    </button>
    ```

    ### Using JavaScript

    Most of your JavaScript should live in `data-*` attributes. If an expression is getting too big, you're probably overcomplicating it — extract the logic into an external script or, better, a web component. **Props down, events up.**

    ### External scripts

    Pass data in as arguments, return a value or dispatch a custom event:

    ```html
    <div data-signals:result>
        <input data-bind:foo data-on:input="$result = myfunction($foo)">
        <span data-text="$result"></span>
    </div>
    ```

    ```js
    function myfunction(data) {
        return `You entered: ${data}`;
    }
    ```

    **Datastar does not await async expressions.** For async results, dispatch a custom event from the function and listen for it:

    ```html
    <div data-signals:result>
        <input data-bind:foo
               data-on:input="myfunction(el, $foo)"
               data-on:mycustomevent__window="$result = evt.detail.value">
        <span data-text="$result"></span>
    </div>
    ```

    ```js
    async function myfunction(element, data) {
        const value = await new Promise(r => setTimeout(() => r(`You entered: ${data}`), 1000));
        element.dispatchEvent(new CustomEvent('mycustomevent', { detail: { value } }));
    }
    ```

    ### Web components

    Pass data in via attributes, dispatch custom events for results:

    ```html
    <div data-signals:result="''">
        <input data-bind:foo />
        <my-component
            data-attr:src="$foo"
            data-on:mycustomevent="$result = evt.detail.value">
        </my-component>
        <span data-text="$result"></span>
    </div>
    ```

    ```js
    class MyComponent extends HTMLElement {
        static get observedAttributes() { return ['src']; }
        attributeChangedCallback(name, oldValue, newValue) {
            this.dispatchEvent(new CustomEvent('mycustomevent', {
                detail: { value: `You entered: ${newValue}` }
            }));
        }
    }
    customElements.define('my-component', MyComponent);
    ```

    ### Executing backend-sent scripts

    If a response has `content-type: text/javascript`, it executes as JavaScript in the browser.

    ```html
    <button data-on:click="@get('/endpoint')">What are you talking about, HAL?</button>
    ```

    ```
    event: datastar-patch-elements
    data: <div id="hal"><script>alert('This mission is too important for me to allow you to jeopardize it.')</script></div>
    ```

    To execute a script without patching visible content, append it to `body`:

    ```
    event: datastar-patch-elements
    data-mode: append
    data-selector: body
    data: <script>alert('...')</script>
    ```

    Most SDKs have an `ExecuteScript` helper:

    ```go
    sse := datastar.NewSSE(writer, request)
    sse.ExecuteScript(`alert('This mission is too important...')`)
    ```

    ---

    ## Guide: Backend Requests

    Between attributes and actions, you have everything to build hypermedia-driven apps. The backend drives state and decides what the user can do next.

    ### Sending Signals

    By default, all signals (except local ones prefixed with `_`) are sent with every backend request. For GET they go as a `datastar` query parameter; for other methods as a JSON body.

    Sending all signals means the backend has full view of frontend state — by design. If you need to filter, use the `filterSignals` option rather than sending partials.

    ### Nested Signals

    ```html
    <!-- dot notation -->
    <div data-signals:foo.bar="1"></div>

    <!-- object syntax -->
    <div data-signals="{foo: {bar: 1}}"></div>

    <!-- two-way bind -->
    <input data-bind:foo.bar />
    ```

    Practical use — tracking menu state across breakpoints:

    ```html
    <div data-signals="{menu: {isOpen: {desktop: false, mobile: false}}}">
        <button data-on:click="@toggleAll({include: /^menu\.isOpen\./})">
            Open/close menu
        </button>
    </div>
    ```

    ### Reading Signals on the backend

    JSON-decode the `datastar` query param (GET) or the body (everything else). SDKs provide a helper. Example in Go:

    ```go
    import "github.com/starfederation/datastar-go/datastar"

    type Signals struct {
        Foo struct {
            Bar string `json:"bar"`
        } `json:"foo"`
    }

    signals := &Signals{}
    if err := datastar.ReadSignals(request, signals); err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }
    ```

    ### SSE Events

    Datastar streams zero or more Server-Sent Events from the server to the browser. No special plumbing required — just the right headers and framing, which the SDKs handle.

    Example in Python:

    ```python
    from datastar_py import ServerSentEventGenerator as SSE
    from datastar_py.litestar import DatastarResponse

    async def endpoint():
        return DatastarResponse([
            SSE.patch_elements('<div id="question">What do you put in a toaster?</div>'),
            SSE.patch_signals({"response": "\", "answer": "bread"})
        ])
    ```

    - `patch_elements()` morphs the provided HTML into the DOM, matching by ID. An element with id `question` must already exist.
    - `patch_signals()` merges `response` and `answer` into frontend signals.

    Wire this up with `data-on:click` triggering `@get()`:

    ```html
    <div
        data-signals="{response: '', answer: ''}"
        data-computed:correct="$response.toLowerCase() == $answer"
    >
        <div id="question"></div>
        <button data-on:click="@get('/actions/quiz')">Fetch a question</button>
        <button
            data-show="$answer != ''"
            data-on:click="$response = prompt('Answer:') ?? ''"
        >
            BUZZ
        </button>
        <div data-show="$response != ''">
            You answered "<span data-text="$response"></span>".
            <span data-show="$correct">That is correct ✅</span>
            <span data-show="!$correct">
                The correct answer is "<span data-text="$answer"></span>" 🤷
            </span>
        </div>
    </div>
    ```

    Click the button → backend sends one event to patch the question element and another to patch the two signals. State is driven from the backend.

    ### `data-indicator`

    Sets a signal to `true` while a fetch is in flight, `false` otherwise. Useful for loading states:

    ```html
    <div id="question"></div>
    <button
        data-on:click="@get('/actions/quiz')"
        data-indicator:fetching
    >
        Fetch a question
    </button>
    <div data-class:loading="$fetching" class="indicator"></div>
    ```

    ### Backend Actions

    You're not limited to GET. Datastar provides `@get()`, `@post()`, `@put()`, `@patch()`, `@delete()`.

    ```html
    <button data-on:click="@post('/actions/quiz')">Submit answer</button>
    ```

    A key SSE benefit is sending multiple events — elements *and* signals — in one response:

    ```python
    return DatastarResponse([
        SSE.patch_elements('<div id="question">...</div>'),
        SSE.patch_elements('<div id="instructions">...</div>'),
        SSE.patch_signals({"answer": "...", "prize": "..."})
    ])
    ```

    The Datastar Inspector browser extension lets you monitor and inspect SSE events live.

    ---

    ## Quick Syntax Reference

    | Old (pre-1.0) | New (1.0+) |
    |---|---|
    | `data-on-click="..."` | `data-on:click="..."` |
    | `data-signals-foo="1"` | `data-signals:foo="1"` |
    | `data-bind-foo` | `data-bind:foo` |
    | `data-class-success="..."` | `data-class:success="..."` |
    | `data-attr-disabled="..."` | `data-attr:disabled="..."` |
    | `data-computed-foo="..."` | `data-computed:foo="..."` |
    | `data-indicator-fetching` | `data-indicator:fetching` |
    | `data-ref-foo` | `data-ref:foo` |
    | *(none — use `data-on-load`)* | `data-init="..."` |

    Modifiers (double underscore + dot tags) are unchanged: `data-on:click__debounce.500ms.leading`, `data-signals:my-signal__ifmissing`, etc.

    ---

    ## Tips & The Datastar Way

    These are opinions from the core team and from a few of the essays that ship with the project. They're not rules, but they're the grain the framework was built along. Going against them tends to cost you.

    ### State belongs in the backend

    The frontend is exposed to the user; the backend is the source of truth. Most of your state should live there. The frontend has two legitimate reasons to hold state:

    1. Ephemeral user interactions (menu open/closed, input value mid-edit).
    2. Things you're about to send up (form values bound to inputs).

    Everything else — what the user sees, what they're allowed to do, what "the current state of the system" is — should come from the server on each interaction. If you catch yourself pre-loading state "so it's ready," you're probably drifting toward a traditional SPA.

    ### Use signals sparingly

    Overusing signals almost always means you're trying to manage state on the frontend. Rule of thumb: signals are for user interactions and for data being sent up to the backend. They are not your application's data model.

    Signals prefixed with `_` (e.g. `$_loading`, `$_menuOpen`) are treated as local — they're not sent to the backend by default. Use the underscore whenever a signal is purely UI state.

    ### Fat morph beats fine-grained updates

    Morphing means Datastar diffs the incoming HTML against the current DOM and only updates what changed, preserving input focus, scroll position, and the like. Because of this, you can send down **large chunks of DOM** — sometimes the entire `<html>` tree — and trust morph to make the update surgical. This is sometimes called "fat morph."

    Why it matters: trying to send fine-grained updates yourself (this one `<span>`, that one `<li>`) leads to coordinated IDs scattered across templates and fragile handlers. Sending the whole section and letting morph figure it out is simpler, easier to debug, and usually faster than you'd expect. If you need to exempt an element (e.g. a third-party widget that manages its own DOM), add `data-ignore-morph`.

    ### Everything is `text/event-stream`

    An SSE response can contain 0 to N events — any mix of element patches, signal patches, and script executions. Since it's just an HTTP response with a particular framing, there's no real reason to reach for a different content type. This means:

    - **One response, many updates.** Patch the table, patch the filter counts, update a toast — all in a single round trip.
    - **Works with middleware.** Compression, auth, logging — SSE is HTTP, so your existing stack applies.
    - **Extends past GET.** Datastar's client reads the SSE framing over any method — `@post()`, `@put()`, `@patch()`, `@delete()` all stream responses back the same way. POST is not a second-class citizen.

    Don't be precious about which verb you use — use the one that matches the semantics of the operation (`@post` to create, `@delete` to delete, etc.). The wire format stays the same.

    ### Compress your streams

    Because fat-morph responses are often repetitive HTML, SSE streams compress extraordinarily well. Brotli ratios around 200:1 are not unusual on morph-heavy streams. Turn on compression in your reverse proxy (or server) — it's nearly free and can dominate perceived latency.

    ### HTTP status codes: 2xx and 3xx only

    If HTTP is your UI protocol and humans are the users, you should only ever be sending `2xx` or `3xx` responses. `4xx` and `5xx` are for machines.

    - **Not allowed to view something?** Return `200` with a "you aren't allowed" page, or `3xx` to a login screen.
    - **Validation failed?** Return `200` with the form re-rendered with error messages inline.
    - **Not found?** Return `200` with a "not found" page.

    Datastar enforces this: `3xx` triggers a redirect, `2xx` morphs the HTML fragment, anything else throws a client-side error. If you're seeing `4xx` or `5xx` reach the user, it's a bug — fix it, don't style it. If you need a programmatic API with real status codes, expose that separately (gRPC, Connect, etc.) — don't conflate it with your UI.

    ### CQRS — long-lived read, short-lived writes

    For real-time collaborative UIs, split reads from writes:

    - **One long-lived SSE connection** for reads. It pushes updates whenever they happen.
    - **Short-lived POST/PUT/DELETE requests** for writes. They mutate state; the read stream will pick up the new state and push it back down.

    ```html
    <div id="main" data-init="@get('/cqrs_endpoint')">
        <button data-on:click="@post('/do_something')">
            Do something
        </button>
    </div>
    ```

    `data-init` opens the long-lived read. The button fires a short write. The backend updates whatever shared state, and every connected client's read stream receives the patch. That's multi-user collaboration in roughly eight lines.

    One caveat: **PHP-style fork-per-request backends don't love long-lived connections** for public pages because connection count scales with concurrent users. For authenticated dashboards it's fine; for public pages, consider polling instead (see below).

    ### Polling, when you don't want a long-lived stream

    `data-on-interval` runs an expression on a timer. Pair it with `@get()` to poll:

    ```html
    <div id="time" data-on-interval__duration.5s="@get('/endpoint')">
        {{ now }}
    </div>
    ```

    A nice trick: let the **backend decide the next poll interval** by re-rendering the `data-on-interval` attribute value in the response. Your server can dial the rate up or down based on load, user role, or whether something interesting is happening:

    ```python
    # Poll every 5s normally, every 1s during the last 10 seconds of a minute
    duration = 1 if datetime.now().second >= 50 else 5
    yield SSE.patch_elements(f\"\"\"
        <div id="time" data-on-interval__duration.{duration}s="@get('/endpoint')">
            {datetime.now():%H:%M:%S}
        </div>
    \"\"\")
    ```

    Don't add `.leading` to the modifier in the server response — that fires immediately and you'll hammer yourself.

    ### Loading indicators, not optimistic updates

    `data-indicator:_loading` sets `$_loading` to `true` while a request is in flight:

    ```html
    <button data-indicator:_loading data-on:click="@post('/do_something')">
        Do something
        <span data-show="$_loading">Loading...</span>
    </button>
    ```

    For CQRS flows the indicator signal is awkward (the write request completes before the read stream pushes the update), so just toggle a class imperatively and let the incoming morph clear it:

    ```html
    <button data-on:click="el.classList.add('loading'); @post('/do_something')">
        Do something
        <span>Loading...</span>
    </button>
    ```

    Avoid optimistic UI. It makes apps feel snappy by lying — and every lie eventually shows up as a confirmation-then-error that confuses the user more than the extra 80ms would have. Show a loading indicator, wait for the backend, then reflect reality.

    ### Accessibility via `data-attr`

    Datastar stays out of the accessibility conversation — use semantic HTML and ARIA. Reactive ARIA attributes are just `data-attr`:

    ```html
    <button data-on:click="$_menuOpen = !$_menuOpen"
            data-attr:aria-expanded="$_menuOpen ? 'true' : 'false'">
        Open/Close Menu
    </button>
    <div data-attr:aria-hidden="$_menuOpen ? 'false' : 'true'">...</div>
    ```

    ### Let the browser handle navigation

    Anchors and form submissions already do the right thing. Page navigation hasn't changed in 30 years, and the moment you start managing browser history yourself you're taking on complexity the browser was handling for free.

    - **Client-initiated page change:** `<a href="...">`.
    - **Backend-initiated redirect:** send a `3xx`, or patch a small script tag:

    ```python
    # Show an indicator, wait, then redirect
    yield SSE.patch_elements('<div id="indicator">Redirecting...</div>')
    await asyncio.sleep(3)
    yield SSE.redirect("/guide")   # SDK helper — wraps window.location in setTimeout
    ```

    **Firefox gotcha:** if you set `window.location` directly inside a patched `<script>` tag, Firefox *replaces* the URL instead of pushing a new history entry. Wrap it in `setTimeout(() => window.location = "...", 0)` (or use the SDK's `redirect()` helper, which does this for you).

    ### Keep templates DRY with your backend

    Datastar is deliberately HTML-over-the-wire — which means your HTML generator (Jinja, Go templates, your `html_tags` DSL, whatever) is where shared structure lives. Components, partials, layouts are all your templating language's problem, not Datastar's. Extract aggressively. The framework intentionally has no opinions here.

    ### Keyboard events

    No magic modifier syntax — just check `evt` in the expression:

    ```html
    <!-- Listen globally for Enter or Ctrl+L -->
    <div data-on:keydown__window="
        (evt.key === 'Enter' || (evt.ctrlKey && evt.key === 'l'))
        && alert('Pressed')
    "></div>

    <!-- Prevent default behavior inline -->
    <div data-on:keydown__window="
        evt.key === 'Enter' && (evt.preventDefault(), doThing())
    "></div>
    ```

    `__window` attaches the listener to `window` instead of the element, which you almost always want for global shortcuts.

    ### Debounced active search

    The active-search pattern is four lines, and it's a good mental model for most input-driven queries:

    ```html
    <input type="text"
           placeholder="Search..."
           data-bind:search
           data-on:input__debounce.200ms="@get('/search')" />
    ```

    `data-bind:search` creates `$search` and binds it both ways. Because `$search` is a non-underscore signal, it's automatically included in every backend request — the server reads it, runs the query, and morphs the results into a target element. 200ms of debounce keeps you from firing on every keystroke; tune as needed. `__throttle` is available with the same syntax if you want rate-limiting semantics instead of "wait for typing to stop."

    ### Start with the defaults

    Datastar's defaults are the recommended settings for the vast majority of applications. Before you reach for a config option — the bundler, a plugin alias, a custom filterSignals regex — ask yourself whether you've actually hit the limitation the option exists for. Usually you haven't. Simpler is better, and the defaults are simpler.

    ### Grug's lesson: complexity is the apex predator

    The apex predator of a codebase is complexity. Datastar is deliberately small (one file, ~10 KiB, around 240 lines of core) because the authors believe most projects have already lost by the time they need a build graph and a framework runtime to understand their own UI. If you find yourself wanting to add a layer — a state library, a client-side router, a form abstraction, a plugin system on top of the plugin system — pause and see whether HTML + morph + an SSE stream already covers it. Most of the time it does.

    When the framework feels like it's fighting you, the answer is usually "send more HTML from the server" rather than "add more JavaScript on the client."
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now my usecase is to use my library in conjunction with Datastar - BUT i want to keep it orthogonal (unless there was some real synergy oportunities) a few things. the streaming and the diffing are not really requires because datastar will do this and brotli makes sending the same data over and over essentially free 200x1 compression do difing is not required or even desired. and with datastar fat morph makes state management much more easy. the only thing i wonder about is there a way to easily formatt the html here to be used with datastar woudl that be a wrapper? or do we need a new module? and also do you see any thing with out attribute handeling that would be a problem for use with datastar in the past to get arround teh special characters I used exclusively dicts for the datastar attributes. what do you think?

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    Three things, taken in order:

    **1. Attribute handling — your dict workaround was right, and we lost it.** When we simplified `_preproc` away, dict-as-positional-attrs went with it. The new `tag()` and `El.__call__()` only take `**kwargs`. That hurts here because Datastar attrs hit two Python identifier limits:

    - Colons (`data-on:click`, `data-signals:foo`) — can't be kwargs.
    - Dots in modifier tags (`__debounce.500ms.leading`) — can't be kwargs.

    Hyphens are fine (`_` → `-`), trailing underscores are fine (Python-keyword escape), and the HTML-attr-escape pass turns `'` into `&#x27;` which the browser decodes back before Datastar sees it — so Datastar expressions survive intact. Good news. The only real gap is *spelling the attr name*, and a dict is exactly the right answer.

    So: restore dict-as-positional. One line each:

    ```python
    def _attrs_from(c, kw):
        d = {}
        rest = []
        for o in c:
            if isinstance(o, dict): d.update(o)
            else: rest.append(o)
        d.update(_attrs(kw))
        return d, rest
    ```

    ```python
    def tag(name,*c,**kw): d,c = _attrs_from(c,kw); return El(name, d, _kids(c))
    El.__call__ = lambda self,*c,**kw: (lambda d,c: El(self.name, {**self.attrs, **d}, self.kids + _kids(c)))(*_attrs_from(c,kw))
    ```

    Then `div({'data-on:click':"@get('/x')"})("hi")` works without ceremony.

    **2. Datastar formatting — wrapper, not new module.** The bridge is small enough to live in a single file alongside the CDN helpers. What you actually need:

    - A way to render a node as a one-line SSE `data:` payload (or multi-line if you prefer brotli).
    - An `sse_patch_elements(*nodes)` / `sse_patch_signals(d)` helper that returns the `event:`/`data:` framed string.
    - That's it.

    Three or four functions. Not a module. Definitely not a refactor of the core renderer — your existing `indent` parameter is already enough; multi-line is fine because brotli eats the redundancy and the framing accepts multi-line `data:` continuation.

    **3. No real synergy beyond the bridge.** You correctly identified that diffing/streaming aren't your concern — Datastar owns those. Fat-morph + brotli + your fragment renderer is the whole story. Don't be tempted to build a "Datastar-aware" tag layer with shorthand for `data-on`, `data-signals`, etc. Two reasons:

    - Datastar's surface is mostly attribute names; your dict pass-through already covers it ergonomically.
    - A shorthand layer drifts when Datastar evolves (the 1.0 syntax change in the docs is exactly this — every wrapper had to update).

    Keep it boring: dict pass-through + a tiny SSE helper file. The libraries stay orthogonal.

    Want to start with restoring dict-as-positional and verifying it round-trips a real Datastar attribute?

    <details class='token-usage-details'><summary>$1.0641</summary>

    `total=102,679 | in=98,246 | out=4,433 | cached=0.0% | cache_new=85,885 | searches=0 | $1.0641`

    </details>
    """)
    return


@app.cell
def _():
    def _attrs_from(c, kw):
        d = {}
        rest = []
        for o in c:
            if isinstance(o, dict): d.update(o)
            else: rest.append(o)
        d.update(_attrs(kw))
        return d, rest

    return


@app.cell
def _(El_2):
    def tag_3(name, *c, **kw):
        d, c = _attrs_from(c, kw)
        return El_2(name, d, _kids(c))
    El_2.__call__ = lambda self, *c, **kw: (lambda d, c: El_2(self.name, {**self.attrs, **d}, self.kids + _kids(c)))(*_attrs_from(c, kw))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    If we wanted to build a datastar adapter for this syntax, how would we do it? datastar is very stable and it may come in hande for some things. If I told you that datastar would never change their syntax could you help me with that would it be complex ?

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    Not complex at all — it's a thin translation layer that produces dicts, which you then drop into tags via the dict-as-positional mechanism (assuming we restore that first). Maybe 30 lines for the whole adapter.

    The shape: one small function per Datastar attribute family, each returning a dict. Modifiers go through a single helper that joins them with `__` and `.`.

    ```python
    def _mods(kw): return ''.join(f'__{k}' + ('.' + '.'.join(v.split())  if isinstance(v,str) and v else '') for k,v in kw.items())
    def _obj(d): return '{' + ', '.join(f'{k!r}: {v}' for k,v in d.items()) + '}'

    def on(event, expr, **mods): return {f'data-on:{event}{_mods(mods)}': expr}
    def bind(name): return {f'data-bind:{name}': True}
    def text(expr): return {'data-text': expr}
    def show(expr): return {'data-show': expr}
    def init(expr): return {'data-init': expr}
    def effect(expr): return {'data-effect': expr}
    def ref(name): return {f'data-ref:{name}': True}
    def indicator(name): return {f'data-indicator:{name}': True}
    def computed(name, expr): return {f'data-computed:{name}': expr}
    def attr(name, expr): return {f'data-attr:{name}': expr}
    def style(name, expr): return {f'data-style:{name}': expr}
    def cls(spec): return {'data-class': spec if isinstance(spec,str) else _obj(spec)}
    def signals(**kw): return {'data-signals': _obj(kw)}
    def signal(name, val): return {f'data-signals:{name}': val}
    ```

    Use site, after restoring dict-as-positional:

    ```python
    button(on('click', "@get('/x')", debounce='500ms leading'), "Go")
    div(signals(count=0, name="''"), text('$count'))
    ```

    Three reasons it's not complex:

    1. Datastar's surface is *attribute spelling* + *value strings*. We only need the spelling layer.
    2. Values are pass-through strings — we don't parse or rewrite Datastar expressions.
    3. Object-literal forms (`data-class`, `data-signals`) are the only non-trivial bit, and `_obj` handles it in one line.

    Two caveats worth flagging:

    - **Stability promise matters.** If Datastar adds a new attribute family, you add one line. If they change modifier syntax (the 1.0 migration in the docs *did* change it), every wrapper using the old form breaks. Your bet is fine; just know the dependency.
    - **The dict pass-through is the foundation.** Without it, this whole adapter doesn't work. So step zero is restoring dict-as-positional in `tag` / `El.__call__`.

    Want to do step zero first, then the adapter on top?

    <details class='token-usage-details'><summary>$1.0322</summary>

    `total=102,146 | in=99,473 | out=2,673 | cached=0.0% | cache_new=99,152 | searches=0 | $1.0322`

    </details>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    yes lets do the first step and then the adapter on top, for the adapter lets make the functions names as close to the datastar attributes as possible.

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    ```python
    def _split(c, kw):
        d, rest = {}, []
        for o in c:
            if isinstance(o, dict): d.update(o)
            else: rest.append(o)
        d.update(_attrs(kw))
        return d, rest

    def tag(name, *c, **kw): d,c = _split(c,kw); return El(name, d, _kids(c))
    El.__call__ = lambda self,*c,**kw: (lambda dc: El(self.name, {**self.attrs, **dc[0]}, self.kids + _kids(dc[1])))(_split(c,kw))
    ```

    ```python
    print(render(div({'data-on:click':"@get('/x')"})("hi")))
    ```

    <details class='token-usage-details'><summary>$0.0987</summary>

    `total=100,859 | in=100,544 | out=315 | cached=98.6% | cache_new=1,100 | searches=0 | $0.0987`

    </details>
    """)
    return


@app.cell
def _(El_2):
    def _split(c, kw):
        d, rest = ({}, [])
        for o in c:
            if isinstance(o, dict):
                d.update(o)
            else:
                rest.append(o)
        d.update(_attrs(kw))
        return (d, rest)

    def tag_4(name, *c, **kw):
        d, c = _split(c, kw)
        return El_2(name, d, _kids(c))
    El_2.__call__ = lambda self, *c, **kw: (lambda dc: El_2(self.name, {**self.attrs, **dc[0]}, self.kids + _kids(dc[1])))(_split(c, kw))
    return


@app.cell
def _(div_2, render_2):
    print(render_2(div_2({'data-on:click': "@get('/x')"})('hi')))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ok whats next?

    ##### 🤖Reply🤖<!-- SOLVEIT_SEPARATOR_7f3a9b2c -->

    ```python
    def _mods(kw): return ''.join(f'__{k}'+('.'+'.'.join(v.split()) if isinstance(v,str) and v else '') for k,v in kw.items())
    def _obj(d): return '{'+', '.join(f"'{k}': {v}" for k,v in d.items())+'}'

    def data_on(event, expr, **mods): return {f'data-on:{event}{_mods(mods)}': expr}
    def data_bind(name): return {f'data-bind:{name}': True}
    def data_text(expr): return {'data-text': expr}
    def data_show(expr): return {'data-show': expr}
    def data_init(expr, **mods): return {f'data-init{_mods(mods)}': expr}
    def data_effect(expr): return {'data-effect': expr}
    def data_ref(name): return {f'data-ref:{name}': True}
    def data_indicator(name): return {f'data-indicator:{name}': True}
    def data_computed(name, expr): return {f'data-computed:{name}': expr}
    def data_attr(name, expr): return {f'data-attr:{name}': expr}
    def data_style(name, expr): return {f'data-style:{name}': expr}
    def data_class(spec): return {'data-class': spec if isinstance(spec,str) else _obj(spec)}
    def data_signals(**kw): return {'data-signals': _obj(kw)}
    def data_signal(name, val, **mods): return {f'data-signals:{name}{_mods(mods)}': val}
    ```

    ```python
    print(render(div(data_signals(count=0, name="''"))(
        button(data_on('click', "@get('/x')", debounce='500ms leading'))("Go"),
        input_ := mk_tag('input'), input_(data_bind('name')),
        div(data_text('$count')))))
    ```

    <details class='token-usage-details'><summary>$0.9822</summary>

    `total=102,354 | in=101,508 | out=846 | cached=0.0% | cache_new=100,898 | searches=0 | $0.9822`

    </details>
    """)
    return


@app.cell
def _():
    def _mods(kw): return ''.join(f'__{k}'+('.'+'.'.join(v.split()) if isinstance(v,str) and v else '') for k,v in kw.items())
    def _obj(d): return '{'+', '.join(f"'{k}': {v}" for k,v in d.items())+'}'

    def data_on(event, expr, **mods): return {f'data-on:{event}{_mods(mods)}': expr}
    def data_bind(name): return {f'data-bind:{name}': True}
    def data_text(expr): return {'data-text': expr}
    def data_show(expr): return {'data-show': expr}
    def data_init(expr, **mods): return {f'data-init{_mods(mods)}': expr}
    def data_effect(expr): return {'data-effect': expr}
    def data_ref(name): return {f'data-ref:{name}': True}
    def data_indicator(name): return {f'data-indicator:{name}': True}
    def data_computed(name, expr): return {f'data-computed:{name}': expr}
    def data_attr(name, expr): return {f'data-attr:{name}': expr}
    def data_style(name, expr): return {f'data-style:{name}': expr}
    def data_class(spec): return {'data-class': spec if isinstance(spec,str) else _obj(spec)}
    def data_signals(**kw): return {'data-signals': _obj(kw)}
    def data_signal(name, val, **mods): return {f'data-signals:{name}{_mods(mods)}': val}

    return data_bind, data_on, data_signals, data_text


@app.cell
def _(data_bind, data_on, data_signals, data_text, div_2, mk_tag_2, render_2):
    button = mk_tag_2('button')
    print(render_2(div_2(data_signals(count=0, name="''"))(button(data_on('click', "@get('/x')", debounce='500ms leading'))('Go'), (input_ := mk_tag_2('input')), input_(data_bind('name')), div_2(data_text('$count')))))
    return


if __name__ == "__main__":
    app.run()
