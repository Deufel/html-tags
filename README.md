# html-tags

![PyPI version](https://img.shields.io/pypi/v/html-tags)

> [!WARNING]
> Under active development — Apr 2026

# html_tags

A minimal, zero-dependency Python DSL for HTML, SVG, and MathML. Built around a single idea: **a tag is a closure**. No classes, no templates, no mutation — just functions that return functions that render to strings.

## Install

pip install html-tags

## The whole API in ten seconds

```python
from html_tags import div, p, h1, ul, li, render

page = div(cls="card")(
    h1("Hello"),
    p("A minimal HTML DSL."),
    ul(li(x) for x in ["red", "blue", "green"]),
)

print(render(page))
```

Any name you import from `html_tags` becomes a tag constructor — `from html_tags import my_custom_component` works, no pre-registration. Underscores become hyphens (`data_list` → `<data-list>`), trailing underscores are stripped (`input_` → `<input>`).

## The attribute rule

There are two channels for attributes:

- **Keyword arguments** are Pythonified: `cls` → `class`, `_for` → `for`, `data_test_id` → `data-test-id`, trailing `_` stripped.
- **Dict arguments** pass through verbatim. Use a dict for anything that isn't a valid Python identifier.

```python
# kwargs: friendly Python names
div(cls="btn", data_test_id="save")

# dict: anything with colons, dots, or reserved names
div({"data-on:click": "@post('/save')"})

# mix freely — they merge
form({"data-signals": "{count: 0}"}, cls="counter")(
    input_({"data-bind:name": True}, type="text"),
)
```

This rule is why the library handles Datastar 1.0 attributes (`data-on:click__debounce.500ms.leading`), XML namespaces (`xlink:href`), and any other non-identifier attribute name without special cases.

## Purity: extension never mutates

```python
shell = div(cls="card")
a = shell(p("branch A"))
b = shell(p("branch B"))

# shell is unchanged. a and b are independent.
```

Each call returns a new closure. Reuse shells freely across requests, components, whatever — they're immutable values.

## Namespace handling

The library automatically switches rendering rules for SVG, MathML, and back to HTML inside `<foreignObject>`. You write the tags; namespacing, `xmlns`, and void-element conventions just work.

### SVG

```python
from html_tags import svg, circle, rect, render

logo = svg(
    circle(cx="50", cy="50", r="40", fill="steelblue"),
    rect(x="30", y="30", width="40", height="40", fill="white"),
    viewBox="0 0 100 100", width="200",
)
print(render(logo))
```

Renders (note the automatic `xmlns` on the root and self-closing void elements):

```html
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="200">
  <circle cx="50" cy="50" r="40" fill="steelblue" />
  <rect x="30" y="30" width="40" height="40" fill="white" />
</svg>
```

### MathML

```python
from html_tags import math, mrow, msup, mi, mn, mo, render

# a² + b² = c²
eq = math(mrow(
    msup(mi("a"), mn("2")), mo("+"),
    msup(mi("b"), mn("2")), mo("="),
    msup(mi("c"), mn("2")),
))
print(render(eq))
```

Renders with the correct MathML xmlns and namespace-appropriate void rules:

```html
<math xmlns="http://www.w3.org/1998/Math/MathML">
  <mrow>
    <msup><mi>a</mi><mn>2</mn></msup>
    <mo>+</mo>
    ...
  </mrow>
</math>
```

### HTML inside SVG via `foreignObject`

This is the interesting case. `<foreignObject>` embeds real HTML inside an SVG. The void-element rules are different in the two namespaces (`<br>` self-closes in SVG, not in HTML) — and `html_tags` switches back to HTML mode for the subtree automatically.

```python
from html_tags import div, svg, circle, foreignObject, p, input_, br, strong, render

doc = div(
    svg(
        circle(cx="50", cy="50", r="40", fill="steelblue"),
        foreignObject(
            div(
                p("Real HTML, including ", input_(type="text", placeholder="type here")),
                br(),
                strong("bold text"),
            ),
            x="20", y="20", width="60", height="60",
        ),
        viewBox="0 0 100 100", width="200",
    ),
)
print(render(doc))
```

Output — note how `<circle />` self-closes (SVG) but `<input>` and `<br>` inside the `foreignObject` use HTML's void conventions:

```html
<div>
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="200">
    <circle cx="50" cy="50" r="40" fill="steelblue" />
    <foreignObject x="20" y="20" width="60" height="60">
      <div>
        <p>Real HTML, including <input type="text" placeholder="type here"></p>
        <br>
        <strong>bold text</strong>
      </div>
    </foreignObject>
  </svg>
</div>
```

Three layers of namespace, one function call per tag, no configuration.

## Dynamic trees

Build from data — the closure model handles arbitrary depth because it's just normal Python recursion:

```python
import html_tags as h

def build(node):
    if isinstance(node, str):
        return node
    ctor = getattr(h, node["type"])
    children = [build(c) for c in node.get("children", [])]
    return ctor(*children, **node.get("attrs", {}))

tree = {"type": "ul", "children": [
    {"type": "li", "children": [f"Item {i}"]} for i in range(3)
]}
print(h.render(build(tree)))
```

## Full document

```python
from html_tags import html_doc, head, title, body, h1, p, Datastar, Favicon

doc = html_doc(
    head(
        title("My Page"),
        Favicon("🚀"),
        Datastar(),  # v1.0.0 stable, pass 'latest' for main branch
    ),
    body(
        h1("Hello"),
        p("World."),
    ),
)
print(doc)
```

## Safe HTML opt-out

By default, text children and attribute values are escaped. Wrap pre-sanitized HTML in `Safe` to opt out:

```python
from html_tags import div, Safe, render

render(div("<b>escaped</b>"))        # &lt;b&gt;escaped&lt;/b&gt;
render(div(Safe("<b>trusted</b>")))  # <b>trusted</b>
```

## Parsing HTML into tags

```python
from html_tags import html_to_tag, render

t = html_to_tag('<div class="x"><p>hi</p></div>')
print(render(t))
```

Useful for round-tripping content through the same pipeline as generated HTML.

## Design notes

The entire library is one file, built on three ideas:

1. **A tag is a closure.** `tag(name, children, attrs)` returns a function that, when called, returns another closure with extended children/attrs. No classes, no mutation.
2. **Two attribute channels.** Kwargs are for Python-friendly names; dicts are for everything else. Transformation happens once, at the boundary.
3. **Namespaces switch at specific tags.** `<svg>` switches to SVG rules, `<math>` to MathML, `<foreignObject>` back to HTML. Everything else inherits from its enclosing namespace.

That's the whole model. If you want to read the source, it's a single file under 250 lines.

## License  
MIT
