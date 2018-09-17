"""
    <title>three.js webgl - instancing test</title>
"""    
import random

from datetime import datetime

from THREE import *
import THREE._Math as _Math
from THREE.pyOpenGL.pyOpenGL import *
from THREE.controls.TrackballControls import *


vertexShader = """
        precision highp float;

        attribute vec3 instancePosition;
        attribute vec4 instanceQuaternion;
        attribute vec3 instanceScale;

        vec3 applyTRS( vec3 position, vec3 translation, vec4 quaternion, vec3 scale ) {

            position *= scale;
            position += 2.0 * cross( quaternion.xyz, cross( quaternion.xyz, position ) + quaternion.w * position );
            return position + translation;

        }

        attribute vec3 color;
        varying vec3 vColor;

        void main(){

            vColor = color;

            vec3 transformed = applyTRS( position.xyz, instancePosition, instanceQuaternion, instanceScale );

            gl_Position = projectionMatrix * modelViewMatrix * vec4( transformed, 1.0 );

        }
"""

fragmentShader = """
        precision highp float;
        varying vec3 vColor;

        void main() {

            gl_FragColor = vec4( vColor, 1.0 );

        }
"""


class Params:
    def __init__(self):
        self.container = None
        self.camera = None
        self.scene = None
        self.renderer = None
        self.controls = None


def init(p):
    p.container = pyOpenGL(p)
    p.container.addEventListener('resize', onWindowResize, False)
    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize(window.innerWidth, window.innerHeight)

    p.camera = THREE.PerspectiveCamera( 50, window.innerWidth / window.innerHeight, 0.01, 100 )
    p.camera.position.z = 4

    p.controls = TrackballControls( p.camera, p.container )

    p.scene = THREE.Scene()
    p.scene.background = THREE.Color( 0x101010 )

    #

    # geometry = THREE.BoxBufferGeometry( 0.01, 0.01, 0.01 )
    geometry = THREE.IcosahedronBufferGeometry( 0.1, 1 )

    colors = []

    for i in range(geometry.attributes.position.count):
        colors.extend([ random.random(), random.random(), random.random() ])

    geometry.addAttribute( 'color', THREE.Float32BufferAttribute( colors, 3 ) )

    material = THREE.MeshBasicMaterial( { 'color': 0xff0000, 'vertexColors': THREE.VertexColors } )

    mesh = THREE.Mesh( geometry, material )
    # scene.add( mesh );

    #

    INSTANCE_COUNT = 100

    geometry2 = THREE.InstancedBufferGeometry().copy( geometry )

    instancePositions = []
    instanceQuaternions = []
    instanceScales = []

    for i in range(INSTANCE_COUNT):
        mesh = THREE.Mesh( geometry, material )
        p.scene.add( mesh )

        position = mesh.position
        quaternion = mesh.quaternion
        scale = mesh.scale

        position.set( random.random() * 2 - 1, random.random() * 2 - 1, random.random() * 2 - 1 )

        quaternion.set( random.random() * 2 - 1, random.random() * 2 - 1, random.random() * 2 - 1, random.random() * 2 - 1 )
        quaternion.normalize()

        scale.set( random.random() * 2, random.random() * 2, random.random() * 2 )

        instancePositions.extend([ position.x, position.y, position.z ])
        instanceQuaternions.extend([ quaternion.x, quaternion.y, quaternion.z, quaternion.w ])
        instanceScales.extend([ scale.x, scale.y, scale.z ])

    attribute = THREE.InstancedBufferAttribute( Float32Array( instancePositions ), 3 )
    geometry2.addAttribute( 'instancePosition', attribute )

    attribute = THREE.InstancedBufferAttribute( Float32Array( instanceQuaternions ), 4 )
    geometry2.addAttribute( 'instanceQuaternion', attribute )

    attribute = THREE.InstancedBufferAttribute( Float32Array( instanceScales ), 3 )
    geometry2.addAttribute( 'instanceScale', attribute )

    material = THREE.ShaderMaterial( {
        'uniforms': {},
        'vertexShader': vertexShader,
        'fragmentShader': fragmentShader
    } );

    mesh2 = THREE.Mesh( geometry2, material )
    mesh2.position.x = 0.1
    p.scene.add( mesh2 )


def animate(p):
    render(p)


def render(p):
    p.controls.update()

    p.renderer.render( p.scene, p.camera )


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
