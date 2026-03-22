# html-tags

![PyPI version](https://img.shields.io/pypi/v/html-tags)

> [!WARNING]
> Under active development — Mar 2026

Concise, immutable HTML/SVG generation for Python.

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

## Install

```
pip install html-tags
```

## License

MIT