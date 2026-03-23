import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")

with app.setup:
    import types, re
    from collections import namedtuple
    from html import escape
    from html.parser import HTMLParser

    VOID_TAGS = frozenset({'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'})
    RAW_TAGS = frozenset({'script', 'style'})
    RAW_CLOSE_RE = re.compile('</(script|style)[\\s/>]', re.IGNORECASE)

    SAFE_ATTR_RE = re.compile('^[a-zA-Z_][\\w\\-:.]*$')
    URL_ATTRS = frozenset({'href', 'src', 'action', 'formaction', 'data', 'poster', 'codebase', 'cite', 'background', 'dynsrc', 'lowsrc'})
    DANGEROUS_URL_RE = re.compile('^(?:javascript:|vbscript:|data:(?!(?:text/html|text/plain|image/|application/json)))', re.IGNORECASE)

    ALL_TAGS = ['A', 'Abbr', 'Address', 'Area', 'Article', 'Aside', 'Audio', 'B', 'Base', 'Bdi', 'Bdo', 'Blockquote', 'Body', 'Br', 'Button', 'Canvas', 'Caption', 'Cite', 'Code', 'Col', 'Colgroup', 'Data', 'Datalist', 'Dd', 'Del', 'Details', 'Dfn', 'Dialog', 'Div', 'Dl', 'Dt', 'Em', 'Embed', 'Fieldset', 'Figcaption', 'Figure', 'Footer', 'Form', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'Head', 'Header', 'Hgroup', 'Hr', 'Html', 'I', 'Iframe', 'Img', 'Input', 'Ins', 'Kbd', 'Label', 'Legend', 'Li', 'Link', 'Main', 'Map', 'Mark', 'Menu', 'Meta', 'Meter', 'Nav', 'Noscript', 'Object', 'Ol', 'Optgroup', 'Option', 'Output', 'P', 'Picture', 'Pre', 'Progress', 'Q', 'Rp', 'Rt', 'Ruby', 'S', 'Samp', 'Script', 'Search', 'Section', 'Select', 'Slot', 'Small', 'Source', 'Span', 'Strong', 'Style', 'Sub', 'Summary', 'Sup', 'Table', 'Tbody', 'Td', 'Template', 'Textarea', 'Tfoot', 'Th', 'Thead', 'Time', 'Title', 'Tr', 'Track', 'U', 'Ul', 'Var', 'Video', 'Wbr']


    SVG_NAMES = {'ClipPath': 'clipPath', 'ForeignObject': 'foreignObject', 'LinearGradient': 'linearGradient', 'RadialGradient': 'radialGradient', 'TextPath': 'textPath', 'AnimateMotion': 'animateMotion', 'AnimateTransform': 'animateTransform', 'FeBlend': 'feBlend', 'FeColorMatrix': 'feColorMatrix', 'FeComponentTransfer': 'feComponentTransfer', 'FeComposite': 'feComposite', 'FeConvolveMatrix': 'feConvolveMatrix', 'FeDiffuseLighting': 'feDiffuseLighting', 'FeDisplacementMap': 'feDisplacementMap', 'FeDistantLight': 'feDistantLight', 'FeDropShadow': 'feDropShadow', 'FeFlood': 'feFlood', 'FeFuncA': 'feFuncA', 'FeFuncB': 'feFuncB', 'FeFuncG': 'feFuncG', 'FeFuncR': 'feFuncR', 'FeGaussianBlur': 'feGaussianBlur', 'FeImage': 'feImage', 'FeMerge': 'feMerge', 'FeMergeNode': 'feMergeNode', 'FeMorphology': 'feMorphology', 'FeOffset': 'feOffset', 'FePointLight': 'fePointLight', 'FeSpecularLighting': 'feSpecularLighting', 'FeSpotLight': 'feSpotLight', 'FeTile': 'feTile', 'FeTurbulence': 'feTurbulence'}
    SVG_VOID = frozenset({'stop', 'set', 'image', 'use', 'feBlend', 'feColorMatrix', 'feComposite', 'feConvolveMatrix', 'feDisplacementMap', 'feDistantLight', 'feDropShadow', 'feFlood', 'feFuncA', 'feFuncB', 'feFuncG', 'feFuncR', 'feGaussianBlur', 'feImage', 'feMergeNode', 'feMorphology', 'feOffset', 'fePointLight', 'feSpotLight', 'feTile', 'feTurbulence'})
    SVG_SELF_CLOSING = frozenset({'circle', 'ellipse', 'line', 'path', 'polygon', 'polyline', 'rect', 'animate', 'animateMotion', 'animateTransform'})
    ALL_SVG = ['Svg', 'G', 'Defs', 'Symbol', 'Use', 'Image', 'Circle', 'Ellipse', 'Line', 'Path', 'Polygon', 'Polyline', 'Rect', 'Text', 'Tspan', 'TextPath', 'ClipPath', 'Mask', 'Marker', 'Pattern', 'Filter', 'LinearGradient', 'RadialGradient', 'Stop', 'ForeignObject', 'Set', 'Animate', 'AnimateMotion', 'AnimateTransform', 'FeBlend', 'FeColorMatrix', 'FeComponentTransfer', 'FeComposite', 'FeConvolveMatrix', 'FeDiffuseLighting', 'FeDisplacementMap', 'FeDistantLight', 'FeDropShadow', 'FeFlood', 'FeFuncA', 'FeFuncB', 'FeFuncG', 'FeFuncR', 'FeGaussianBlur', 'FeImage', 'FeMerge', 'FeMergeNode', 'FeMorphology', 'FeOffset', 'FePointLight', 'FeSpecularLighting', 'FeSpotLight', 'FeTile', 'FeTurbulence']


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Utils
    """)
    return


@app.function
def attrmap(k):
    match k:
        case 'cls'|'_class': return 'class'
        case '_for': return 'for'
        case '_from': return 'from'
        case '_in': return 'in'
        case '_is': return 'is'
        case _: return k.replace('_', '-')


@app.function
def flatten(c):
    for o in c:
        if o is None or o is False: continue
        if hasattr(o, 'tag'): yield o
        elif isinstance(o, (list, tuple, map, filter, types.GeneratorType)): yield from flatten(o)
        else: yield o


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Core
    """)
    return


