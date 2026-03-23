# html-tags

![PyPI version](https://img.shields.io/pypi/v/html-tags)

> [!WARNING]
> Under active development — Mar 2026

Concise, immutable HTML/SVG generation for Python. Zero dependencies. Purely functional — data and rendering are fully separated.

```python
from html_tags import setup_tags, setup_svg, to_html

setup_tags(); setup_svg()

page = Html(
    Head(Title("hello")),
    Body(
        H1("hello world", cls="title"),
        Svg(Circle(cx="50", cy="50", r="40")),
    )
)

print(to_html(page))
```

## Core design

Tags are **inert data** — `Tag` is a namedtuple describing structure. Rendering is a function that operates on it:

- `to_html(tag)` — render to HTML string
- `pretty(tag)` — indented HTML for debugging
- `validate(tag)` — check structural rules
- `HTML(tag)` — thin wrapper for notebook display

```python
>>> Div(P("hello"), cls="main")
Div(cls='main')(P('hello'))

>>> to_html(Div(P("hello"), cls="main"))
'<div class="main"><p>hello</p></div>'
```

## Immutable construction

Tags are immutable — call to append children or merge attributes:

```python
Div(cls="card")("content", id="main")
```

SVG elements self-close correctly (`<line />`) and shapes like `Circle` accept children for animations:

```python
Circle(cx=50, cy=50, r=20, fill='blue')(
    AnimateTransform(attributeName='transform', type='rotate',
        values='0 50 50;360 50 50', dur='1s', repeatCount='indefinite'))
```

## Parsing HTML

Convert HTML strings back into Tag trees:

```python
>>> html_to_tag('<div id="main"><p class="greeting">hello</p></div>')
Div(id='main')(P(cls='greeting')('hello'))
```

## Raw HTML

Use `Safe` to pass pre-escaped HTML strings through without escaping:

```python
Safe('<b>already escaped</b>')
```

`Script` and `Style` tags handle raw content natively — no wrapping needed.

## Fragments

Group children without a wrapping element:

```python
Fragment(P("one"), P("two"), P("three"))
```

## Gotchas

Keyword attribute names convert `_` to `-`:

```python
Circle(stroke_width="2")  # → stroke-width="2"
```

Dict keys pass through verbatim — use for special syntax or reserved names:

```python
Div({"data-on:click__once": "@post('/api')"})
FeBlend({"mode": "multiply"})
```

HTML void elements render without slash (`<br>`), SVG elements self-close (`<line />`).

Positional args must come before keyword args (Python rule) — use `__call__` chaining to add children after attrs:

```python
Circle(cx=50, cy=50, r=20)(Animate(attributeName='r', values='18;22;18', dur='2s'))
```

## Security

Validates against injection, not HTML structure:

- `<script>`/`<style>` content checked for closing tag injection
- URL attributes reject `javascript:` and `vbscript:` schemes
- Attribute names validated against injection patterns
- Void elements reject children, `<html>` rejects nesting

Structural correctness (e.g. `<li>` inside `<ul>`) is left to the browser.

## Install

```
pip install html-tags
```

## License

MIT