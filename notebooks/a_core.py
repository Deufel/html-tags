import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")

with app.setup:


    import types, re
    from collections import namedtuple
    from html import escape

    ALL_TAGS = [ 'A','Abbr','Address','Area','Article','Aside','Audio', 'B','Base','Bdi','Bdo','Blockquote','Body','Br','Button', 'Canvas','Caption','Cite','Code','Col','Colgroup', 'Data','Datalist','Dd','Del','Details','Dfn','Dialog','Div','Dl','Dt', 'Em','Embed', 'Fieldset','Figcaption','Figure','Footer','Form', 'H1','H2','H3','H4','H5','H6','Head','Header','Hgroup','Hr','Html', 'I','Iframe','Img','Input','Ins', 'Kbd', 'Label','Legend','Li','Link', 'Main','Map','Mark','Menu','Meta','Meter', 'Nav','Noscript', 'Object','Ol','Optgroup','Option','Output', 'P','Picture','Pre','Progress', 'Q', 'Rp','Rt','Ruby', 'S','Samp','Script','Search','Section','Select','Slot','Small','Source','Span','Strong','Style','Sub','Summary','Sup', 'Table','Tbody','Td','Template','Textarea','Tfoot','Th','Thead','Time','Title','Tr','Track', 'U','Ul', 'Var','Video', 'Wbr']

    VOID_TAGS = frozenset({"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"})
    RAW_TAGS = frozenset({"script", "style"})
    RAW_CLOSE_RE = re.compile(r'</(script|style)[\s/>]', re.IGNORECASE)
    SAFE_ATTR_RE = re.compile(r'^[a-zA-Z_][\w\-:.]*$')
    URL_ATTRS = frozenset({'href', 'src', 'action', 'formaction', 'data', 'poster', 'codebase', 'cite', 'background', 'dynsrc', 'lowsrc'})
    DANGEROUS_URL_RE = re.compile(r'^\s*(javascript|vbscript|data)\s*:', re.IGNORECASE)


@app.function
def setup_tags(
    ns=None  # Optional namespace
):
    """Create tag constructors in the given namespace (or caller's globals)"""
    import inspect
    if ns is None: ns = inspect.currentframe().f_back.f_globals
    for name in ALL_TAGS:
        n = name.lower()
        if n in VOID_TAGS: mode = 'void'
        elif n in RAW_TAGS: mode = 'raw'
        else: mode = 'normal'
        ns[name] = mktag(n, mode)


@app.function
def mktag(
    name,                    # HTML tag name (e.g. 'div', 'p')
    mode='normal',           # 'normal', 'void', or 'raw'
    self_closing=False       # Render as self-closing (<tag />) when empty?
):
    "Create a tag constructor function for the given element name"
    def f(*c, **kw):
        attrs = {k:v for o in c if isinstance(o, dict) for k,v in o.items()}
        children = tuple(o for o in c if not isinstance(o, dict))
        return Tag(name, children, {**attrs, **{attrmap(k):v for k,v in kw.items()}}, mode, self_closing)
    f.__name__ = name.capitalize()
    return f


@app.class_definition
class Tag(namedtuple('Tag', 'tag children attrs mode self_closing', defaults=((), {}, 'normal', False))):
    "An HTML element with a tag name, children, and attributes"
    def __new__(cls,
        tag,                  # HTML tag name (e.g. 'div', 'p', '')
        children=(),          # Child elements and/or text nodes
        attrs={},             # Attribute key-value pairs
        mode='normal',        # 'normal', 'void', or 'raw'
        self_closing=False    # Render as self-closing (<tag />) when empty?
    ):
        children = tuple(flatten(children))
        if tag:
            for child in children:
                if hasattr(child, 'tag') and child.tag == 'html':
                    raise ValueError('<html> cannot be nested inside another element')
        if mode == 'void' and children: raise ValueError(f'Void element <{tag}> cannot have children')
        if mode == 'raw':
            for child in children:
                if hasattr(child, 'tag'): raise ValueError(f'Raw element <{tag}> cannot contain nested tags')
        return super().__new__(cls, tag, children, attrs, mode, self_closing)
    def __str__(self) -> str: return globals()['to_html'](self)
    __html__ = _repr_html_ = __str__
    def __call__(self,
        *c,    # Additional children to append
        **kw   # Additional attributes to merge
    ) -> 'Tag':
        "Create a new Tag with appended children and merged attributes"
        return Tag(self.tag, self.children + tuple(flatten(c)), {**self.attrs, **{attrmap(k):v for k,v in kw.items()}}, self.mode, self.self_closing)


