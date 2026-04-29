from .node import Node, SVG
from .dsl import TagFactory

s = TagFactory(SVG)

def rect(x: float, y: float, width: float, height: float,
         cls: str = '', rx: float = 0, **extra) -> Node:
    """A filled rectangle. The workhorse of bar charts.

    x, y are the top-left corner in SVG space.
    For bar charts built with a flipped y scale, y is the top of the bar
    and height is the distance down to the baseline — both come from scale math.

    cls   -- CSS classes for colorNtype styling (e.g. 'surface', '.pri')
    rx    -- corner radius in pixels, 0 = sharp corners
    """
    attrs = {'x': x, 'y': y, 'width': width, 'height': height}
    if rx:    attrs['rx'] = rx
    if cls: attrs['class'] = cls
    attrs.update(extra)
    return s.rect(**attrs)

def circle(cx: float, cy: float, r: float, cls: str = '', **extra) -> Node:
    """A circle. Used for scatter plots and dot plots.

    cx, cy are the center coordinates in SVG space.
    r is the radius in pixels.
    """
    attrs = {'cx': cx, 'cy': cy, 'r': r}
    if cls: attrs['class'] = cls
    attrs.update(extra)
    return s.circle(**attrs)

def line(x1: float, y1: float, x2: float, y2: float, cls: str = '') -> Node:
    """A straight line between two points.

    Used for connectors, reference lines, and axis rules.
    Stroke color and width come from CSS — set --color and stroke-width via cls.
    """
    attrs = {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}
    if cls: attrs['class'] = cls
    return s.line(**attrs)

def polyline(points: list[tuple[float, float]], cls: str = '') -> Node:
    """A connected sequence of line segments. Used for line charts.

    points -- list of (x, y) tuples in SVG space, already scale-mapped.

    Example:
        y = LinearScale(domain=(0, 100), range_=(height, 0))
        x = LinearScale(domain=(0, 10),  range_=(0, width))
        polyline([(x(i), y(v)) for i, v in enumerate(values)])
    """
    assert len(points) >= 2, "polyline requires at least 2 points"
    pts_str = ' '.join(f'{px},{py}' for px, py in points)
    attrs   = {'points': pts_str, 'fill': 'none'}
    if cls: attrs['class'] = cls
    return s.polyline(**attrs)

def path(d: str, cls: str = '') -> Node:
    """A raw SVG path. Used for area charts and complex shapes.

    d -- an SVG path data string. Build it with path_d() below,
         or pass a pre-built string for full control.
    """
    assert d, "path data string must not be empty"
    attrs = {'d': d}
    if cls: attrs['class'] = cls
    return s.path(**attrs)

def path_d(points: list[tuple[float, float]], close: bool = False) -> str:
    """Build an SVG path data string from a list of (x, y) points.

    First point becomes M (moveto), rest become L (lineto).
    close=True appends Z to close the path — use for filled areas.

    Example:
        d = path_d([(0, 100), (50, 60), (100, 80)], close=True)
        path(d, cls='surface')
    """
    assert len(points) >= 1, "path requires at least one point"
    parts = [f'M {points[0][0]} {points[0][1]}']
    parts += [f'L {px} {py}' for px, py in points[1:]]
    if close:
        parts.append('Z')
    return ' '.join(parts)

def area_d(points: list[tuple[float, float]], baseline: float) -> str:
    """Build a closed SVG path for an area chart.

    points   -- (x, y) data points, top edge of the area
    baseline -- y pixel value of the bottom edge (usually chart height or y(0))

    Traces the top edge left to right, then closes along the baseline.
    """
    assert len(points) >= 2, "area requires at least 2 points"
    top    = [f'M {points[0][0]} {points[0][1]}']
    top   += [f'L {px} {py}' for px, py in points[1:]]
    bottom = [f'L {points[-1][0]} {baseline}',
              f'L {points[0][0]}  {baseline}',
              'Z']
    return ' '.join(top + bottom)

def text(content: str, x: float, y: float,
         anchor: str = 'middle', cls: str = '') -> Node:
    """A text label at a given position.

    anchor -- SVG text-anchor: 'start', 'middle', 'end'
    cls    -- colorNtype classes; --type step on the element controls size.

    Font size is never set here. Use --type via cls or inline style.
    """
    assert anchor in ('start', 'middle', 'end'), \
        f"anchor must be 'start', 'middle', or 'end', got {anchor!r}"
    attrs = {
        'x': x, 'y': y,
        'text-anchor': anchor,
    }
    if cls: attrs['class'] = cls
    return s.text(content, **attrs)

def group(*children, cls: str = '', transform: str = '') -> Node:
    """An SVG <g> element for grouping marks.

    The primary tool for applying a shared --color, --hue, or transform
    to a set of marks without touching each one individually.

    Example:
        group(
            rect(...), rect(...), rect(...),
            cls='surface',
            transform='translate(40, 20)',
        )
    """
    attrs = {}
    if cls:       attrs['class']       = cls
    if transform: attrs['transform'] = transform
    return s.g(*children, **attrs)
