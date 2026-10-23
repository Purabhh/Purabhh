"""Turn text into SVG path data so the SVGs never depend on a loaded font."""
import os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

HERE = os.path.dirname(os.path.abspath(__file__))
_cache = {}


def font(name):
    if name not in _cache:
        _cache[name] = TTFont(os.path.join(HERE, "fonts", name))
    return _cache[name]


def measure(text, size, fname="baloo.ttf", spacing=0):
    f = font(fname)
    cmap, hmtx = f.getBestCmap(), f["hmtx"]
    scale = size / f["head"].unitsPerEm
    return sum(hmtx[cmap[ord(c)]][0] * scale + spacing for c in text) - spacing


def text(t, x, y, size, fname="baloo.ttf", anchor="start", spacing=0):
    """Path data for t with its baseline at y."""
    f = font(fname)
    cmap, gs, hmtx = f.getBestCmap(), f.getGlyphSet(), f["hmtx"]
    scale = size / f["head"].unitsPerEm
    w = measure(t, size, fname, spacing)
    if anchor == "middle":
        x -= w / 2
    elif anchor == "end":
        x -= w
    pen = SVGPathPen(gs)
    for c in t:
        g = cmap[ord(c)]
        gs[g].draw(TransformPen(pen, (scale, 0, 0, -scale, x, y)))
        x += hmtx[g][0] * scale + spacing
    return pen.getCommands()
