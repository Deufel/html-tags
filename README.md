# html-tags

![PyPI version](https://img.shields.io/pypi/v/html-tags)

> [!WARNING]
> Under active development — Mar 2026

Concise, immutable HTML/SVG generation for Python. Zero dependencies.

```python
from html_tags import setup_tags, setup_svg
setup_tags(); setup_svg()

page = Html(
    Head(Title("hello")),
    Body(
        H1("hello world", cls="title"),
        Svg(Circle(cx="50", cy="50", r="40")),
    )
)
```

Tags are immutable — call to add children or attributes:

```python
Div(cls="card")("content", id="main")
```

SVG elements self-close correctly (`<line />`) and shapes like `Circle` accept children for animations.

Datastar SSE helpers included:

```python
from html_tags import patch_elements, patch_signals, datastar_stream
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