@app.class_definition
class Tag(
    namedtuple(
        'Tag', 
        'tag children attrs mode self_closing', 
        defaults=(
            (), {}, 'normal', False
        )
    )
):
    '''An HTML element: pure data, no rendering'''
    def __call__(self, *c, **kw):
        "Create new Tag with appended children and merged attributes"
        attrs = {k:v for o in c if isinstance(o, dict) for k,v in o.items()}
        children = tuple(flatten(o for o in c if not isinstance(o, dict)))
        return Tag(
            self.tag, 
            self.children + children, 
            {**self.attrs, **{attrmap(k):v for k,v in kw.items()}, **attrs}, 
            self.mode, 
            self.self_closing)


@app.function
def mktag(name, mode='normal', self_closing=False):
    '''Create a tag constructor function for the given element name'''
    def f(*c, **kw):
        attrs = {k:v for o in c if isinstance(o, dict) for k,v in o.items()}
        children = tuple(flatten(o for o in c if not isinstance(o, dict)))
        return Tag(name, children, {**{attrmap(k):v for k,v in kw.items()}, **attrs}, mode, self_closing)
    f.__name__ = name.capitalize()
    return f


@app.function
def Fragment(*c, **kw): return Tag('', tuple(flatten(c)), {attrmap(k):v for k,v in kw.items()})


@app.cell
def _():
    Tag('div', ('hello',), {'class': 'test'})
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Validation
    """)
    return


@app.function
def validate(t):
    "Validate a Tag tree, raising ValueError on structural problems"
    if not hasattr(t, 'tag'): return t
    if t.mode == 'void' and t.children: raise ValueError(f'Void element <{t.tag}> cannot have children')
    if t.mode == 'raw':
        for c in t.children:
            if hasattr(c, 'tag'): raise ValueError(f'Raw element <{t.tag}> cannot contain nested tags')
        inner = ''.join(str(c).replace('\x00', '') for c in t.children)
        if RAW_CLOSE_RE.search(inner): raise ValueError(f'Raw text in <{t.tag}> must not contain closing tag pattern')
    for c in t.children:
        if hasattr(c, 'tag') and c.tag == 'html' and t.tag != 'iframe':
            raise ValueError('<html> cannot be nested inside another element (except <iframe>)')
        validate(c)
    return t


@app.cell
def _():
    validate(Tag('div', (Tag('p', ('hello',)),)))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Rendering
    """)
    return


@app.function
def render_attrs(d):
    "Render a dict of attributes to an HTML attribute string"
    out = ''
    for k,v in d.items():
        if not SAFE_ATTR_RE.match(k): raise ValueError(f'Unsafe attribute name: {k!r}')
        if k in URL_ATTRS and DANGEROUS_URL_RE.match(str(v)): raise ValueError(f'Dangerous URL scheme in {k}: {str(v)[:60]!r}')
        v2 = str(v).replace('&', '&amp;').replace('<', '&lt;').replace('"', '&quot;')
        if v is True: out += f' {k}'
        elif v is not False and v is not None: out += f' {k}="{v2}"'
    return out


