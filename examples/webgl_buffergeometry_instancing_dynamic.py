"""
    <title>three.js webgl - indexed instancing (single box), dynamic updates</title>
"""

import random

from datetime import datetime

from THREE import *
import THREE._Math as _Math
from THREE.pyOpenGL.pyOpenGL import *


vertexShader = """
        precision highp float;

        uniform mat4 modelViewMatrix;
        uniform mat4 projectionMatrix;

        attribute vec3 position;
        attribute vec3 offset;
        attribute vec2 uv;
        attribute vec4 orientation;

        varying vec2 vUv;

        void main() {

            vec3 vPosition = position;
            vec3 vcV = cross(orientation.xyz, vPosition);
            vPosition = vcV * (2.0 * orientation.w) + (cross(orientation.xyz, vcV) * 2.0 + vPosition);

            vUv = uv;

            gl_Position = projectionMatrix * modelViewMatrix * vec4( offset + vPosition, 1.0 );

        }
"""

fragmentShader = """
        precision highp float;

        uniform sampler2D map;

        varying vec2 vUv;

        void main() {

            gl_FragColor = texture2D(map, vUv);

        }
"""


class Params:
    def __init__(self):
        self.container = None
        self.camera = None
        self.scene = None
        self.renderer = None
        self.orientations = None
        self.lastTime = 0
        self.moveQ = ( THREE.Quaternion( .5, .5, .5, 0.0 ) ).normalize()
        self.tmpQ = THREE.Quaternion()
        self.currentQ = THREE.Quaternion()


def init(p):
    p.container = pyOpenGL(p)
    p.container.addEventListener('resize', onWindowResize, False)
    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize(window.innerWidth, window.innerHeight)

    p.camera = THREE.PerspectiveCamera( 50, window.innerWidth / window.innerHeight, 1, 1000 )
    #camera.position.z = 20;

    p.scene = THREE.Scene()
    p.scene.background = THREE.Color( 0x101010 )

    # geometry

    instances = 5000

    geometry = THREE.InstancedBufferGeometry()

    # per mesh data
    vertices = THREE.BufferAttribute( Float32Array( [
        # Front
        -1, 1, 1,
        1, 1, 1,
        -1, -1, 1,
        1, -1, 1,
        # Back
        1, 1, -1,
        -1, 1, -1,
        1, -1, -1,
        -1, -1, -1,
        # Left
        -1, 1, -1,
        -1, 1, 1,
        -1, -1, -1,
        -1, -1, 1,
        # Right
        1, 1, 1,
        1, 1, -1,
        1, -1, 1,
        1, -1, -1,
        # Top
        -1, 1, 1,
        1, 1, 1,
        -1, 1, -1,
        1, 1, -1,
        # Bottom
        1, -1, 1,
        -1, -1, 1,
        1, -1, -1,
        -1, -1, -1
    ] ), 3 )

    geometry.addAttribute( 'position', vertices )

    uvs = THREE.BufferAttribute( Float32Array( [
                #x    y    z
                # Front
                0, 0,
                1, 0,
                0, 1,
                1, 1,
                # Back
                1, 0,
                0, 0,
                1, 1,
                0, 1,
                # Left
                1, 1,
                1, 0,
                0, 1,
                0, 0,
                # Right
                1, 0,
                1, 1,
                0, 0,
                0, 1,
                # Top
                0, 0,
                1, 0,
                0, 1,
                1, 1,
                # Bottom
                1, 0,
                0, 0,
                1, 1,
                0, 1
    ] ), 2 )

    geometry.addAttribute( 'uv', uvs )

    indices = Uint16Array( [
        0, 1, 2,
        2, 1, 3,
        4, 5, 6,
        6, 5, 7,
        8, 9, 10,
        10, 9, 11,
        12, 13, 14,
        14, 13, 15,
        16, 17, 18,
        18, 17, 19,
        20, 21, 22,
        22, 21, 23
    ] )

    geometry.setIndex( THREE.BufferAttribute( indices, 1 ) )

    # per instance data
    offsets = THREE.InstancedBufferAttribute( Float32Array( instances * 3 ), 3, 1 )

    vector = THREE.Vector4()
    for i in range(offsets.count):
        x = random.random() * 100 - 50
        y = random.random() * 100 - 50
        z = random.random() * 100 - 50
        vector.set( x, y, z, 0 ).normalize()
        # move out at least 5 units from center in current direction
        offsets.setXYZ( i, x + vector.x * 5, y + vector.y * 5, z + vector.z * 5 )

    geometry.addAttribute( 'offset', offsets ) # per mesh translation

    p.orientations = THREE.InstancedBufferAttribute( Float32Array( instances * 4 ), 4, 1 ).setDynamic( True )

    for i in range(p.orientations.count):
        vector.set( random.random() * 2 - 1, random.random() * 2 - 1, random.random() * 2 - 1, random.random() * 2 - 1 )
        vector.normalize()

        p.orientations.setXYZW( i, vector.x, vector.y, vector.z, vector.w )

    geometry.addAttribute( 'orientation', p.orientations )     # per mesh orientation

    # material
    texture = THREE.TextureLoader().load( 'textures/crate.gif' )
    texture.anisotropy = p.renderer.capabilities.getMaxAnisotropy()

    material = THREE.RawShaderMaterial( {
        'uniforms': {
            'map': UniformValue(texture)
        },
        'vertexShader': vertexShader,
        'fragmentShader': fragmentShader,
        'side': THREE.DoubleSide,
        'transparent': False
    } )

    mesh = THREE.Mesh( geometry, material )
    p.scene.add( mesh )


def animate(p):
    render(p)

    
def render(p):
    time = datetime.now().timestamp()

    object = p.scene.children[0]

    object.rotation.y = time * 0.05

    p.renderer.render( p.scene, p.camera )

    delta = ( time - p.lastTime ) / 5000
    p.tmpQ.set( p.moveQ.x * delta, p.moveQ.y * delta, p.moveQ.z * delta, 1 ).normalize()

    for i in range(p.orientations.count):
        index = i * 4
        p.currentQ.set( p.orientations.array[index], p.orientations.array[index + 1], p.orientations.array[index + 2], p.orientations.array[index + 3] )
        p.currentQ.multiply( p.tmpQ )

        p.orientations.setXYZW( i, p.currentQ.x, p.currentQ.y, p.currentQ.z, p.currentQ.w )

    p.orientations.needsUpdate = True
    p.lastTime = time


def onWindowResize(event, p):
    p.camera.aspect = window.innerWidth / window.innerHeight
    p.camera.updateProjectionMatrix()

    p.renderer.setSize( window.innerWidth, window.innerHeight )


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener('animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
