import types, re
from collections import namedtuple
from html import escape

ALL_TAGS = ['A', 'Abbr', 'Address', 'Area', 'Article', 'Aside', 'Audio', 'B', 'Base', 'Bdi', 'Bdo', 'Blockquote', 'Body', 'Br', 'Button', 'Canvas', 'Caption', 'Cite', 'Code', 'Col', 'Colgroup', 'Data', 'Datalist', 'Dd', 'Del', 'Details', 'Dfn', 'Dialog', 'Div', 'Dl', 'Dt', 'Em', 'Embed', 'Fieldset', 'Figcaption', 'Figure', 'Footer', 'Form', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'Head', 'Header', 'Hgroup', 'Hr', 'Html', 'I', 'Iframe', 'Img', 'Input', 'Ins', 'Kbd', 'Label', 'Legend', 'Li', 'Link', 'Main', 'Map', 'Mark', 'Menu', 'Meta', 'Meter', 'Nav', 'Noscript', 'Object', 'Ol', 'Optgroup', 'Option', 'Output', 'P', 'Picture', 'Pre', 'Progress', 'Q', 'Rp', 'Rt', 'Ruby', 'S', 'Samp', 'Script', 'Search', 'Section', 'Select', 'Slot', 'Small', 'Source', 'Span', 'Strong', 'Style', 'Sub', 'Summary', 'Sup', 'Table', 'Tbody', 'Td', 'Template', 'Textarea', 'Tfoot', 'Th', 'Thead', 'Time', 'Title', 'Tr', 'Track', 'U', 'Ul', 'Var', 'Video', 'Wbr']
VOID_TAGS = frozenset({'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'})
RAW_TAGS = frozenset({'script', 'style'})
RAW_CLOSE_RE = re.compile('</(script|style)[\\s/>]', re.IGNORECASE)
SAFE_ATTR_RE = re.compile('^[a-zA-Z_][\\w\\-:.]*$')
URL_ATTRS = frozenset({'href', 'src', 'action', 'formaction', 'data', 'poster', 'codebase', 'cite', 'background', 'dynsrc', 'lowsrc'})
DANGEROUS_URL_RE = re.compile('^\\s*(javascript|vbscript|data)\\s*:', re.IGNORECASE)


class Tag(namedtuple('Tag', 'tag children attrs', defaults=((), {}))):
    "An HTML element with a tag name, children, and attributes"
    def __str__(self) -> str: return to_html(self)
    __html__ = _repr_html_ = __str__
    def __call__(self,
        *c,    # Additional children to append
        **kw   # Additional attributes to merge
    ) -> 'Tag': # New Tag with combined children and attributes
        "Create a new Tag with appended children and merged attributes"
        return Tag(self.tag, self.children + tuple(flatten(c)), {**self.attrs, **kw})


def attrmap(
    k: str  # Python attribute name to map
) -> str:   # HTML-safe attribute name
    """Map Python-friendly attribute names to their HTML equivalents (e.g. 'cls' → 'class')."""
    match k:
        case 'cls'|'_class': return 'class'
        case '_for': return 'for'
        case _: return k


def render_attrs(
    d: dict  # Attribute key-value pairs (e.g. {"class": "main", "id": "app"})
) -> str:    # Rendered HTML attribute string (e.g. ' class="main" id="app"')
    """Render a dict of attributes to an HTML attribute string. Escapes values, validates keys and URL schemes."""
    out = ''
    for k,v in d.items():
        k = attrmap(k)
        if not SAFE_ATTR_RE.match(k): raise ValueError(f'Unsafe attribute name: {k!r}')
        v2 = str(v).replace('&', '&amp;').replace('<', '&lt;').replace('"', '&quot;')
        if k in URL_ATTRS and DANGEROUS_URL_RE.match(str(v)): raise ValueError(f'Dangerous URL scheme in {k}: {str(v)[:60]!r}')
        if v is True: out += f' {k}'
        elif v not in (False, None): out += f' {k}="{v2}"'
    return out

def is_void(t): return t.tag in VOID_TAGS

def is_raw(t): return t.tag in RAW_TAGS

def is_root(t): return t.tag == 'html'

