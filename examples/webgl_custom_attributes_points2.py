"""
<title>three.js webgl - custom attributes [particles][billboards]</title>
"""
import math
import random
import math
import random
from datetime import datetime

from THREE import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.pyOpenGL.pyGUI import *
from THREE.pyOpenGL.widgets.Stats import *


vertexshader = """
    attribute float size;
    attribute vec3 ca;

    varying vec3 vColor;

    void main() {

        vColor = ca;

        vec4 mvPosition = modelViewMatrix * vec4( position, 1.0 );

        gl_PointSize = size * ( 300.0 / -mvPosition.z );

        gl_Position = projectionMatrix * mvPosition;

    }
"""


fragmentshader = """
    uniform vec3 color;
    uniform sampler2D texture;

    varying vec3 vColor;

    void main() {

        vec4 color = vec4( color * vColor, 1.0 ) * texture2D( texture, gl_PointCoord );

        gl_FragColor = color;

    }
"""


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.geometry = None
        self.mesh = None
        self.sphere = None
        self.length1 = None


def init(p):
    p.container = pyOpenGL(p)
    p.container.addEventListener('resize', onWindowResize, False)
    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize(window.innerWidth, window.innerHeight)
    
    p.camera = THREE.PerspectiveCamera( 45, window.innerWidth / window.innerHeight, 1, 10000 )
    p.camera.position.z = 300

    p.scene = THREE.Scene()

    radius = 100
    segments = 68
    rings = 38

    vertices1 = THREE.SphereGeometry( radius, segments, rings ).vertices
    vertices2 = THREE.BoxGeometry( 0.8 * radius, 0.8 * radius, 0.8 * radius, 10, 10, 10 ).vertices

    p.length1 = len(vertices1)

    vertices = np.concatenate((vertices1, vertices2))

    vl = len(vertices)
    positions = Float32Array( vl * 3 )
    colors = Float32Array( vl * 3 )
    sizes = Float32Array( vl )

    color = THREE.Color()

    for i in range(len(vertices)):
        vertex = vertices[ i ]
        vertex.toArray( positions, i * 3 )

        if i < p.length1:
            color.setHSL( 0.01 + 0.1 * ( i / p.length1 ), 0.99, ( vertex.y + radius ) / ( 4 * radius ) )

        else:
            color.setHSL( 0.6, 0.75, 0.25 + vertex.y / ( 2 * radius ) )

        color.toArray( colors, i * 3 )

        sizes[ i ] = 10 if i < p.length1 else 40

    geometry = THREE.BufferGeometry()
    geometry.addAttribute( 'position', THREE.BufferAttribute( positions, 3 ) )
    geometry.addAttribute( 'size', THREE.BufferAttribute( sizes, 1 ) )
    geometry.addAttribute( 'ca', THREE.BufferAttribute( colors, 3 ) )

    #

    texture = THREE.TextureLoader().load( "textures/sprites/disc.png" )
    texture.wrapS = THREE.RepeatWrapping
    texture.wrapT = THREE.RepeatWrapping

    material = THREE.ShaderMaterial( {
        'uniforms': {
            'amplitude': { 'value': 1.0 },
            'color':     { 'value': THREE.Color( 0xffffff ) },
            'texture':   { 'value': texture }
        },
        'vertexShader':   vertexshader,
        'fragmentShader': fragmentshader,
        'transparent':    True
    })

    #

    p.sphere = THREE.Points( geometry, material )
    p.scene.add( p.sphere )

    #

    p.gui = pyGUI(p.renderer)
    p.gui.add(Stats())


def onWindowResize(event, params):
    params.camera.aspect = window.innerWidth / window.innerHeight
    params.camera.updateProjectionMatrix()

    params.renderer.setSize( window.innerWidth, window.innerHeight )


_vector = THREE.Vector3()


def sortPoints(p):
    vector = _vector

    # Model View Projection matrix

    matrix = THREE.Matrix4()
    matrix.multiplyMatrices( p.camera.projectionMatrix, p.camera.matrixWorldInverse )
    matrix.multiply( p.sphere.matrixWorld )

    #

    geometry = p.sphere.geometry

    index = geometry.getIndex()
    positions = geometry.getAttribute( 'position' ).array
    length = int(len(positions) / 3)

    if index is None:
        array = Uint16Array( length )

        for i in range(length):
            array[ i ] = i

        index = THREE.BufferAttribute( array, 1 )

        geometry.setIndex( index )

    sortArray = []

    for i in range(length):
        vector.fromArray( positions, i * 3 )
        vector.applyMatrix4( matrix )

        sortArray.append( [ vector.z, i ] )


    def numericalSort( a):
        return -a[ 0 ]

    sortArray.sort( key = numericalSort )

    indices = index.array

    for i in range(length):
        indices[ i ] = sortArray[ i ][ 1 ]

    geometry.index.needsUpdate = True


def animate(p):
    render(p)
    p.gui.update()


def render(p):
    time = datetime.now().timestamp() * 2

    p.sphere.rotation.y = 0.02 * time
    p.sphere.rotation.z = 0.02 * time

    geometry = p.sphere.geometry
    attributes = geometry.attributes

    for i in range(len(attributes.size.array)):
        if i < p.length1:
            attributes.size.array[ i ] = 16 + 12 * math.sin( 0.1 * i + time )

    attributes.size.needsUpdate = True

    sortPoints(p)

    p.renderer.render( p.scene, p.camera )


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener('animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