@app.function
def to_html(t):
    "Convert a Tag tree to an HTML string"
    if hasattr(t, '__html__') and not isinstance(t, Tag): return t.__html__()
    if not hasattr(t, 'tag'): return escape(str(t).replace('\x00', ''))
    validate(t)
    attrs = render_attrs(t.attrs) if t.attrs else ''
    if t.mode == 'raw':
        inner = ''.join(str(c).replace('\x00', '') for c in t.children)
    else: inner = ''.join(to_html(c) for c in t.children)
    if not t.tag: return inner
    if t.mode == 'void': return f'<{t.tag}{attrs} />' if t.self_closing else f'<{t.tag}{attrs}>'
    if not inner and t.self_closing: return f'<{t.tag}{attrs} />'
    if t.tag == 'html': return f'<!DOCTYPE html>\n<{t.tag}{attrs}>{inner}</{t.tag}>'
    return f'<{t.tag}{attrs}>{inner}</{t.tag}>'


@app.cell
def _():
    to_html(Tag('div', (Tag('p', ('hello',)),), {'class': 'main'}))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Notebook Helpers
    """)
    return


@app.class_definition
class HTML:
    "Thin wrapper for notebook display — keeps rendering out of Tag"
    def __init__(self, t): self.t = t
    def __str__(self): return to_html(self.t)
    _repr_html_ = __str__


@app.function
def setup_tags(ns=None):
    "Create tag constructors in the given namespace (or caller's globals)"
    import inspect
    if ns is None: ns = inspect.currentframe().f_back.f_globals
    for name in ALL_TAGS:
        n = name.lower()
        if n in VOID_TAGS: mode = 'void'
        elif n in RAW_TAGS: mode = 'raw'
        else: mode = 'normal'
        ns[name] = mktag(n, mode)
    return ns


@app.function
def setup_svg(ns=None):
    "Create SVG tag constructors; sub-tags are attrs of Svg"
    import inspect
    if ns is None: ns = inspect.currentframe().f_back.f_globals
    is_dict = isinstance(ns, dict)
    svg_tag = mktag('svg', 'normal', False)
    for name in ALL_SVG:
        if name == 'Svg': continue
        tag_name = SVG_NAMES.get(name, name.lower())
        if tag_name in SVG_VOID: mode, sc = 'void', True
        elif tag_name in SVG_SELF_CLOSING: mode, sc = 'normal', True
        else: mode, sc = 'normal', False
        setattr(svg_tag, name, mktag(tag_name, mode, sc))
    if is_dict: ns['Svg'] = svg_tag
    else: setattr(ns, 'Svg', svg_tag)
    return ns


@app.cell
def _(Div, Svg):
    # Confirm path does not colide (nice!)
    setup_tags()
    setup_svg()
    print(to_html(Div(Svg(Svg.Circle(cx=50, cy=50, r=40), Svg.Path(d="M10 10")))))
    from pathlib import Path
    print(type(Path('.')))

    return


@app.cell
def _(Circle, Svg):
    setup_svg()
    print(HTML(Svg(Circle(cx=50, cy=50, r=40), width=100, height=100)))
    HTML(Svg(Circle(cx=50, cy=50, r=40), width=100, height=100))
    return


@app.cell
def _(Div, P):
    setup_tags()
    print(to_html(Div(P('hello', cls='greeting'), id='main')))
    HTML(Div(P('hello', cls='greeting'), id='main'))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Convenience
    """)
    return


@app.function
def pretty(t, indent=2, indent_script=False, indent_style=True, _depth=0):
    "Pretty-print an HTML tag tree with indentation"
    if hasattr(t, '__html__') and not isinstance(t, Tag): return t.__html__()
    pad, pad1 = ' ' * (indent * _depth), ' ' * (indent * (_depth + 1))
    if not hasattr(t, 'tag'): return pad + escape(str(t).replace('\x00', ''))
    validate(t)
    attrs = render_attrs(t.attrs) if t.attrs else ''
    if t.mode == 'void': return f'{pad}<{t.tag}{attrs} />' if t.self_closing else f'{pad}<{t.tag}{attrs}>'
    if t.mode == 'raw':
        inner = ''.join(str(c).replace('\x00', '') for c in t.children)
        should_indent = (t.tag == 'style' and indent_style) or (t.tag == 'script' and indent_script)
        if should_indent and inner.strip():
            lines = inner.strip().splitlines()
            return f'{pad}<{t.tag}{attrs}>\n' + '\n'.join(pad1 + l for l in lines) + f'\n{pad}</{t.tag}>'
        if not inner: return f'{pad}<{t.tag}{attrs}></{t.tag}>'
        return f'{pad}<{t.tag}{attrs}>{inner}</{t.tag}>'
    if not t.tag: return '\n'.join(pretty(c, indent, indent_script, indent_style, _depth) for c in t.children)
    if not t.children: return f'{pad}<{t.tag}{attrs} />' if t.self_closing else f'{pad}<{t.tag}{attrs}></{t.tag}>'
    if len(t.children) == 1 and isinstance(t.children[0], str): return f'{pad}<{t.tag}{attrs}>{escape(t.children[0].replace(chr(0), ""))}</{t.tag}>'
    prefix = '<!DOCTYPE html>\n' if t.tag == 'html' else ''
    children = '\n'.join(pretty(c, indent, indent_script, indent_style, _depth + 1) for c in t.children)
    return f'{prefix}{pad}<{t.tag}{attrs}>\n{children}\n{pad}</{t.tag}>'