def to_html(
    t  # Tag tree, string, or any object
) -> str:  # HTML string, with DOCTYPE prepended for root <html>
    "Convert a tag tree to an HTML string. Escapes text, validates raw tags, and prepends DOCTYPE for root <html>."
    if isinstance(t, str): return escape(t.replace('\x00', ''))
    if not hasattr(t, 'tag'): return escape(str(t).replace('\x00', ''))
    attrs = render_attrs(t.attrs) if t.attrs else ''
    if is_raw(t):
        inner = ''.join(str(c).replace('\x00', '') for c in t.children)
        validate_raw(t.tag, inner)
    else: inner = ''.join(to_html(c) for c in t.children)
    if not t.tag: return inner
    if is_void(t): return f'<{t.tag}{attrs}>'
    if is_root(t): return f'<!DOCTYPE html>\n<{t.tag}{attrs}>{inner}</{t.tag}>'
    return f'<{t.tag}{attrs}>{inner}</{t.tag}>'


def mktag(name):
    def f(*c, **kw): return tag(name, *c, **kw)
    f.__name__ = name.capitalize()
    return f


class TagNS:
    def __getattr__(self, name): return mktag(name.lower())
    def export(self, *names): return [getattr(self, n) for n in names]


def Fragment(
    *c,    # Children to render without a wrapping element
    **kw   # Attributes (passed through but rarely used)
) -> Tag:  # Tag with empty name — renders children only, no outer element
    """Create a virtual grouping node. Renders its children without any wrapping HTML element."""
    return tag('', *c, **kw)


def flatten(c):
    for o in c:
        if o is None or o is False: continue
        if hasattr(o, 'tag'): yield o
        elif isinstance(o, (list, tuple, map, filter, types.GeneratorType)): yield from flatten(o)
        else: yield o


def tag(
    name,  # HTML tag name (e.g. 'div', 'p', '')
    *c,    # Children and/or attribute dicts, intermixed
    **kw   # Additional attributes as keyword arguments
) -> Tag:  # Named tuple of (tag, children, attrs)
    "Create a Tag from a name, positional children/attr dicts, and keyword attrs. Dicts in *c are merged as attributes; all other values become children."
    children = tuple(flatten(o for o in c if not isinstance(o, dict)))
    if name:
        for child in children:
            if hasattr(child, 'tag') and child.tag == 'html': raise ValueError('<html> cannot be nested inside another element')
    attrs = {k:v for o in c if isinstance(o, dict) for k,v in o.items()}
    return Tag(name, children, {**attrs, **kw})


def validate_raw(
    tag: str,   # Tag name (e.g. 'script', 'style')
    text: str   # Raw text content to validate
) -> None:      # Raises ValueError if closing tag pattern found
    """Ensure raw text content does not contain a closing tag injection (e.g. </script>)."""
    if RAW_CLOSE_RE.search(text): raise ValueError(f'Raw text in <{tag}> must not contain closing tag pattern: {text!r}')

def setup_tags(
    ns=None  # Optional namespace
):
    """Create tag constructors in the given namespace (or caller's globals)"""
    import inspect
    if ns is None: ns = inspect.currentframe().f_back.f_globals
    H = TagNS()
    for name in ALL_TAGS: ns[name] = getattr(H, name)

def pretty(
    t,                          # Tag tree, string, or any object
    indent: int=2,              # Spaces per indentation level
    indent_script: bool=False,  # Indent <script> content?
    indent_style: bool=True,    # Indent <style> content?
    _depth: int=0               # Internal: current nesting depth (for indentation only)
) -> str:                       # Indented HTML string for debugging
    "Pretty-print an HTML tag tree with indentation. Not for production use — may alter whitespace-sensitive rendering."
    pad = ' ' * (indent * _depth)
    pad1 = ' ' * (indent * (_depth + 1))
    if isinstance(t, str): return pad + escape(t.replace('\x00', ''))
    if not hasattr(t, 'tag'): return pad + escape(str(t).replace('\x00', ''))
    attrs = render_attrs(t.attrs) if t.attrs else ''
    if is_void(t): return f'{pad}<{t.tag}{attrs}>'
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
    if not t.children: return f'{pad}<{t.tag}{attrs}></{t.tag}>'
    if len(t.children) == 1 and isinstance(t.children[0], str):
        inner = escape(t.children[0].replace('\x00', ''))
        return f'{pad}<{t.tag}{attrs}>{inner}</{t.tag}>'
    prefix = f'<!DOCTYPE html>\n' if is_root(t) else ''
    children = '\n'.join(pretty(c, indent, indent_script, indent_style, _depth + 1) for c in t.children)
    return f'{prefix}{pad}<{t.tag}{attrs}>\n{children}\n{pad}</{t.tag}>'