@app.function
#| internal

def attrmap(
    k: str  # Python attribute name to map
) -> str:   # HTML-safe attribute name
    """Map Python-friendly attribute names to their HTML equivalents (e.g. 'cls' → 'class', '_' → '-')."""
    match k:
        case 'cls'|'_class': return 'class'
        case '_for': return 'for'
        case '_from': return 'from'
        case '_in': return 'in'
        case '_is': return 'is'
        case _: return k.replace('_', '-')


@app.function
#| internal

def render_attrs(
    d: dict  # Attribute key-value pairs (e.g. {"class": "main", "id": "app"})
) -> str:    # Rendered HTML attribute string (e.g. ' class="main" id="app"')
    '''Render a dict of attributes to an HTML attribute string. Escapes values, validates keys and URL schemes.'''
    out = ''
    for k,v in d.items():
        if not SAFE_ATTR_RE.match(k): raise ValueError(f'Unsafe attribute name: {k!r}')
        v2 = str(v).replace('&', '&amp;').replace('<', '&lt;').replace('"', '&quot;')
        if k in URL_ATTRS and DANGEROUS_URL_RE.match(str(v)): raise ValueError(f'Dangerous URL scheme in {k}: {str(v)[:60]!r}')
        if v is True: out += f' {k}'
        elif v is not False and v is not None: out += f' {k}="{v2}"'
    return out


@app.function
#| internal
def is_void(t): return t.mode == 'void'


@app.function
#| internal
def is_raw(t): return t.mode == 'raw'


@app.function
#| internal
def is_root(t): return t.tag == 'html'


@app.function
def to_html(
    t  # Tag tree, string, or any object
) -> str:  # HTML string, with DOCTYPE prepended for root <html>
    "Convert a tag tree to an HTML string. Escapes text, validates raw tags, and prepends DOCTYPE for root <html>."
    if hasattr(t, '__html__') and not isinstance(t, Tag): return t.__html__()
    if isinstance(t, str): return escape(t.replace('\x00', ''))
    if not hasattr(t, 'tag'): return escape(str(t).replace('\x00', ''))
    attrs = render_attrs(t.attrs) if t.attrs else ''
    if is_raw(t):
        inner = ''.join(str(c).replace('\x00', '') for c in t.children)
        validate_raw(t.tag, inner)
    else: inner = ''.join(to_html(c) for c in t.children)
    if not t.tag: return inner
    if is_void(t): return f'<{t.tag}{attrs} />' if t.self_closing else f'<{t.tag}{attrs}>'
    if not inner and t.self_closing: return f'<{t.tag}{attrs} />'
    if is_root(t): return f'<!DOCTYPE html>\n<{t.tag}{attrs}>{inner}</{t.tag}>'
    return f'<{t.tag}{attrs}>{inner}</{t.tag}>'


@app.function
#| internal

def Fragment(
    *c,    # Children to render without a wrapping element
    **kw   # Attributes (passed through but rarely used)
) -> Tag:
    "Create a virtual grouping node. Renders its children without any wrapping HTML element."
    return Tag('', c, {attrmap(k):v for k,v in kw.items()})


@app.function
#| internal

def flatten(c):
    for o in c:
        if o is None or o is False: continue
        if hasattr(o, 'tag'): yield o
        elif isinstance(o, (list, tuple, map, filter, types.GeneratorType)): yield from flatten(o)
        else: yield o


@app.function
#| internal

def validate_raw(
    tag: str,   # Tag name (e.g. 'script', 'style')
    text: str   # Raw text content to validate
) -> None:      # Raises ValueError if closing tag pattern found
    """Ensure raw text content does not contain a closing tag injection (e.g. </script>)."""
    if RAW_CLOSE_RE.search(text): raise ValueError(f'Raw text in <{tag}> must not contain closing tag pattern: {text!r}')


