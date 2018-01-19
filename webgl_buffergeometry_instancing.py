"""
    <title>three.js webgl - instancing test (single triangle)</title>
"""
import random

from datetime import datetime

from THREE import *
import THREE._Math as _Math
from THREE.pyOpenGL.pyOpenGL import *

class Params:
    def __init__(self):
        self.container = None
        self.stats = None
        self.camera = None
        self.scene = None


vertexShader = """
        // precision highp float;

        uniform float sineTime;

        uniform mat4 modelViewMatrix;
        uniform mat4 projectionMatrix;

        attribute vec3 position;
        attribute vec3 offset;
        attribute vec4 color;
        attribute vec4 orientationStart;
        attribute vec4 orientationEnd;

        varying vec3 vPosition;
        varying vec4 vColor;

        void main(){

            vPosition = offset * max(abs(sineTime * 2.0 + 1.0), 0.5) + position;
            vec4 orientation = normalize(mix(orientationStart, orientationEnd, sineTime));
            vec3 vcV = cross(orientation.xyz, vPosition);
            vPosition = vcV * (2.0 * orientation.w) + (cross(orientation.xyz, vcV) * 2.0 + vPosition);

            vColor = color;

            gl_Position = projectionMatrix * modelViewMatrix * vec4( vPosition, 1.0 );

        }
"""

fragmentShader = """
        // precision highp float;

        uniform float time;

        varying vec3 vPosition;
        varying vec4 vColor;

        void main() {

            vec4 color = vec4( vColor );
            color.r += sin( vPosition.x * 10.0 + time ) * 0.5;

            gl_FragColor = color;

        }
"""


def init(p):
    p.container = pyOpenGL(p)
    p.container.addEventListener('resize', onWindowResize, False)
    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize(window.innerWidth, window.innerHeight)

    p.camera = THREE.PerspectiveCamera( 50, window.innerWidth / window.innerHeight, 1, 10 )
    p.camera.position.z = 2

    p.scene = THREE.Scene()
    p.scene.background = THREE.Color( 0x101010 )

    # geometry

    triangles = 1
    instances = 65000

    geometry = THREE.InstancedBufferGeometry()

    geometry.maxInstancedCount = instances     # set so its initalized for dat.GUI, will be set in first draw otherwise
    # gui = dat.GUI()
    # gui.add( geometry, "maxInstancedCount", 0, instances )

    vertices = THREE.BufferAttribute( Float32Array( triangles * 3 * 3 ), 3 )

    vertices.setXYZ( 0, 0.025, -0.025, 0 )
    vertices.setXYZ( 1, -0.025, 0.025, 0 )
    vertices.setXYZ( 2, 0, 0, 0.025 )

    geometry.addAttribute( 'position', vertices )

    offsets = THREE.InstancedBufferAttribute( Float32Array( instances * 3 ), 3, 1 )

    for i in range(offsets.count):
        offsets.setXYZ( i, random.random() - 0.5, random.random() - 0.5, random.random() - 0.5 )

    geometry.addAttribute( 'offset', offsets )

    colors = THREE.InstancedBufferAttribute( Float32Array( instances * 4 ), 4, 1 )

    for i in range(colors.count):
        colors.setXYZW( i, random.random(), random.random(), random.random(), random.random() )

    geometry.addAttribute( 'color', colors )

    vector = THREE.Vector4()

    orientationsStart = THREE.InstancedBufferAttribute( Float32Array( instances * 4 ), 4, 1 )

    for i in range(orientationsStart.count):
        vector.set( random.random() * 2 - 1, random.random() * 2 - 1, random.random() * 2 - 1, random.random() * 2 - 1 )
        vector.normalize()

        orientationsStart.setXYZW( i, vector.x, vector.y, vector.z, vector.w )

    geometry.addAttribute( 'orientationStart', orientationsStart )

    orientationsEnd = THREE.InstancedBufferAttribute( Float32Array( instances * 4 ), 4, 1 )

    for i in range(orientationsEnd.count):
        vector.set( random.random() * 2 - 1, random.random() * 2 - 1, random.random() * 2 - 1, random.random() * 2 - 1 )
        vector.normalize()

        orientationsEnd.setXYZW( i, vector.x, vector.y, vector.z, vector.w )

    geometry.addAttribute( 'orientationEnd', orientationsEnd )

    # material

    material = THREE.RawShaderMaterial( {
        'uniforms': {
            'time': UniformValue(1.0),
            'sineTime': UniformValue(1.0)
        },
        'vertexShader': vertexShader,
        'fragmentShader': fragmentShader,
        'side': THREE.DoubleSide,
        'transparent': True

    } )

    p.mesh = THREE.Mesh( geometry, material )
    p.scene.add( p.mesh )


def animate(p):
    render(p)

    
def render(p):
    time = datetime.now().timestamp()

    object = p.scene.children[0]

    object.rotation.y = time * 0.01
    object.material.uniforms.time.value = time * 0.1
    object.material.uniforms.sineTime.value = math.sin( object.material.uniforms.time.value )

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
