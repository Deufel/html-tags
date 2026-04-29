from .node import SVG, Safe
from .dsl import TagFactory
from .viz_mark import group

s = TagFactory(SVG)
CHART_STYLES = Safe('\n      .mark          { fill: var(--bg); }\n      .mark-stroke   { fill: none; stroke: var(--bg); }\n      .axis-rule     { stroke: var(--bg); fill: none; opacity: 0.3; }\n      .tick-line     { stroke: var(--bg); fill: none; opacity: 0.3; }\n      .tick-label    { fill: var(--bg); font-family: inherit; }\n    ')

class Margin:
    """Space reserved around the plot area for axes and labels.

    inner_width  = width  - left - right
    inner_height = height - top  - bottom
    """
    __slots__ = ('top', 'right', 'bottom', 'left')

    def __init__(self, top=40, right=20, bottom=40, left=50):
        self.top    = top
        self.right  = right
        self.bottom = bottom
        self.left   = left

    @property
    def inner_width(self):  return self._w - self.left - self.right
    @property
    def inner_height(self): return self._h - self.top  - self.bottom

    def bind(self, width: float, height: float):
        """Return a BoundMargin with inner dimensions resolved."""
        return BoundMargin(self.top, self.right, self.bottom, self.left,
                            width, height)

class BoundMargin:
    """Margin with outer dimensions known. Returned by Margin.bind().

    inner_width  = width  - left - right
    inner_height = height - top  - bottom
    """
    __slots__ = ('top', 'right', 'bottom', 'left', 'width', 'height',
                 'inner_width', 'inner_height')

    def __init__(self, top, right, bottom, left, width, height):
        self.top          = top
        self.right        = right
        self.bottom       = bottom
        self.left         = left
        self.width        = width
        self.height       = height
        self.inner_width  = width  - left - right
        self.inner_height = height - top  - bottom

def chart(width: float, height: float, *layers,
          margin: Margin = None, cls: str = '') -> object:
    """A complete SVG chart scaffold with margin convention.

    width, height  -- outer SVG dimensions in pixels
    layers         -- marks, axes, or any __node__() object
                      drawn inside the plot area (already translated)
    margin         -- Margin instance, defaults to Margin()
    cls            -- colorNtype classes on the outer <svg>

    The returned object implements __node__() and can be dropped
    anywhere in an HTML tree.

    Example:
        x  = LinearScale(domain=(0,100), range_=(0, inner_w))
        y  = LinearScale(domain=(0, 50), range_=(inner_h, 0))
        chart(
            500, 300,
            axis(x, 'bottom'),
            axis(y, 'left'),
            rect(...), rect(...),
            margin=Margin(top=20, right=20, bottom=40, left=50),
        )
    """
    m = margin.bind(width, height) if margin else Margin().bind(width, height)
    return _Chart(width, height, layers, m, cls)

class _Chart:
    """Internal. Holds chart state and implements __node__()."""
    __slots__ = ('width', 'height', 'layers', 'margin', 'cls')

    def __init__(self, width, height, layers, margin, cls):
        self.width  = width
        self.height = height
        self.layers = layers
        self.margin = margin
        self.cls    = cls

    def __node__(self):
        return _build_chart(
            self.width, self.height,
            self.layers, self.margin, self.cls,
        )

def _build_chart(width, height, layers, margin, cls):
    """Build the chart Node tree.

    Outer SVG holds the full viewport.
    Inner <g> is translated to margin.left, margin.top — all layers
    draw relative to this origin, which is the bottom-left of the plot area
    in data space (because y scales are flipped).
    """
    # resolve any __node__() objects in layers
    children = []
    for layer in layers:
        if hasattr(layer, '__node__'):
            children.append(layer.__node__())
        else:
            children.append(layer)

    inner = s.g(
        *children,
        transform=f'translate({margin.left},{margin.top})',
    )

    style_block = s.style(CHART_STYLES)   # <-- injected once

    attrs = {
        'width':   width,
        'height':  height,
        'viewBox': f'0 0 {width} {height}',
    }
    if cls: attrs['class'] = cls

    return s.svg(style_block, inner, **attrs)
