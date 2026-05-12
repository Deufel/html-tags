import marimo

__generated_with = "0.22.0"
app = marimo.App()

with app.setup:
    # scale.py
    pass


@app.cell
def _():
    import pytest

    return (pytest,)


@app.class_definition
class Scale:
    """Abstract base. A scale maps domain values to range values.

    Subclasses implement __call__(value) and ticks(count).
    domain and range_ are always 2-tuples.
    """
    __slots__ = ('domain', 'range_')

    def __init__(self, domain: tuple, range_: tuple):
        assert len(domain) == 2, "domain must be (min, max)"
        assert len(range_)  == 2, "range_ must be (min, max)"
        self.domain = domain
        self.range_ = range_

    def __call__(self, value: float) -> float:
        raise NotImplementedError

    def ticks(self, count: int = 5) -> list:
        raise NotImplementedError


@app.class_definition
class LinearScale(Scale):
    """Maps a continuous domain linearly to a continuous range.

    For vertical chart axes pass range_=(height, 0) to flip y so that
    larger data values map to higher positions — math convention, not SVG.

    Example:
        x = LinearScale(domain=(0, 100), range_=(0, 400))
        y = LinearScale(domain=(0, 50),  range_=(300, 0))  # flipped
        x(50)   # -> 200.0
        y(25)   # -> 150.0
    """
    __slots__ = ('domain', 'range_')

    def __call__(self, value: float) -> float:
        d0, d1 = self.domain
        r0, r1 = self.range_
        assert d1 != d0, "domain min and max must differ"
        t = (value - d0) / (d1 - d0)
        return r0 + t * (r1 - r0)

    def ticks(self, count: int = 5) -> list[float]:
        """Return evenly spaced values across the domain."""
        d0, d1  = self.domain
        assert count >= 2, "tick count must be at least 2"
        step    = (d1 - d0) / (count - 1)
        return [d0 + i * step for i in range(count)]


@app.class_definition
class BandScale(Scale):
    """Maps a discrete domain (list of categories) to a continuous range.

    Divides the range into equal bands, one per category.
    padding is a 0.0–1.0 ratio of band width reserved as gap between bands.

    Example:
        x = BandScale(domain=['A', 'B', 'C'], range_=(0, 300), padding=0.2)
        x('A')       # -> left edge of band A in pixels
        x.bandwidth  # -> width of each band
        x.ticks()    # -> ['A', 'B', 'C']
    """
    __slots__ = ('domain', 'range_', 'padding', 'bandwidth', '_step', '_offsets')

    def __init__(self, domain: list, range_: tuple, padding: float = 0.1):
        assert 0.0 <= padding < 1.0, "padding must be in [0.0, 1.0)"
        assert len(domain) > 0,      "domain must have at least one category"
        assert len(range_)  == 2,    "range_ must be (min, max)"

        self.domain  = domain
        self.range_  = range_
        self.padding = padding

        r0, r1       = range_
        total        = abs(r1 - r0)
        n            = len(domain)
        step         = total / (n + padding * (n - 1) / (1 - padding) if padding < 1 else n)
        self._step   = total / n
        self.bandwidth = self._step * (1 - padding)

        self._offsets = {
            cat: r0 + i * self._step + (self._step * padding / 2)
            for i, cat in enumerate(domain)
        }

    def __call__(self, value) -> float:
        assert value in self._offsets, f"{value!r} not in domain"
        return self._offsets[value]

    def ticks(self, count: int = None) -> list:
        """Return all category labels — count is ignored for band scales."""
        return list(self.domain)


@app.class_definition
class HueScale:
    """Maps a continuous domain to a CSS hue range (0–360).

    Used to set --hue on SVG marks for data-driven color encoding.
    Pair with --color: 0.2 (or similar) on the mark element so chroma
    stays in the legible range while hue carries the data signal.

    Example:
        hue = HueScale(domain=(0, 100), range_=(25, 280))
        hue(0)    # -> 25   (set as style="--hue: 25")
        hue(100)  # -> 280
        hue(50)   # -> 152.5
    """
    __slots__ = ('domain', 'range_')

    def __init__(self, domain: tuple, range_: tuple = (25, 280)):
        assert len(domain) == 2, "domain must be (min, max)"
        assert len(range_)  == 2, "range_ must be (min, max)"
        self.domain = domain
        self.range_ = range_

    def __call__(self, value: float) -> float:
        d0, d1 = self.domain
        r0, r1 = self.range_
        assert d1 != d0, "domain min and max must differ"
        t = (value - d0) / (d1 - d0)
        return round(r0 + t * (r1 - r0), 2)


@app.class_definition
class OrdinalHueScale:
    """Maps a discrete domain to evenly spaced hues around the color wheel.

    For categorical data where each category needs a distinct color.
    Pair with --color: 0.3 on marks so chroma is vivid but not harsh.

    Example:
        hue = OrdinalHueScale(['A', 'B', 'C'])
        hue('A')   # -> 0
        hue('B')   # -> 120
        hue('C')   # -> 240
    """
    __slots__ = ('domain', '_hues')

    def __init__(self, domain: list, start: float = 0, spread: float = 360):
        assert len(domain) > 0, "domain must have at least one category"
        n          = len(domain)
        step       = spread / n
        self.domain = domain
        self._hues  = {cat: round(start + i * step, 2) for i, cat in enumerate(domain)}

    def __call__(self, value) -> float:
        assert value in self._hues, f"{value!r} not in domain"
        return self._hues[value]

    def ticks(self) -> list:
        return list(self.domain)


@app.cell
def _(pytest):
    class TestScale:

        def test_linear_basic(self):
            x = LinearScale(domain=(0, 100), range_=(0, 400))
            assert x(0)   == 0.0
            assert x(100) == 400.0
            assert x(50)  == 200.0

        def test_linear_flipped_y(self):
            y = LinearScale(domain=(0, 100), range_=(300, 0))
            assert y(0)   == 300.0
            assert y(100) == 0.0
            assert y(50)  == 150.0

        def test_linear_ticks(self):
            x = LinearScale(domain=(0, 100), range_=(0, 400))
            assert x.ticks(5) == [0, 25, 50, 75, 100]

        def test_band_basic(self):
            x = BandScale(domain=['A', 'B', 'C'], range_=(0, 300), padding=0.0)
            assert x('A') == 0.0
            assert x('B') == pytest.approx(100.0)
            assert x('C') == pytest.approx(200.0)

        def test_band_bandwidth(self):
            x = BandScale(domain=['A', 'B', 'C'], range_=(0, 300), padding=0.0)
            assert x.bandwidth == pytest.approx(100.0)

        def test_band_ticks(self):
            x = BandScale(domain=['A', 'B', 'C'], range_=(0, 300))
            assert x.ticks() == ['A', 'B', 'C']

        def test_band_unknown_raises(self):
            x = BandScale(domain=['A', 'B'], range_=(0, 200))
            with pytest.raises(AssertionError):
                x('Z')

        def test_hue_scale(self):
            h = HueScale(domain=(0, 100), range_=(25, 280))
            assert h(0)   == 25.0
            assert h(100) == 280.0
            assert h(50)  == pytest.approx(152.5)

        def test_ordinal_hue_even_spread(self):
            h = OrdinalHueScale(['A', 'B', 'C'])
            assert h('A') == 0.0
            assert h('B') == pytest.approx(120.0)
            assert h('C') == pytest.approx(240.0)

        def test_ordinal_hue_unknown_raises(self):
            h = OrdinalHueScale(['A', 'B'])
            with pytest.raises(AssertionError):
                h('Z')

    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
