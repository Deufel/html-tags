import marimo

__generated_with = "0.21.1"
app = marimo.App()

with app.setup:
    from a_core import mktag

    SVG_NAMES = {
        # Structure
        'ClipPath': 'clipPath',
        'ForeignObject': 'foreignObject',
        # Gradients
        'LinearGradient': 'linearGradient',
        'RadialGradient': 'radialGradient',
        # Text
        'TextPath': 'textPath',
        # Animation
        'AnimateMotion': 'animateMotion',
        'AnimateTransform': 'animateTransform',
        # Filters
        'FeBlend': 'feBlend',
        'FeColorMatrix': 'feColorMatrix',
        'FeComponentTransfer': 'feComponentTransfer',
        'FeComposite': 'feComposite',
        'FeConvolveMatrix': 'feConvolveMatrix',
        'FeDiffuseLighting': 'feDiffuseLighting',
        'FeDisplacementMap': 'feDisplacementMap',
        'FeDistantLight': 'feDistantLight',
        'FeDropShadow': 'feDropShadow',
        'FeFlood': 'feFlood',
        'FeFuncA': 'feFuncA',
        'FeFuncB': 'feFuncB',
        'FeFuncG': 'feFuncG',
        'FeFuncR': 'feFuncR',
        'FeGaussianBlur': 'feGaussianBlur',
        'FeImage': 'feImage',
        'FeMerge': 'feMerge',
        'FeMergeNode': 'feMergeNode',
        'FeMorphology': 'feMorphology',
        'FeOffset': 'feOffset',
        'FePointLight': 'fePointLight',
        'FeSpecularLighting': 'feSpecularLighting',
        'FeSpotLight': 'feSpotLight',
        'FeTile': 'feTile',
        'FeTurbulence': 'feTurbulence',
    }

    SVG_VOID = frozenset({
        'circle', 'ellipse', 'line', 'path', 'polygon', 'polyline', 'rect',
        'stop', 'use', 'image',
        'set', 'animate', 'animateMotion', 'animateTransform',
        'feBlend', 'feColorMatrix', 'feComposite', 'feConvolveMatrix',
        'feDisplacementMap', 'feDistantLight', 'feDropShadow', 'feFlood',
        'feFuncA', 'feFuncB', 'feFuncG', 'feFuncR', 'feGaussianBlur',
        'feImage', 'feMergeNode', 'feMorphology', 'feOffset',
        'fePointLight', 'feSpotLight', 'feTile', 'feTurbulence',
    })

    ALL_SVG = [
        'Svg', 'G', 'Defs', 'Symbol', 'Use', 'Image',
        'Circle', 'Ellipse', 'Line', 'Path', 'Polygon', 'Polyline', 'Rect',
        'Text', 'Tspan', 'TextPath',
        'ClipPath', 'Mask', 'Marker', 'Pattern', 'Filter',
        'LinearGradient', 'RadialGradient', 'Stop',
        'ForeignObject',
        'Set', 'Animate', 'AnimateMotion', 'AnimateTransform',
        'FeBlend', 'FeColorMatrix', 'FeComponentTransfer', 'FeComposite',
        'FeConvolveMatrix', 'FeDiffuseLighting', 'FeDisplacementMap',
        'FeDistantLight', 'FeDropShadow', 'FeFlood',
        'FeFuncA', 'FeFuncB', 'FeFuncG', 'FeFuncR',
        'FeGaussianBlur', 'FeImage', 'FeMerge', 'FeMergeNode',
        'FeMorphology', 'FeOffset', 'FePointLight',
        'FeSpecularLighting', 'FeSpotLight', 'FeTile', 'FeTurbulence',
    ]




@app.function
def setup_svg(ns=None):
    "Create SVG tag constructors in the given namespace (or caller's globals)"
    import inspect
    if ns is None: ns = inspect.currentframe().f_back.f_globals
    for name in ALL_SVG:
        tag_name = SVG_NAMES.get(name, name.lower())
        mode = 'void' if tag_name in SVG_VOID else 'normal'
        ns[name] = mktag(tag_name, mode)


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
