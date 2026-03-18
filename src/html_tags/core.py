import types, re
from collections import namedtuple
from html import escape

ALL_TAGS = ['A', 'Abbr', 'Address', 'Area', 'Article', 'Aside', 'Audio', 'B', 'Base', 'Bdi', 'Bdo', 'Blockquote', 'Body', 'Br', 'Button', 'Canvas', 'Caption', 'Cite', 'Code', 'Col', 'Colgroup', 'Data', 'Datalist', 'Dd', 'Del', 'Details', 'Dfn', 'Dialog', 'Div', 'Dl', 'Dt', 'Em', 'Embed', 'Fieldset', 'Figcaption', 'Figure', 'Footer', 'Form', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'Head', 'Header', 'Hgroup', 'Hr', 'Html', 'I', 'Iframe', 'Img', 'Input', 'Ins', 'Kbd', 'Label', 'Legend', 'Li', 'Link', 'Main', 'Map', 'Mark', 'Menu', 'Meta', 'Meter', 'Nav', 'Noscript', 'Object', 'Ol', 'Optgroup', 'Option', 'Output', 'P', 'Picture', 'Pre', 'Progress', 'Q', 'Rp', 'Rt', 'Ruby', 'S', 'Samp', 'Script', 'Search', 'Section', 'Select', 'Slot', 'Small', 'Source', 'Span', 'Strong', 'Style', 'Sub', 'Summary', 'Sup', 'Table', 'Tbody', 'Td', 'Template', 'Textarea', 'Tfoot', 'Th', 'Thead', 'Time', 'Title', 'Tr', 'Track', 'U', 'Ul', 'Var', 'Video', 'Wbr']
VOID_TAGS = frozenset({'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'})
RAW_TAGS = frozenset({'script', 'style'})
RAW_CLOSE_RE = re.compile('</(script|style)[\\s/>]', re.IGNORECASE)

class Tag(namedtuple('Tag', 'tag children attrs', defaults=((), {}))):
    def __str__(self): return to_html(self)
    __html__ = _repr_html_ = __str__
    def __call__(self, *c, **kw):
        return Tag(self.tag, self.children + tuple(flatten(c)), {**self.attrs, **kw})

def attrmap(k):
    match k:
        case 'cls'|'_class': return 'class'
        case '_for': return 'for'
        case _: return k

def render_attrs(d):
    out = ''
    for k,v in d.items():
        k = attrmap(k)
        v2 = str(v).replace('&', '&amp;').replace('<', '&lt;').replace('"', '&quot;')
        if v is True: out += f' {k}'
        elif v not in (False, None): out += f' {k}="{v2}"'
    return out

def is_void(t): return t.tag in VOID_TAGS

def is_raw(t): return t.tag in RAW_TAGS

def to_html(t, raw=False):
    if isinstance(t, str): return escape(t.replace('\x00', ''))
    if not hasattr(t, 'tag'): return escape(str(t).replace('\x00', ''))
    attrs = render_attrs(t.attrs) if t.attrs else ''
    if is_raw(t):
        inner = ''.join(str(c).replace('\x00', '') for c in t.children)
        validate_raw(t.tag, inner)
    else: inner = ''.join(to_html(c) for c in t.children)
    if not t.tag: return inner
    if is_void(t): return f'<{t.tag}{attrs}>'
    return f'<{t.tag}{attrs}>{inner}</{t.tag}>'

def mktag(name):
    def f(*c, **kw): return tag(name, *c, **kw)
    f.__name__ = name.capitalize()
    return f

class TagNS:
    def __getattr__(self, name): return mktag(name.lower())
    def export(self, *names): return [getattr(self, n) for n in names]

def Fragment(*c, **kw): return tag('', *c, **kw)

def flatten(c):
    for o in c:
        if o is None or o is False: continue
        if hasattr(o, 'tag'): yield o
        elif isinstance(o, (list, tuple, map, filter, types.GeneratorType)): yield from flatten(o)
        else: yield o

def tag(name, *c, **kw):
    children = tuple(flatten(o for o in c if not isinstance(o, dict)))
    attrs = {k:v for o in c if isinstance(o, dict) for k,v in o.items()}
    return Tag(name, children, {**attrs, **kw})

def validate_raw(tag, text):
    if RAW_CLOSE_RE.search(text): raise ValueError(f'Raw text in <{tag}> must not contain closing tag pattern: {text!r}')

def setup_tags(
    ns=None  # Optional namespace
):
    "Create tag constructors in the given namespace (or caller's globals)"
    import inspect
    if ns is None: ns = inspect.currentframe().f_back.f_globals
    H = TagNS()
    for name in ALL_TAGS: ns[name] = getattr(H, name)

def ui_head(color=None, scheme=None, density=None, size=None):
    "Emit <script> + <style> for the UI framework"
    attrs = {}
    if color: attrs['style'] = f'--_color:{color}'
    if scheme: attrs['data_ui_scheme'] = scheme
    if density: attrs['data_ui_density'] = density
    if size: attrs['data_ui_size'] = size
    return Fragment(
        tag('script', src="https://cdn.jsdelivr.net/gh/gnat/css-scope-inline@main/script.js"),
        
        tag('html', **attrs) if attrs else None)
