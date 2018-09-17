"""
    <title>three.js webgl - buffergeometry - selective - draw</title>
"""    

import math
import random
from datetime import datetime

from THREE import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.pyOpenGL.pyGUI import *
from THREE.pyOpenGL.widgets.Stats import *


vertexshader="""
attribute float visible;
varying float vVisible;
attribute vec3 vertColor;
varying vec3 vColor;

void main() {

    vColor = vertColor;
    vVisible = visible;
    gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );

}
"""

fragmentshader = """
varying float vVisible;
varying vec3 vColor;

void main() {

    if ( vVisible > 0.0 ) {

        gl_FragColor = vec4( vColor, 1.0 );

    } else {

        discard;

    }
    
}
"""


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.geometry = None
        self.mesh =  None
        self.numLat = 100
        self.numLng = 200
        self.numLinesCulled = 0
        self.gui = None
        self.keymap = {
            104: 0,
            115: 0
        }


def init(p: Params):
    p.container = pyOpenGL(p)
    p.container.addEventListener('resize', onWindowResize, False)
    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize(window.innerWidth, window.innerHeight)

    p.scene = THREE.Scene()

    p.camera = THREE.PerspectiveCamera( 45, window.innerWidth / window.innerHeight, 0.01, 10 )
    p.camera.position.z = 3.5

    p.scene.add( THREE.AmbientLight( 0x444444 ) )

    p.geometry = THREE.BufferGeometry()

    linePositions = Float32Array(p.numLat * p.numLng * 3 * 2)
    lineColors = Float32Array(p.numLat * p.numLng * 3 * 2)
    visible = Float32Array(p.numLat * p.numLng * 2)

    def addLines( radius ):
        for i in range(p.numLat):
            for j in range(p.numLng):
                lat = ( random.random() * math.pi ) / 50.0 + i / p.numLat * math.pi
                lng = ( random.random() * math.pi ) / 50.0 + j / p.numLng * 2 * math.pi

                index = i * p.numLng + j

                linePositions[ index * 6 + 0 ] = 0
                linePositions[ index * 6 + 1 ] = 0
                linePositions[ index * 6 + 2 ] = 0
                linePositions[ index * 6 + 3 ] = radius * math.sin( lat ) * math.cos( lng )
                linePositions[ index * 6 + 4 ] = radius * math.cos( lat )
                linePositions[ index * 6 + 5 ] = radius * math.sin( lat ) * math.sin( lng )

                color = THREE.Color( 0xffffff )

                color.setHSL( lat /math.pi, 1.0, 0.2 )
                lineColors[ index * 6 + 0 ] = color.r
                lineColors[ index * 6 + 1 ] = color.g
                lineColors[ index * 6 + 2 ] = color.b

                color.setHSL( lat / math.pi, 1.0, 0.7 )
                lineColors[ index * 6 + 3 ] = color.r
                lineColors[ index * 6 + 4 ] = color.g
                lineColors[ index * 6 + 5 ] = color.b

                # non-0 is visible
                visible[ index * 2 + 0 ] = 1.0
                visible[ index * 2 + 1 ] = 1.0

    addLines( 1.0 )

    p.geometry.addAttribute( 'position', THREE.BufferAttribute( linePositions, 3 ) )
    p.geometry.addAttribute( 'vertColor', THREE.BufferAttribute( lineColors, 3 ) )
    p.geometry.addAttribute( 'visible', THREE.BufferAttribute( visible, 1 ) )

    p.geometry.computeBoundingSphere()

    shaderMaterial = THREE.ShaderMaterial( {
        "vertexShader": vertexshader,
        "fragmentShader": fragmentshader
    } )

    p.mesh = THREE.LineSegments( p.geometry, shaderMaterial )
    p.scene.add( p.mesh )

    updateCount(p)

    p.gui = pyGUI(p.renderer)
    p.gui.add(Stats())


def updateCount(p):
    str = '1 draw call, %f lines, %d culled (<a target="_blank" href="http://callum.com">author</a>)' % (p.numLat * p.numLng, p.numLinesCulled)
    print(str)

    
def hideLines(p):
    for i in range(0, len(p.geometry.attributes.visible.array), 2):
        if random.random() > 0.75:
            if p.geometry.attributes.visible.array[ i + 0 ]:
                p.numLinesCulled += 1

            p.geometry.attributes.visible.array[ i + 0 ] = 0
            p.geometry.attributes.visible.array[ i + 1 ] = 0

    p.geometry.attributes.visible.needsUpdate = True

    updateCount(p)

    
def showAllLines(p):
    p.numLinesCulled = 0

    for i in range(0, len(p.geometry.attributes.visible.array), 2 ):
        p.geometry.attributes.visible.array[ i + 0 ] = 1
        p.geometry.attributes.visible.array[ i + 1 ] = 1

    p.geometry.attributes.visible.needsUpdate = True

    updateCount(p)

    
def onWindowResize(event, params):
    params.camera.aspect = window.innerWidth / window.innerHeight
    params.camera.updateProjectionMatrix()

    params.renderer.setSize( window.innerWidth, window.innerHeight )


def animate(p):
    time = datetime.now().timestamp() * 0.1

    p.mesh.rotation.x = time * 0.25
    p.mesh.rotation.y = time * 0.5

    p.gui.update()

    p.renderer.render( p.scene, p.camera )


def keyboard(event, p):
    """

    :param event:
    :param p:
    :return:
    """
    keyCode = event.keyCode
    down = (event.type == 'keydown') * 1

    if keyCode == 97:  # Q
        p.container.quit()
    if keyCode == 104 and down:  # H
        hideLines(p)
    if keyCode == 115 and down:  # S
        showAllLines(p)
    elif keyCode in p.keymap:
        p.keymap[keyCode] = down

    else:
        print("keyCode:", keyCode)


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener('animationRequest', animate)
    params.container.addEventListener('keydown', keyboard)
    params.container.addEventListener('keyup', keyboard)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
