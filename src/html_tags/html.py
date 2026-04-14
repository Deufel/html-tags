import re
import types
import json
from .html import escape
from html.parser import HTMLParser
from collections import namedtuple, deque
from enum import Enum, auto

VOID = frozenset('area base br col embed hr img input link meta source track wbr'.split())
RAW = frozenset('script style'.split())
SVG_VOID = frozenset('stop set image use feBlend feColorMatrix feComposite feConvolveMatrix feDisplacementMap feDistantLight feDropShadow feFlood feFuncA feFuncB feFuncG feFuncR feGaussianBlur feImage feMergeNode feMorphology feOffset fePointLight feSpotLight feTile feTurbulence'.split())
SVG_CASE = {k.lower(): k for k in 'clipPath foreignObject linearGradient radialGradient textPath animateMotion animateTransform feBlend feColorMatrix feComponentTransfer feComposite feConvolveMatrix feDiffuseLighting feDisplacementMap feDistantLight feDropShadow feFlood feFuncA feFuncB feFuncG feFuncR feGaussianBlur feImage feMerge feMergeNode feMorphology feOffset fePointLight feSpecularLighting feSpotLight feTile feTurbulence'.split()}
MATH_VOID = frozenset('mprescripts none'.split())
MATH_CASE = {k.lower(): k for k in 'mfrac msqrt mroot mstyle merror mpadded mphantom mfenced menclose msub msup msubsup munder mover munderover mmultiscripts mtable mtr mlabeledtr mtd mstack mlongdiv msgroup msrow mscarries mscarry msline maction math mi mn mo mtext mspace ms'.split()}
NS_RULES = {NS.HTML: (VOID, False), NS.SVG: (SVG_VOID, True), NS.MATH: (MATH_VOID, False)}
SAFE_ATTR = re.compile('^[a-zA-Z_][\\w\\-:.]*$')
BAD_URL = re.compile('^(?:javascript:|vbscript:|data:(?!image/|application/json|text/plain))', re.I)
URL_ATTRS = frozenset('href src action formaction data poster'.split())
ATTR_MAP = {'cls': 'class', '_class': 'class', '_for': 'for', '_from': 'from', '_in': 'in', '_is': 'is'}
DS_EVENT = 'datastar-patch-elements'
DS_SIGNAL = 'datastar-merge-signals'
Frame = namedtuple('Frame', 'node depth ns_ctx', defaults=(0, None))

class NS(Enum):
        HTML = auto()
        SVG  = auto()
        MATH = auto()
class Safe(str):
        def __html__(self): return self
def flat(items):
        stack, out = deque(items), []
        while stack:
            o = stack.popleft()
            if o is None or o is False:                            continue
            if hasattr(o, '__html__'):                             out.append(o); continue
            if isinstance(o, (list, tuple, types.GeneratorType)):  stack.extendleft(reversed(list(o)))
            else:                                                  out.append(o)
        return tuple(out)
def parse(args, kw):
        attrs, children = {}, []
        for o in args:
            if isinstance(o, dict): attrs.update(o)
            else:                   children.append(o)
        attrs.update({ATTR_MAP.get(k, k.rstrip('_').replace('_', '-')): v for k, v in kw.items()})
        return flat(children), attrs
def attrs(d):
        out = []
        for k, v in d.items():
            if not SAFE_ATTR.match(k):                   raise ValueError(f'bad attr: {k!r}')
            if k in URL_ATTRS and BAD_URL.match(str(v)): raise ValueError(f'bad url: {k}')
            if   v is True:              out.append(f' {k}')
            elif v not in (False, None): out.append(f' {k}="{escape(str(v), quote=True)}"')
        return ''.join(out)