@app.function
def pretty(
    t,                          # Tag tree, string, or any object
    indent: int=2,              # Spaces per indentation level
    indent_script: bool=False,  # Indent <script> content?
    indent_style: bool=True,    # Indent <style> content?
    _depth: int=0               # Internal: current nesting depth (for indentation only)
) -> str:                       # Indented HTML string for debugging
    '''Pretty-print an HTML tag tree with indentation. Not for production use — may alter whitespace-sensitive rendering.'''
    if hasattr(t, '__html__') and not isinstance(t, Tag): return t.__html__()
    pad = ' ' * (indent * _depth)
    pad1 = ' ' * (indent * (_depth + 1))
    if isinstance(t, str): return pad + escape(t.replace('\x00', ''))
    if not hasattr(t, 'tag'): return pad + escape(str(t).replace('\x00', ''))
    attrs = render_attrs(t.attrs) if t.attrs else ''
    if is_void(t): return f'{pad}<{t.tag}{attrs} />' if t.self_closing else f'{pad}<{t.tag}{attrs}>'
    if is_raw(t):
        inner = ''.join(str(c).replace('\x00', '') for c in t.children)
        validate_raw(t.tag, inner)
        should_indent = (t.tag == 'style' and indent_style) or (t.tag == 'script' and indent_script)
        if should_indent and inner.strip():
            lines = inner.strip().splitlines()
            inner = '\n'.join(pad1 + line for line in lines)
            return f'{pad}<{t.tag}{attrs}>\n{inner}\n{pad}</{t.tag}>'
        if not inner: return f'{pad}<{t.tag}{attrs}></{t.tag}>'
        return f'{pad}<{t.tag}{attrs}>{inner}</{t.tag}>'
    if not t.tag: return '\n'.join(pretty(c, indent, indent_script, indent_style, _depth) for c in t.children)
    if not t.children: return f'{pad}<{t.tag}{attrs} />' if t.self_closing else f'{pad}<{t.tag}{attrs}></{t.tag}>'
    if len(t.children) == 1 and isinstance(t.children[0], str):
        inner = escape(t.children[0].replace('\x00', ''))
        return f'{pad}<{t.tag}{attrs}>{inner}</{t.tag}>'
    prefix = f'<!DOCTYPE html>\n' if is_root(t) else ''
    children = '\n'.join(pretty(c, indent, indent_script, indent_style, _depth + 1) for c in t.children)
    return f'{prefix}{pad}<{t.tag}{attrs}>\n{children}\n{pad}</{t.tag}>'


@app.function
#| internal 

def dunder_getattr(
    name: str     # Custom html tag user generated
):
    """ Import html custom tags directly from module """
    if name[0].isupper(): return mktag(name.lower().replace('_', '-'))
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Exploratory
    """)
    return


@app.cell
def _():
    # a = Tag('div', 'hello', cls='foo')
    # b = mktag('div')('hello', cls='foo')
    # c = TagNS().div('hello', cls='foo')
    # print(f"{a = }\n{b = }\n{c = }")
    # print(a==b==c)
    a = Tag('div', ('hello',), {'class':'foo'})
    b = mktag('div')('hello', cls='foo')
    print(f"{a = }\n{b = }")
    print(a == b)

    return


@app.cell
def _(Div, H3, Img, P):
    setup_tags()
    _card = lambda title,text,img: Div(
        Img(src=img, alt=title, style='width:100%;border-radius:8px'),
        H3(title), P(text),
        style='border:1px solid #ddd;padding:16px;border-radius:12px;width:200px;display:inline-block;margin:8px')

    Div(
        _card('Mountains', 'Beautiful peaks', 'https://picsum.photos/200/120?1'),
        _card('Ocean', 'Calm waters', 'https://picsum.photos/200/120?2'),
        _card('Forest', 'Tall trees', 'https://picsum.photos/200/120?3'))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Playground
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Future

    - pull in scoped css auto
    - Datastar Demo
    - Type & Space & Color Extra
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Scoped CSS
    ```js
    // 🌘 CSS Scope Inline (https://github.com/gnat/css-scope-inline)
    window.cssScopeCount ??= 1
    window.cssScope ??= new MutationObserver(mutations => {
    	document?.body?.querySelectorAll('style:not([ready])').forEach(node => {
    		var scope = 'me__'+(window.cssScopeCount++)
    		node.parentNode.classList.add(scope)
    		node.textContent = node.textContent
    		.replace(/(?:^|\.|(\s|[^a-zA-Z0-9\-\_]))(me|this|self)(?![a-zA-Z])/g, '$1.'+scope)
    		.replace(/((@keyframes|animation:|animation-name:)[^{};]*)\.me__/g, '$1me__')
    		node.setAttribute('ready', '')
    	})
    }).observe(document.documentElement, {childList: true, subtree: true})
    ```
    """)
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
