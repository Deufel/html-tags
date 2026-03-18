# html-tags

> [!WARNING]
> This project is under active development - Mar 2026


Concise HTML generation for Python.

```python
from html_tags import setup_tags
setup_tags()

page = Html(
    Head(Title("hello")),
    Body(
        H1("hello world", cls="title"),
        Button({"data-on:click": "@delete('/1')"})("delete"),
    )
)
```

Tags are immutable and composable — call a tag to add children or attributes:

```python
Div(cls="card")("some content", id="main")
```

Datastar SSE helpers included:

```python
from html_tags import patch_elements, patch_signals, datastar_stream
```

## Install

```
pip install html-tags
uv add html-tags
```

## License

MIT