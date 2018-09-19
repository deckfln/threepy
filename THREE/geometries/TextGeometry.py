"""
 * @author zz85 / http://www.lab4games.net/zz85/blog
 * @author alteredq / http://alteredqualia.com/
 *
 * Text = 3D Text
 *
 * parameters = {
 *  font: <THREE.Font>, // font
 *
 *  size: <float>, // size of the text
 *  height: <float>, // thickness to extrude text
 *  curveSegments: <int>, // number of points on the curves
 *
 *  bevelEnabled: <bool>, // turn on bevel
 *  bevelThickness: <float>, // how deep into text bevel goes
 *  bevelSize: <float> // how far from text outline is bevel
 * }
"""

from THREE.core.Geometry import *
from THREE.geometries.ExtrudeGeometry import *

# TextGeometry


class TextGeometry(Geometry):
    def __init__(self, text, parameters ):
        super().__init__()

        self.type = 'TextGeometry'

        self.parameters = {
            'text': text,
            'parameters': parameters
        }

        self.fromBufferGeometry( TextBufferGeometry( text, parameters ) )
        self.mergeVertices()

# TextBufferGeometry


class TextBufferGeometry(ExtrudeBufferGeometry):
    def __init__(self, text, parameters=None ):
        parameters = parameters or {}

        font = parameters['font']

        if not ( font and font.my_class(isFont) ):
            raise RuntimeError( 'THREE.TextGeometry: font parameter is not an instance of THREE.Font.' )

        shapes = font.generateShapes( text, parameters['size'] )

        # translate parameters to ExtrudeGeometry API

        parameters['depth'] = parameters['height'] if 'height' in parameters else 50

        # defaults

        if 'bevelThickness' not in parameters:
            parameters['bevelThickness'] = 10
        if 'bevelSize' not in parameters:
            parameters['bevelSize'] = 8
        if 'bevelEnabled' not in parameters:
            parameters['bevelEnabled'] = False

        super().__init__(shapes, parameters )

        self.type = 'TextBufferGeometry'
