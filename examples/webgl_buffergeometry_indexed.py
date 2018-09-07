"""
    <title>three.js webgl - buffergeometry - indexed</title>
"""

import math
from datetime import datetime

from THREE import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.controls.TrackballControls import *


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.container = None
        self.mesh = None


def init(p):
    p.container = pyOpenGL(p)
    p.container.addEventListener('resize', onWindowResize, False)
    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize(window.innerWidth, window.innerHeight)

    p.camera = THREE.PerspectiveCamera(27, window.innerWidth / window.innerHeight, 1, 3500)
    p.camera.position.z = 64

    p.scene = THREE.Scene()
    p.scene.background = THREE.Color(0x050505)

    #

    ambientLight = THREE.AmbientLight(0x222222)
    p.scene.add(ambientLight)

    light1 = THREE.DirectionalLight(0xffffff, 0.5)
    light1.position.set(1, 1, 1)
    p.scene.add(light1)

    light2 = THREE.DirectionalLight(0xffffff, 1)
    light2.position.set(0, - 1, 0)
    p.scene.add(light2)

    #

    geometry = THREE.BufferGeometry()

    indices = []

    vertices = []
    normals = []
    colors = []

    size = 20
    segments = 10

    halfSize = size / 2
    segmentSize = size / segments

    # generate vertices, normals and color data for a simple grid geometry

    for i in range(segments+1):
        y = (i * segmentSize) - halfSize

        for j in range(segments+1):
            x = (j * segmentSize) - halfSize

            vertices.extend([x, - y, 0])
            normals.extend([0, 0, 1])

            r = (x / size) + 0.5
            g = (y / size) + 0.5

            colors.extend([r, g, 1])

    # generate indices (data for element array buffer)

    for i in range(segments):
        for j in range(segments):

            a = i * (segments + 1) + (j + 1)
            b = i * (segments + 1) + j
            c = (i + 1) * (segments + 1) + j
            d = (i + 1) * (segments + 1) + (j + 1)

            # generate two faces (triangles) per iteration

            indices.extend([a, b, d])    # face one
            indices.extend([b, c, d])    # face two

    #

    geometry.setIndex(indices)
    geometry.addAttribute('position', THREE.Float32BufferAttribute(vertices, 3))
    geometry.addAttribute('normal', THREE.Float32BufferAttribute(normals, 3))
    geometry.addAttribute('color', THREE.Float32BufferAttribute(colors, 3))

    material = THREE.MeshPhongMaterial({
        'specular': 0x111111,
        'shininess': 250,
        'side': THREE.DoubleSide, 
        'vertexColors': THREE.VertexColors
    })

    p.mesh = THREE.Mesh(geometry, material)
    p.scene.add(p.mesh)


def onWindowResize(event, params):
    params.camera.aspect = window.innerWidth / window.innerHeight
    params.camera.updateProjectionMatrix()

    params.renderer.setSize(window.innerWidth, window.innerHeight)


def animate(p):
    render(p)

    
def render(p):
    time = datetime.now().timestamp() * 1

    p.mesh.rotation.x = time * 0.25
    p.mesh.rotation.y = time * 0.5

    p.renderer.render(p.scene, p.camera)


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener('animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
