"""
 * @author zz85 / http://www.lab4games.net/zz85/blog
 * @author mrdoob / http://mrdoob.com/
"""

from THREE.pyOpenGLObject import *
from THREE.extras.core.ShapePath import *


def _createPath( char, scale, offsetX, offsetY, data ):
    glyph = data['glyphs'][ char ] or data['glyphs'][ '?' ]

    if not glyph:
        return

    path = ShapePath()

    if glyph['o']:
        outline = glyph['o'].split(' ')

        i = 0
        while i < len(outline):
            action = outline[i]

            if action == 'm':    # moveTo
                x = float(outline[ i + 1]) * scale + offsetX
                y = float(outline[ i + 2]) * scale + offsetY
                i += 2
                path.moveTo( x, y )

            elif action == 'l':     # lineTo
                x = float(outline[ i + 1]) * scale + offsetX
                y = float(outline[ i + 2 ]) * scale + offsetY
                i += 2

                path.lineTo( x, y )

            elif action == 'q':     # quadraticCurveTo
                cpx = float(outline[ i + 1]) * scale + offsetX
                cpy = float(outline[ i + 2 ]) * scale + offsetY
                cpx1 = float(outline[ i + 3 ]) * scale + offsetX
                cpy1 = float(outline[ i + 4 ]) * scale + offsetY
                i += 4

                path.quadraticCurveTo( cpx1, cpy1, cpx, cpy )

            elif action == 'b':     # bezierCurveTo
                cpx = float(outline[ i + 1]) * scale + offsetX
                cpy = float(outline[ i + 2 ]) * scale + offsetY
                cpx1 = float(outline[ i + 3 ]) * scale + offsetX
                cpy1 = float(outline[ i + 4 ]) * scale + offsetY
                cpx2 = float(outline[ i + 5 ]) * scale + offsetX
                cpy2 = float(outline[ i + 6 ]) * scale + offsetY
                i += 6

                path.bezierCurveTo( cpx1, cpy1, cpx2, cpy2, cpx, cpy )

            i += 1

    return { 'offsetX': glyph['ha'] * scale, 'path': path }


def _createPaths( text, size, data ):
    chars = text
    scale = size / data['resolution']
    line_height = ( data['boundingBox']['yMax'] - data['boundingBox']['yMin'] + data['underlineThickness'] ) * scale

    paths = []

    offsetX = 0
    offsetY = 0

    for char in text:
        if char == '\n':
            offsetX = 0
            offsetY -= line_height
        else:
            ret = _createPath( char, scale, offsetX, offsetY, data )
            offsetX += ret['offsetX']
            paths.append( ret['path'] )

    return paths


class Font(pyOpenGLObject):
    isFont = True
    
    def __init__(self, data ):
        super().__init__()
        self.type = 'Font'
        self.data = data
        self.set_class(isFont)

    def generateShapes(self, text, size=100 ):
        shapes = []
        paths = _createPaths( text, size, self.data )

        for path in paths:
            xshapes = path.toShapes()
            for shape in xshapes:
                shapes.append(shape)

        return shapes
