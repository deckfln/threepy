"""
<title>three.js webgl - custom attributes [particles][billboards][alphatest]</title>
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
    attribute float indice;
    attribute vec4 ca;

    varying vec4 vColor;

    uniform float time;
    
    void main() {

        vColor = ca;

        vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);

        float size;
        if (indice > 0) {
            size = max(0.0, 26.0 + 32.0 * sin(0.1 * indice + 0.6 * time));
        }
        else {
            size = 40;
        }

        gl_PointSize = size * (150.0 / -mvPosition.z);

        gl_Position = projectionMatrix * mvPosition;

    }
"""


fragmentshader = """
    uniform vec3 color;
    uniform sampler2D texture;

    varying vec4 vColor;

    void main() {

        vec4 outColor = texture2D(texture, gl_PointCoord);

        if (outColor.a < 0.5) discard;

        gl_FragColor = outColor * vec4(color * vColor.xyz, 1.0);

        float depth = gl_FragCoord.z / gl_FragCoord.w;
        const vec3 fogColor = vec3(0.0);

        float fogFactor = smoothstep(200.0, 600.0, depth);
        gl_FragColor = mix(gl_FragColor, vec4(fogColor, gl_FragColor.w), fogFactor);

    }
"""


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.geometry = None
        self.object = None
        self.uniforms = None
        self.attributes = None
        self.vertices1 = None
        self.uniforms = None


def init(p):
    p.container = pyOpenGL(p)
    p.container.addEventListener('resize', onWindowResize, False)
    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize(window.innerWidth, window.innerHeight)

    p.camera = THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 1, 1000)
    p.camera.position.z = 500

    p.scene = THREE.Scene()

    radius = 100
    inner = 0.6 * radius
    vertices = []

    for i in range(100000):
        vertex = THREE.Vector3()
        vertex.x = random.random() * 2 - 1
        vertex.y = random.random() * 2 - 1
        vertex.z = random.random() * 2 - 1
        vertex.multiplyScalar(radius)

        if (vertex.x > inner or vertex.x < -inner) or \
             (vertex.y > inner or vertex.y < -inner) or \
             (vertex.z > inner or vertex.z < -inner):

            vertices.append(vertex)

    p.vertices1 = len(vertices)

    radius = 200
    geometry2 = THREE.BoxGeometry(radius, 0.1 * radius, 0.1 * radius, 50, 5, 5)

    matrix = THREE.Matrix4()
    position = THREE.Vector3()
    rotation = THREE.Euler()
    quaternion = THREE.Quaternion()
    scale = THREE.Vector3(1, 1, 1)

    def addGeo(geo, x, y, z, ry):
        position.set(x, y, z)
        rotation.set(0, ry, 0)

        matrix.compose(position, quaternion.setFromEuler(rotation), scale)

        for vertex in geo.vertices:
            vertices.append(vertex.clone().applyMatrix4(matrix))

    # side 1

    addGeo(geometry2, 0,  110,  110, 0)
    addGeo(geometry2, 0,  110, -110, 0)
    addGeo(geometry2, 0, -110,  110, 0)
    addGeo(geometry2, 0, -110, -110, 0)

    # side 2

    addGeo(geometry2,  110,  110, 0, math.pi/2)
    addGeo(geometry2,  110, -110, 0, math.pi/2)
    addGeo(geometry2, -110,  110, 0, math.pi/2)
    addGeo(geometry2, -110, -110, 0, math.pi/2)

    # corner edges

    geometry3 = THREE.BoxGeometry(0.1 * radius, radius * 1.2, 0.1 * radius, 5, 60, 5)

    addGeo(geometry3,  110, 0,  110, 0)
    addGeo(geometry3,  110, 0, -110, 0)
    addGeo(geometry3, -110, 0,  110, 0)
    addGeo(geometry3, -110, 0, -110, 0)

    vl = len(vertices)
    positions = Float32Array(vl * 3)
    colors = Float32Array(vl * 3)
    sizes = Float32Array(vl)
    indices = Uint32Array(vl)

    color = THREE.Color()

    for i in range(vl):
        vertex = vertices[ i ]
        vertex.toArray(positions, i * 3)

        if i < p.vertices1:
            color.setHSL(0.5 + 0.2 * (i / p.vertices1), 1, 0.5)

        else:
            color.setHSL(0.1, 1, 0.5)

        color.toArray(colors, i * 3)

        # sizes[ i ] = 10 if i < p.vertices1 else 40

        if i < p.vertices1:
            indices[i] = i
        else:
            indices[i] = 0

    geometry = THREE.BufferGeometry()
    geometry.addAttribute('position', THREE.BufferAttribute(positions, 3))
    geometry.addAttribute('ca', THREE.BufferAttribute(colors, 3))
    geometry.addAttribute('size', THREE.BufferAttribute(sizes, 1))
    geometry.addAttribute('indice', THREE.BufferAttribute(indices, 1))

    #

    texture = THREE.TextureLoader().load("textures/sprites/ball.png")
    texture.wrapS = THREE.RepeatWrapping
    texture.wrapT = THREE.RepeatWrapping

    material = THREE.ShaderMaterial({
        'uniforms': {
            'time': { 'value': 0.0 },
            'amplitude': { 'value': 1.0 },
            'color':     { 'value': THREE.Color(0xffffff) },
            'texture':   { 'value': texture }
        },
        'vertexShader':   vertexshader,
        'fragmentShader': fragmentshader
    })
    p.uniforms = material.uniforms

    #

    p.object = THREE.Points(geometry, material)
    p.scene.add(p.object)

    #

    p.gui = pyGUI(p.renderer)
    p.gui.add(Stats())


def onWindowResize(event, params):
    params.camera.aspect = window.innerWidth / window.innerHeight
    params.camera.updateProjectionMatrix()

    params.renderer.setSize(window.innerWidth, window.innerHeight)


def animate(p):
    render(p)
    p.gui.update()


def render(p):
    global time, limit
    time = datetime.now().timestamp() * 2
    p.object.rotation.y = p.object.rotation.z = 0.02 * time

    time = time - int(time)
    time *= math.pi

    p.uniforms.time.value = time

    """
    geometry = p.object.geometry
    attributes = geometry.attributes
    array = attributes.size.array

    for i in range(len(array)):
        if i < p.vertices1:
            array[i] = max(0, 26 + 32 * math.sin(0.1 * i + 0.6 * time))

    attributes.size.needsUpdate = True
    """
    p.renderer.render(p.scene, p.camera)

    
def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener('animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