@app.class_definition
class Safe(str):
    '''Mark a string as pre-escaped HTML — passes through to_html unescaped'''
    def __html__(self): return self


@app.function
def html_to_tag(s):
    "Parse an HTML string into a Tag tree"
    stack, root = [[]], []
    class P(HTMLParser):
        def handle_starttag(self, tag, attrs):
            d = {k:(v if v is not None else True) for k,v in attrs}
            mode = 'raw' if tag in RAW_TAGS else 'void' if tag in VOID_TAGS else 'normal'
            if mode == 'void': stack[-1].append(Tag(tag, (), d, mode))
            else: stack.append([]); root.append((tag, d, mode))
        def handle_endtag(self, tag):
            if tag in VOID_TAGS: return
            children = tuple(stack.pop())
            t, d, mode = root.pop()
            stack[-1].append(Tag(t, children, d, mode))
        def handle_data(self, data):
            if data.strip(): stack[-1].append(data.strip())
    P().feed(s)
    res = stack[0]
    return res[0] if len(res) == 1 else Fragment(*res)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Demo / Experiments
    """)
    return


@app.cell
def _():
    _ = '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><defs><mask id="SVGD6xQNbIZ"><path fill="none" stroke="#fff" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 23c-2 0 -3 2 -5 2c-2 0 -3 -2 -5 -2c-2 0 -3 2 -5 2c-2 0 -3 -2 -5 -2c-2 0 -3 2 -5 2"><animateTransform attributeName="transform" dur="1.8s" repeatCount="indefinite" type="translate" values="0;10"/><animate fill="freeze" attributeName="d" begin="0.36s" dur="0.18s" to="M18 7c-2 0 -3 2 -5 2c-2 0 -3 -2 -5 -2c-2 0 -3 2 -5 2c-2 0 -3 -2 -5 -2c-2 0 -3 2 -5 2"/></path><path fill="#fff" fill-opacity="0.3" d="M18 23c-2 0 -3 2 -5 2c-2 0 -3 -2 -5 -2c-2 0 -3 2 -5 2c-2 0 -3 -2 -5 -2c-2 0 -3 2 -5 2v15h25Z"><animateTransform attributeName="transform" dur="1.8s" repeatCount="indefinite" type="translate" values="0;10"/><animate fill="freeze" attributeName="d" begin="0.36s" dur="0.18s" to="M18 7c-2 0 -3 2 -5 2c-2 0 -3 -2 -5 -2c-2 0 -3 2 -5 2c-2 0 -3 -2 -5 -2c-2 0 -3 2 -5 2v15h25Z"/></path><path d="M18 3l-2 18h-9l-2 -18h-5v21h24v-20Z"/></mask></defs><path fill="currentColor" d="M0 0h24v24H0z" mask="url(#SVGD6xQNbIZ)"/><path fill="none" stroke="currentColor" stroke-dasharray="62" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 3l-2 18h-9l-2 -18Z"><animate fill="freeze" attributeName="stroke-dashoffset" dur="0.36s" values="62;0"/></path></svg>'''

    HTML(html_to_tag(_))
    return


@app.cell
def _(Div, P):
    print(pretty(
        Div(P('hello', cls='greeting'), P('world'), id='main'),
        indent=2)
         )
    return


@app.cell
def _():
    def _rev_attrmap(k):
        match k:
            case 'class': return 'cls'
            case 'for': return '_for'
            case 'from': return '_from'
            case 'in': return '_in'
            case 'is': return '_is'
            case _: return k.replace('-', '_')

    def _tag_repr(self, _depth=0):
        name = self.tag.capitalize() if self.tag else 'Fragment'
        attrs = [f'{_rev_attrmap(k)}={v!r}' for k,v in self.attrs.items()]
        children = [repr(c) if isinstance(c, str) else c.__repr__(_depth+1) for c in self.children]
        head = f'{name}({", ".join(attrs)})' if attrs else f'{name}'
        if not children: return f'{head}()' if not attrs else head
        single = f'{head}({", ".join(children)})'
        if len(single) <= 80: return single
        pad = '    ' * (_depth + 1)
        return f'{head}(\n{",\n".join(pad + c for c in children)}\n{"    " * _depth})'

    Tag.__repr__ = _tag_repr

    html_to_tag('<div id="main">\n   <p class="greeting">hello</p>\n   <p>world</p>\n</div>')
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
