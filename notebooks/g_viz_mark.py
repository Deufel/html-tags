import marimo

__generated_with = "0.22.0"
app = marimo.App()

with app.setup:
    # mark.py

    from a_node import Node, SVG
    from e_dsl  import TagFactory

    s = TagFactory(SVG)



@app.cell
def _():
    import pytest

    return (pytest,)


@app.function
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


@app.function
def circle(cx: float, cy: float, r: float, cls: str = '', **extra) -> Node:
    """A circle. Used for scatter plots and dot plots.

    cx, cy are the center coordinates in SVG space.
    r is the radius in pixels.
    """
    attrs = {'cx': cx, 'cy': cy, 'r': r}
    if cls: attrs['class'] = cls
    attrs.update(extra)
    return s.circle(**attrs)


@app.function
def line(x1: float, y1: float, x2: float, y2: float, cls: str = '') -> Node:
    """A straight line between two points.

    Used for connectors, reference lines, and axis rules.
    Stroke color and width come from CSS — set --color and stroke-width via cls.
    """
    attrs = {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}
    if cls: attrs['class'] = cls
    return s.line(**attrs)


@app.function
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


@app.function
def path(d: str, cls: str = '') -> Node:
    """A raw SVG path. Used for area charts and complex shapes.

    d -- an SVG path data string. Build it with path_d() below,
         or pass a pre-built string for full control.
    """
    assert d, "path data string must not be empty"
    attrs = {'d': d}
    if cls: attrs['class'] = cls
    return s.path(**attrs)


@app.function
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


@app.function
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


@app.function
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


@app.function
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


@app.cell
def _(pytest):
    class TestMark:

        def test_rect_basic(self):
            node = rect(x=10, y=20, width=80, height=60)
            assert node.tag          == 'rect'
            assert node.ns           == SVG
            assert node.attrs['x']   == 10
            assert node.attrs['y']   == 20

        def test_rect_no_rx_by_default(self):
            node = rect(x=0, y=0, width=10, height=10)
            assert 'rx' not in node.attrs

        def test_rect_rx_present_when_set(self):
            node = rect(x=0, y=0, width=10, height=10, rx=4)
            assert node.attrs['rx'] == 4

        def test_rect_cls(self):
            node = rect(x=0, y=0, width=10, height=10, cls='surface')
            assert node.attrs['class'] == 'surface'

        def test_circle_basic(self):
            node = circle(cx=50, cy=50, r=10)
            assert node.tag           == 'circle'
            assert node.attrs['cx']   == 50
            assert node.attrs['r']    == 10

        def test_line_basic(self):
            node = line(x1=0, y1=0, x2=100, y2=100)
            assert node.tag            == 'line'
            assert node.attrs['x1']    == 0
            assert node.attrs['x2']    == 100

        def test_polyline_basic(self):
            node = polyline([(0, 0), (50, 50), (100, 0)])
            assert node.tag                   == 'polyline'
            assert node.attrs['points']       == '0,0 50,50 100,0'
            assert node.attrs['fill']         == 'none'

        def test_polyline_requires_two_points(self):
            with pytest.raises(AssertionError):
                polyline([(0, 0)])

        def test_path_basic(self):
            node = path('M 0 0 L 100 100')
            assert node.tag        == 'path'
            assert node.attrs['d'] == 'M 0 0 L 100 100'

        def test_path_empty_raises(self):
            with pytest.raises(AssertionError):
                path('')

        def test_path_d_basic(self):
            d = path_d([(0, 0), (50, 50), (100, 0)])
            assert d.startswith('M 0 0')
            assert 'L 50 50' in d
            assert 'L 100 0' in d

        def test_path_d_close(self):
            d = path_d([(0, 0), (100, 0)], close=True)
            assert d.endswith('Z')

        def test_area_d_basic(self):
            d = area_d([(0, 50), (100, 30)], baseline=200)
            assert d.startswith('M 0 50')
            assert 'L 0  200' in d
            assert d.endswith('Z')

        def test_text_basic(self):
            node = text('hello', x=100, y=50)
            assert node.tag                       == 'text'
            assert node.children[0]              == 'hello'
            assert node.attrs['text-anchor']     == 'middle'

        def test_text_anchor_options(self):
            for anchor in ('start', 'middle', 'end'):
                node = text('x', x=0, y=0, anchor=anchor)
                assert node.attrs['text-anchor'] == anchor

        def test_text_bad_anchor_raises(self):
            with pytest.raises(AssertionError):
                text('x', x=0, y=0, anchor='center')

        def test_text_no_font_size_attr(self):
            node = text('x', x=0, y=0)
            assert 'font-size' not in node.attrs

        def test_group_basic(self):
            node = group(circle(cx=0, cy=0, r=5), rect(x=0, y=0, width=10, height=10))
            assert node.tag          == 'g'
            assert len(node.children) == 2

        def test_group_transform(self):
            node = group(cls='surface', transform='translate(40, 20)')
            assert node.attrs['transform'] == 'translate(40, 20)'

        def test_group_no_empty_attrs(self):
            node = group()
            assert 'cls'       not in node.attrs
            assert 'transform' not in node.attrs

    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
