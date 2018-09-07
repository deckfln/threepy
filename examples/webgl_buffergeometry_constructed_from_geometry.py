"""
    <title>three.js webgl - buffer geometry constructed from geometry</title>
"""
import math

from THREE import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.controls.TrackballControls import *


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.controls = None
        self.container = None
        self.mesh = None


def init(p):
    p.container = pyOpenGL(p)
    p.container.addEventListener('resize', onWindowResize, False)
    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize(window.innerWidth, window.innerHeight)

    p.scene = THREE.Scene()

    p.camera = THREE.PerspectiveCamera(45.0, window.innerWidth / window.innerHeight, 100, 1500.0)
    p.camera.position.z = 480.0

    p.scene.add(THREE.AmbientLight(0x444444))

    light1 = THREE.DirectionalLight(0x999999, 0.1)
    light1.position.set(1, 1, 1)
    p.scene.add(light1)

    light2 = THREE.DirectionalLight(0x999999, 1.5)
    light2.position.set(0, -1, 0)
    p.scene.add(light2)

    p.controls = TrackballControls(p.camera, p.container)
    p.controls.minDistance = 100.0
    p.controls.maxDistance = 800.0
    p.controls.dynamicDampingFactor = 0.1

    createScene(p)


def createGeometry():
    heartShape = THREE.Shape()    # From http://blog.burlock.org/html5/130-paths
    x = 0
    y = 0

    heartShape.moveTo(x + 25, y + 25)
    heartShape.bezierCurveTo(x + 25, y + 25, x + 20, y, x, y)
    heartShape.bezierCurveTo(x - 30, y, x - 30, y + 35, x - 30, y + 35)
    heartShape.bezierCurveTo(x - 30, y + 55, x - 10, y + 77, x + 25, y + 95)
    heartShape.bezierCurveTo(x + 60, y + 77, x + 80, y + 55, x + 80, y + 35)
    heartShape.bezierCurveTo(x + 80, y + 35, x + 80, y, x + 50, y)
    heartShape.bezierCurveTo(x + 35, y, x + 25, y + 25, x + 25, y + 25)

    extrudeSettings = {
        'depth': 16,
        'bevelEnabled': True,
        'bevelSegments': 1,
        'steps': 2,
        'bevelSize': 1,
        'bevelThickness': 1
    }

    geometry = THREE.ExtrudeGeometry(heartShape, extrudeSettings)
    geometry.rotateX(math.pi)
    geometry.scale(0.4, 0.4, 0.4)

    return geometry


def createScene(p):
    bufferGeometry = THREE.BufferGeometry()

    radius = 125
    count = 80

    positions = []
    normals = []
    colors = []

    spherical = THREE.Spherical()
    vector = THREE.Vector3()

    for i in range(count):
        phi = math.acos(-1 + (2 * i) / count)
        theta = math.sqrt(count * math.pi) * phi

        spherical.set(radius, phi, theta)
        vector.setFromSpherical(spherical)

        geometry = createGeometry()

        geometry.lookAt(vector)
        geometry.translate(vector.x, vector.y, vector.z)

        color = THREE.Color(0xffffff)
        color.setHSL((i / count), 1.0, 0.7)

        for face in geometry.faces:
            positions.append(geometry.vertices[face.a].x)
            positions.append(geometry.vertices[face.a].y)
            positions.append(geometry.vertices[face.a].z)
            positions.append(geometry.vertices[face.b].x)
            positions.append(geometry.vertices[face.b].y)
            positions.append(geometry.vertices[face.b].z)
            positions.append(geometry.vertices[face.c].x)
            positions.append(geometry.vertices[face.c].y)
            positions.append(geometry.vertices[face.c].z)

            normals.append(face.normal.x)
            normals.append(face.normal.y)
            normals.append(face.normal.z)
            normals.append(face.normal.x)
            normals.append(face.normal.y)
            normals.append(face.normal.z)
            normals.append(face.normal.x)
            normals.append(face.normal.y)
            normals.append(face.normal.z)

            colors.append(color.r)
            colors.append(color.g)
            colors.append(color.b)
            colors.append(color.r)
            colors.append(color.g)
            colors.append(color.b)
            colors.append(color.r)
            colors.append(color.g)
            colors.append(color.b)

    bufferGeometry.addAttribute('position', THREE.Float32BufferAttribute(positions, 3))
    bufferGeometry.addAttribute('normal', THREE.Float32BufferAttribute(normals, 3))
    bufferGeometry.addAttribute('color', THREE.Float32BufferAttribute(colors, 3))

    material = THREE.MeshPhongMaterial({
        'shininess': 80,
        'vertexColors': THREE.VertexColors
    })

    mesh = THREE.Mesh(bufferGeometry, material)
    p.scene.add(mesh)


def onWindowResize(event, params):
    params.camera.aspect = window.innerWidth / window.innerHeight
    params.camera.updateProjectionMatrix()

    params.renderer.setSize(window.innerWidth, window.innerHeight)


def animate(p):
    p.controls.update()
    render(p)


def render(p):
    p.renderer.render(p.scene, p.camera)


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener('animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
