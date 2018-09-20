"""
<title>three.js webgl - custom attributes [lines]</title>
"""
#TODO the extruded bezel is not working as expected

import math
import random
import math
import random
from datetime import datetime

from THREE import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.pyOpenGL.pyGUI import *
from THREE.pyOpenGL.widgets.Stats import *
from THREE.pyOpenGL.pyCache import *
from THREE.loaders.FontLoader import *
from THREE.geometries.TextGeometry import *


vertexshader = """
    uniform float amplitude;

    attribute vec3 displacement;
    attribute vec3 customColor;

    varying vec3 vColor;

    void main() {

        vec3 newPosition = position + amplitude * displacement;

        vColor = customColor;

        gl_Position = projectionMatrix * modelViewMatrix * vec4( newPosition, 1.0 );

    }
"""

fragmentshader = """
    uniform vec3 color;
    uniform float opacity;

    varying vec3 vColor;

    void main() {

        gl_FragColor = vec4( vColor * color, opacity );

    }
"""


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.geometry = None
        self.mesh = None
        self.object = None
        self.uniforms = None


def init(p):
    p.container = pyOpenGL(p)
    p.container.addEventListener('resize', onWindowResize, False)
    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize(window.innerWidth, window.innerHeight)

    loader = FontLoader()
    font = loader.load( 'fonts/helvetiker_bold.typeface.json')

    p.camera = THREE.PerspectiveCamera( 30, window.innerWidth / window.innerHeight, 1, 10000 )
    p.camera.position.z = 400

    p.scene = THREE.Scene()
    p.scene.background = THREE.Color( 0x050505 )

    uniforms = {
        'amplitude': { 'value': 5.0 },
        'opacity':   { 'value': 0.3 },
        'color':     { 'value': THREE.Color( 0xff0000 ) }
    }

    shaderMaterial = THREE.ShaderMaterial( {
        'uniforms':       uniforms,
        'vertexShader':   vertexshader,
        'fragmentShader': fragmentshader,
        'blending':       THREE.AdditiveBlending,
        'depthTest':      False,
        'transparent':    True
    })
    p.uniforms = shaderMaterial.uniforms

    url = "three.js.geometry"
    cached = pyCache(url)
    geometry = cached.load(True)
    if geometry is None:
        geometry = TextGeometry('three.js', {
            'font': font,

            'size': 50,
            'height': 15,
            'curveSegments': 10,

            'bevelThickness': 5,
            'bevelSize': 1.5,
            'bevelEnabled': True,
            'bevelSegments': 10,
        })

        geometry.center()
        cached.save(geometry)
    else:
        geometry.rebuild_id()

    vertices = geometry.vertices

    buffergeometry = THREE.BufferGeometry()

    position = THREE.Float32BufferAttribute( len(vertices) * 3, 3 ).copyVector3sArray( vertices )
    buffergeometry.addAttribute( 'position', position )

    displacement = THREE.Float32BufferAttribute( len(vertices) * 3, 3 )
    buffergeometry.addAttribute( 'displacement', displacement )
    array = buffergeometry.attributes.displacement.array
    for i in range(0, len(array), 3):
        array[ i     ] = 3 * ( 0.5 - random.random() )
        array[ i + 1 ] = 3 * ( 0.5 - random.random() )
        array[ i + 2 ] = 3 * ( 0.5 - random.random() )

    customColor = THREE.Float32BufferAttribute( len(vertices) * 3, 3 )
    buffergeometry.addAttribute( 'customColor', customColor )

    color = THREE.Color( 0xffffff )

    l = customColor.count
    for i in range(l):
        color.setHSL( i / l, 0.5, 0.5 )
        color.toArray( customColor.array, i * customColor.itemSize )

    p.object = THREE.Line( buffergeometry, shaderMaterial )
    p.object.rotation.x = 0.2
    p.scene.add( p.object )

    p.gui = pyGUI(p.renderer)
    p.gui.add(Stats())


def onWindowResize(event, params):
    params.camera.aspect = window.innerWidth / window.innerHeight
    params.camera.updateProjectionMatrix()

    params.renderer.setSize( window.innerWidth, window.innerHeight )


def animate(p):
    render(p)
    p.gui.update()


def render(p):
    time = datetime.now().timestamp() * 1

    p.object.rotation.y = 0.25 * time

    p.uniforms.amplitude.value = math.sin( 0.5 * time )
    p.uniforms.color.value.offsetHSL( 0.0005, 0, 0 )

    attributes = p.object.geometry.attributes
    array = attributes.displacement.array

    #for i in range(0, len(array), 3):
    #    array[ i     ] += 0.3 * ( 0.5 - random.random() )
    #    array[ i + 1 ] += 0.3 * ( 0.5 - random.random() )
    #    array[ i + 2 ] += 0.3 * ( 0.5 - random.random() )

    #attributes.displacement.needsUpdate = True

    p.renderer.render( p.scene, p.camera )


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener('animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
