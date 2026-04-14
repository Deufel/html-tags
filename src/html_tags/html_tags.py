import re
import types
from .html import escape
from html.parser import HTMLParser
from collections import namedtuple
from urllib.parse import quote

VOID = frozenset('area base br col embed hr img input link meta source track wbr'.split())
RAW = frozenset('script style'.split())
SVG_VOID = frozenset('stop set image use feBlend feColorMatrix feComposite feConvolveMatrix feDisplacementMap feDistantLight feDropShadow feFlood feFuncA feFuncB feFuncG feFuncR feGaussianBlur feImage feMergeNode feMorphology feOffset fePointLight feSpotLight feTile feTurbulence'.split())
SVG_CASE = {k.lower(): k for k in 'clipPath foreignObject linearGradient radialGradient textPath animateMotion animateTransform feBlend feColorMatrix feComponentTransfer feComposite feConvolveMatrix feDiffuseLighting feDisplacementMap feDistantLight feDropShadow feFlood feFuncA feFuncB feFuncG feFuncR feGaussianBlur feImage feMerge feMergeNode feMorphology feOffset fePointLight feSpecularLighting feSpotLight feTile feTurbulence'.split()}
NS = {'html': (VOID, False), 'svg': (SVG_VOID, True)}
SAFE_ATTR = re.compile('^[a-zA-Z_][\\w\\-:.]*$')
BAD_URL = re.compile('^(?:javascript:|vbscript:|data:(?!image/|application/json|text/plain))', re.I)
URL_ATTRS = frozenset('href src action formaction data poster'.split())
ATTR_MAP = {'cls': 'class', '_class': 'class', '_for': 'for', '_from': 'from', '_in': 'in', '_is': 'is'}
DS_EVENT = 'datastar-patch-elements'
DS_SIGNAL = 'datastar-merge-signals'

class Safe(str):
        def __html__(self): return self
def _flat(items):
        stack, out = list(items), []
        while stack:
            o = stack.pop(0)
            if o is None or o is False:                            continue
            if hasattr(o, '__html__'):                             out.append(o); continue
            if isinstance(o, (list, tuple, types.GeneratorType)):  stack[:0] = list(o)
            else:                                                  out.append(o)
        return tuple(out)
def _parse(args, kw):
        attrs, children = {}, []
        for o in args:
            if isinstance(o, dict): attrs.update(o)
            else:                   children.append(o)
        attrs.update({ATTR_MAP.get(k, k.rstrip('_').replace('_', '-')): v for k, v in kw.items()})
        return _flat(children), attrs
def _attrs(d):
        out = []
        for k, v in d.items():
            if not SAFE_ATTR.match(k):                   raise ValueError(f'bad attr: {k!r}')
            if k in URL_ATTRS and BAD_URL.match(str(v)): raise ValueError(f'bad url: {k}')
            if   v is True:              out.append(f' {k}')
            elif v not in (False, None): out.append(f' {k}="{escape(str(v), quote=True)}"')
        return ''.join(out)
def render(t, indent=None):
        stack, out = [(t, 0)], []
        while stack:
            node, depth = stack.pop()
            if hasattr(node, '__html__') and not isinstance(node, Tag):
                out.append(node.__html__()); continue
            if not isinstance(node, Tag):
                out.append(escape(str(node))); continue
            voids, sc_all = NS.get(node.ns, (VOID, False))
            a, tag = _attrs(node.attrs), node.tag
            if not tag:
                for c in reversed(node.children): stack.append((c, depth))
                continue
            if tag in RAW:
                out.append(f'<{tag}{a}>' + ''.join(str(c) for c in node.children) + f'</{tag}>'); continue
            if tag in voids:
                out.append(f'<{tag}{a} />' if sc_all else f'<{tag}{a}>'); continue
            if not node.children and sc_all:
                out.append(f'<{tag}{a} />'); continue
            pre = '<!DOCTYPE html>\n' if tag == 'html' else ''
            if indent:
                pad  = '\n' + ' ' * (indent * depth)
                pad1 = '\n' + ' ' * (indent * (depth + 1))
                out.append(f'{pre}{pad}<{tag}{a}>')
            else:
                out.append(f'{pre}<{tag}{a}>')
            stack.append((Safe(f'{pad}</{tag}>' if indent else f'</{tag}>'), depth))
            for c in reversed(node.children): stack.append((c, depth + 1))
        return ''.join(out).strip() if indent else ''.join(out)
class Tag(namedtuple('TagBase', 'tag ns children attrs', defaults=(None, (), {}))):
        def __call__(self, *c, **kw):
            ch, a = _parse(c, kw)
            return self._replace(children=self.children + ch, attrs={**self.attrs, **a})
        def __str__(self):  return render(self)
        def __html__(self): return render(self)

def flat(items):
    """Re-export _flat as public flat."""
    return _flat(items)

def parse(args, kw):
    """Re-export _parse as public parse."""
    return _parse(args, kw)

def pretty(t):
    return render(t, indent=2)

def Fragment(*c, **kw):
    ch, a = _parse(c, kw)
    return Tag('', None, ch, a)

def html_to_tag(s):
    stack, root = [[]], []
    class P(HTMLParser):
        def handle_starttag(self, tag, attrs):
            name = SVG_CASE.get(tag.lower(), tag.lower())
            d = {k: (v if v is not None else True) for k, v in attrs}
            if name in VOID or name in SVG_VOID: stack[-1].append(Tag(name, None, (), d))
            else: stack.append([]); root.append((name, d))
        def handle_endtag(self, tag):
            name = SVG_CASE.get(tag.lower(), tag.lower())
            if name in VOID or name in SVG_VOID: return
            children = tuple(stack.pop())
            t, d = root.pop()
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
    import json
    return f"event: {DS_SIGNAL}\ndata: signals {json.dumps(data)}\n\n"