def render(t, indent=None):
        stack, out = [Frame(t, 0, None)], []

        while stack:
            node, depth, ns_ctx = stack.pop()

            if hasattr(node, '__html__') and not isinstance(node, Tag):
                out.append(node.__html__()); continue
            if not isinstance(node, Tag):
                out.append(escape(str(node))); continue

            match node.ns:
                case NS.SVG:  ns = NS.SVG
                case NS.HTML: ns = NS.HTML
                case NS.MATH: ns = NS.MATH
                case _:       ns = ns_ctx or NS.HTML

            voids, sc_all = NS_RULES[ns]
            a, tag        = attrs(node.attrs), node.tag

            if not tag:
                for c in reversed(node.children):
                    stack.append(Frame(c, depth, ns_ctx))
                continue

            if tag in RAW:
                out.append(f'<{tag}{a}>' + ''.join(str(c) for c in node.children) + f'</{tag}>'); continue

            if tag in voids:
                out.append(f'<{tag}{a} />' if sc_all else f'<{tag}{a}>'); continue

            if not node.children and sc_all:
                out.append(f'<{tag}{a} />'); continue

            match tag:
                case 'svg':           child_ctx = NS.SVG
                case 'math':          child_ctx = NS.MATH
                case 'foreignObject': child_ctx = NS.HTML
                case _:               child_ctx = ns

            pre = '<!DOCTYPE html>\n' if tag == 'html' else ''
            if indent:
                pad  = ' ' * (indent * depth)
                pad1 = ' ' * (indent * (depth + 1))
                out.append(f'{pre}{pad}<{tag}{a}>\n')
                stack.append(Frame(Safe(f'{pad}</{tag}>'), depth, ns_ctx))
                for c in reversed(node.children):
                    stack.append(Frame(Safe('\n'),  depth + 1, child_ctx))
                    stack.append(Frame(c,           depth + 1, child_ctx))
                    stack.append(Frame(Safe(pad1),  depth + 1, child_ctx))
            else:
                out.append(f'{pre}<{tag}{a}>')
                stack.append(Frame(Safe(f'</{tag}>'), depth, ns_ctx))
                for c in reversed(node.children):
                    stack.append(Frame(c, depth + 1, child_ctx))

        return ''.join(out)
class Tag(namedtuple('TagBase', 'tag ns children attrs', defaults=(None, (), {}))):
        def __call__(self, *c, **kw):
            ch, a = parse(c, kw)
            return self._replace(children=self.children + ch, attrs={**self.attrs, **a})
        def __str__(self):  return render(self)
        def __html__(self): return render(self)

def pretty(t):
    return render(t, indent=2)

def Fragment(*c, **kw):
    ch, a = parse(c, kw)
    return Tag('', None, ch, a)

def mktag(name, ns=None):
    match ns:
        case 'svg':  resolved = NS.SVG;  name = SVG_CASE.get(name.lower(),  name.lower())
        case 'math': resolved = NS.MATH; name = MATH_CASE.get(name.lower(), name.lower())
        case 'html': resolved = NS.HTML; name = name.lower()
        case _:      resolved = None;    name = name.lower()
    def make(*c, **kw):
        ch, a = parse(c, kw)
        return Tag(name, resolved, ch, a)
    return make

def html_to_tag(s):
    stack, root = [[]], []
    class P(HTMLParser):
        def handle_starttag(self, tag, attrs):
            name = SVG_CASE.get(tag.lower(), tag.lower())
            d    = {k: (v if v is not None else True) for k, v in attrs}
            if name in VOID or name in SVG_VOID: stack[-1].append(Tag(name, None, (), d))
            else: stack.append([]); root.append((name, d))
        def handle_endtag(self, tag):
            name = SVG_CASE.get(tag.lower(), tag.lower())
            if name in VOID or name in SVG_VOID: return
            children = tuple(stack.pop())
            t, d     = root.pop()
            stack[-1].append(Tag(t, None, children, d))
        def handle_data(self, data):
            if data.strip(): stack[-1].append(data.strip())
    P().feed(s)
    res = stack[0]
    return res[0] if len(res) == 1 else Fragment(*res)

def sse_patch(t, pretty=False):
    html  = render(t, indent=2) if pretty else render(t)
    lines = html.splitlines() if pretty else [html]
    data  = ''.join(f"data: elements {line}\n" for line in lines)
    return f"event: {DS_EVENT}\n{data}\n"

def sse_signal(data):
    return f"event: {DS_SIGNAL}\ndata: signals {json.dumps(data)}\n\n"

class NS_Accessor:
    def __init__(self, ns): self.ns = ns
    def __getattr__(self, name): return mktag(name, self.ns)
