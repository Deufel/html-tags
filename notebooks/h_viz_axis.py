import marimo

__generated_with = "0.22.0"
app = marimo.App()

with app.setup:
    # axis.py

    from a_node  import SVG
    from e_dsl   import TagFactory
    from f_viz_scale import LinearScale, BandScale
    from g_viz_mark  import line, text, group

    s = TagFactory(SVG)

    ORIENTATIONS = ('bottom', 'top', 'left', 'right')

    # Tick line length in pixels — enough to read, not enough to dominate
    TICK_SIZE = 6


@app.cell
def _():
    import pytest

    return


@app.function
def axis(scale, orientation: str, tick_count: int = 5,
         tick_format=None, cls: str = '') -> object:
    """Return a renderable axis for the given scale and orientation.

    scale        -- a LinearScale or BandScale
    orientation  -- 'bottom' | 'top' | 'left' | 'right'
    tick_count   -- approximate number of ticks (ignored for BandScale)
    tick_format  -- callable(value) -> str, defaults to str()
    cls          -- colorNtype classes applied to the whole axis group

    Returns an object implementing __node__() — drop it anywhere in the tree.

    Example:
        x = LinearScale(domain=(0, 100), range_=(0, 400))
        h.div(axis(x, 'bottom', tick_count=5))
    """
    assert orientation in ORIENTATIONS, \
        f"orientation must be one of {ORIENTATIONS}, got {orientation!r}"

    fmt = tick_format if tick_format is not None else _default_format

    if isinstance(scale, BandScale):
        ticks = scale.ticks()
    else:
        ticks = scale.ticks(tick_count)

    return internal_Axis(scale, orientation, ticks, fmt, cls)


@app.function
def internal_default_format(value) -> str:
    """Format a tick value as a string.
    Integers render without decimal point. Floats render with up to 4 places,
    trailing zeros stripped.
    """
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if isinstance(value, float):
        return f'{value:.4f}'.rstrip('0').rstrip('.')
    return str(value)


@app.class_definition
class internal_Axis:
    """Internal. Holds axis state and implements __node__().

    Not instantiated directly — use axis() instead.
    """
    __slots__ = ('scale', 'orientation', 'ticks', 'fmt', 'cls')

    def __init__(self, scale, orientation, ticks, fmt, cls):
        self.scale       = scale
        self.orientation = orientation
        self.ticks       = ticks
        self.fmt         = fmt
        self.cls         = cls

    def __node__(self):
        return internal_build_axis(
            self.scale, self.orientation,
            self.ticks, self.fmt, self.cls,
        )


@app.function
def internal_build_axis(scale, orientation: str, ticks: list,
                fmt, cls: str):
    """Build the axis Node tree from its parts.

    Separated from _Axis so the construction logic is testable
    and readable without class machinery around it.
    """
    is_horizontal = orientation in ('bottom', 'top')
    children      = []

    # --- baseline rule ---
    if is_horizontal:
        r0, r1  = scale.range_
        baseline = line(x1=r0, y1=0, x2=r1, y2=0, cls='axis-rule')
    else:
        r0, r1  = scale.range_
        baseline = line(x1=0, y1=r0, x2=0, y2=r1, cls='axis-rule')

    children.append(baseline)

    # --- ticks and labels ---
    for tick in ticks:
        pos   = scale(tick)
        label = fmt(tick)
        children.append(internal_tick_group(pos, label, orientation))

    attrs = {}
    if cls: attrs['class'] = cls

    return s.g(*children, **attrs)


@app.function
def internal_tick_group(pos: float, label: str, orientation: str):
    """Build a single tick mark + label group at the given position."""

    if orientation == 'bottom':
        tick_line  = line(x1=pos, y1=0,         x2=pos, y2=TICK_SIZE)
        tick_label = text(label, x=pos, y=TICK_SIZE + 4, anchor='middle')

    elif orientation == 'top':
        tick_line  = line(x1=pos, y1=0,          x2=pos, y2=-TICK_SIZE)
        tick_label = text(label, x=pos, y=-(TICK_SIZE + 4), anchor='middle')

    elif orientation == 'left':
        tick_line  = line(x1=0,         y1=pos, x2=-TICK_SIZE, y2=pos)
        tick_label = text(label, x=-(TICK_SIZE + 4), y=pos, anchor='end')

    elif orientation == 'right':
        tick_line  = line(x1=0,        y1=pos, x2=TICK_SIZE, y2=pos)
        tick_label = text(label, x=TICK_SIZE + 4,  y=pos, anchor='start')

    return s.g(tick_line, tick_label)


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
