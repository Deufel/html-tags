import marimo

__generated_with = "0.22.0"
app = marimo.App()

with app.setup:
    # attrs.py

    # Keyword escapes: things Python won't let you type as kwargs
    ALIASES = {
        'cls':       'class',
        'klass':     'class',
        'fr':        'for',
        'htmlfor':   'for',
    }


@app.function
def internal_normalize_key(key: str) -> str:
    """Transform a Python identifier into an HTML attribute name.

    Rules applied in order:
      1. Check alias table (cls -> class, fr -> for, etc.)
      2. Strip a single leading underscore  (_for -> for)
      3. Replace remaining underscores with hyphens (data_foo -> data-foo)
    """
    if key in ALIASES:
        return ALIASES[key]
    if key.startswith('_'):
        key = key[1:]
    return key.replace('_', '-')


@app.function
def normalize_attrs(*dicts: dict, **kwargs) -> dict:
    """Merge dicts (verbatim) and kwargs (normalized) into one attrs dict.

    Dict positional args bypass key transformation entirely — use them for
    attributes with colons, dots, or any character invalid in Python identifiers
    (e.g. data-on:click, xlink:href).

    Values:
      True  -> bare boolean attribute (rendered as just the name)
      False -> attribute omitted
      None  -> attribute omitted
    """
    out = {}

    for d in dicts:
        assert isinstance(d, dict), f"positional args must be dicts, got {type(d).__name__!r}"
        for k, v in d.items():
            if v is False or v is None:
                continue
            out[k] = v

    for k, v in kwargs.items():
        if v is False or v is None:
            continue
        out[internal_normalize_key(k)] = v

    return out


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
