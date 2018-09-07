"""
    <title>three.js webgl - indexed instancing (single box), interleaved buffers, dynamic updates</title>
"""
from datetime import datetime
import random

from THREE import *
from THREE.core.InstancedInterleavedBuffer import *
from THREE.pyOpenGL.pyOpenGL import *


vertexShader = """
    #version 330
    precision highp float;

    uniform mat4 modelViewMatrix;
    uniform mat4 projectionMatrix;

    attribute vec3 position;
    attribute vec3 offset;
    attribute vec2 uv;
    attribute vec4 orientation;

    varying vec2 vUv;

    // http://www.geeks3d.com/20141201/how-to-rotate-a-vertex-by-a-quaternion-in-glsl/

    vec3 applyQuaternionToVector(vec4 q, vec3 v){

        return v + 2.0 * cross(q.xyz, cross(q.xyz, v) + q.w * v);

    }

    void main() {

        vec3 vPosition = applyQuaternionToVector(orientation, position);

        vUv = uv;

        gl_Position = projectionMatrix * modelViewMatrix * vec4(offset + vPosition, 1.0);

    }
"""

fragmentShader = """
    #version 330
    precision highp float;

    uniform sampler2D map;

    varying vec2 vUv;

    void main() {

        gl_FragColor = texture2D(map, vUv);

    }
"""


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.container = None
        self.mesh = None
        self.orientations = None
        self.instanceBuffer = None
        self.lastTime = 0
        self.moveQ = (THREE.Quaternion(.5, .5, .5, 0.0)).normalize()
        self.tmpQ = THREE.Quaternion()
        self.currentQ = THREE.Quaternion()


def init(p):
    p.container = pyOpenGL(p)
    p.container.addEventListener('resize', onWindowResize, False)
    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize(window.innerWidth, window.innerHeight)

    p.camera = THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 1, 1000)
    # camera.position.z = 20

    p.scene = THREE.Scene()
    p.scene.background = THREE.Color(0x101010)

    # geometry

    instances = 5000

    geometry = THREE.InstancedBufferGeometry()

    # per mesh data x,y,z,w,u,v,s,t for 4-element alignment
    # only use x,y,z and u,v; but x, y, z, nx, ny, nz, u, v would be a good layout
    vertexBuffer = THREE.InterleavedBuffer(Float32Array([
        # Front
        -1, 1, 1, 0, 0, 0, 0, 0,
        1, 1, 1, 0, 1, 0, 0, 0,
        -1, -1, 1, 0, 0, 1, 0, 0,
        1, -1, 1, 0, 1, 1, 0, 0,
        # Back
        1, 1, -1, 0, 1, 0, 0, 0,
        -1, 1, -1, 0, 0, 0, 0, 0,
        1, -1, -1, 0, 1, 1, 0, 0,
        -1, -1, -1, 0, 0, 1, 0, 0,
        # Left
        -1, 1, -1, 0, 1, 1, 0, 0,
        -1, 1, 1, 0, 1, 0, 0, 0,
        -1, -1, -1, 0, 0, 1, 0, 0,
        -1, -1, 1, 0, 0, 0, 0, 0,
        # Right
        1, 1, 1, 0, 1, 0, 0, 0,
        1, 1, -1, 0, 1, 1, 0, 0,
        1, -1, 1, 0, 0, 0, 0, 0,
        1, -1, -1, 0, 0, 1, 0, 0,
        # Top
        -1, 1, 1, 0, 0, 0, 0, 0,
        1, 1, 1, 0, 1, 0, 0, 0,
        -1, 1, -1, 0, 0, 1, 0, 0,
        1, 1, -1, 0, 1, 1, 0, 0,
        # Bottom
        1, -1, 1, 0, 1, 0, 0, 0,
        -1, -1, 1, 0, 0, 0, 0, 0,
        1, -1, -1, 0, 1, 1, 0, 0,
        -1, -1, -1, 0, 0, 1, 0, 0
    ]), 8)

    # Use vertexBuffer, starting at offset 0, 3 items in position attribute
    positions = THREE.InterleavedBufferAttribute(vertexBuffer, 3, 0)
    geometry.addAttribute('position', positions)
    # Use vertexBuffer, starting at offset 4, 2 items in uv attribute
    uvs = THREE.InterleavedBufferAttribute(vertexBuffer, 2, 4)
    geometry.addAttribute('uv', uvs)

    indices = Uint16Array([
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
    ])

    geometry.setIndex(THREE.BufferAttribute(indices, 1))

    # per instance data
    p.instanceBuffer = InstancedInterleavedBuffer(Float32Array(instances * 8), 8, 1).setDynamic(True)
    offsets = THREE.InterleavedBufferAttribute(p.instanceBuffer, 3, 0)

    vector = THREE.Vector4()
    for i in range(offsets.count):
        x = random.random() * 100 - 50
        y = random.random() * 100 - 50
        z = random.random() * 100 - 50
        vector.set(x, y, z, 0).normalize()
        # move out at least 5 units from center in current direction
        offsets.setXYZ(i, x + vector.x * 5, y + vector.y * 5, z + vector.z * 5)

    geometry.addAttribute('offset', offsets)    # per mesh translation

    p.orientations = THREE.InterleavedBufferAttribute(p.instanceBuffer, 4, 4)

    for i in range(p.orientations.count):
        vector.set(random.random() * 2 - 1, random.random() * 2 - 1, random.random() * 2 - 1, random.random() * 2 - 1)
        vector.normalize()

        p.orientations.setXYZW(i, vector.x, vector.y, vector.z, vector.w)

    geometry.addAttribute('orientation', p.orientations)  # per mesh orientation

    # material
    texture = THREE.TextureLoader().load('textures/crate.gif')
    texture.anisotropy = p.renderer.capabilities.getMaxAnisotropy()

    material = THREE.RawShaderMaterial({
        'uniforms': {
            'map': {'value': texture}
        },
        'vertexShader': vertexShader,
        'fragmentShader': fragmentShader,
        'side': THREE.DoubleSide,
        'transparent': False
    })

    mesh = THREE.Mesh(geometry, material)
    mesh.frustumCulled = False
    p.scene.add(mesh)


def onWindowResize(event, params):
    params.camera.aspect = window.innerWidth / window.innerHeight
    params.camera.updateProjectionMatrix()

    params.renderer.setSize(window.innerWidth, window.innerHeight)


def animate(p):
    render(p)

    
def render(p):
    time = datetime.now().timestamp() * 1000

    object = p.scene.children[0]

    object.rotation.y = time * 0.00005

    p.renderer.render(p.scene, p.camera)

    delta = (time - p.lastTime) / 5000
    p.tmpQ.set(p.moveQ.x * delta, p.moveQ.y * delta, p.moveQ.z * delta, 1).normalize()

    for i in range(p.orientations.count):
        index = i * p.instanceBuffer.stride + p.orientations.offset
        p.currentQ.set(p.instanceBuffer.array[index], p.instanceBuffer.array[index + 1], p.instanceBuffer.array[index + 2], p.instanceBuffer.array[index + 3])
        p.currentQ.multiply(p.tmpQ)

        p.orientations.setXYZW(i, p.currentQ.x, p.currentQ.y, p.currentQ.z, p.currentQ.w)

    p.instanceBuffer.needsUpdate = True
    p.lastTime = time

    
def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener('animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
