"""
        <title>three.js webgl - buffergeometry - uint</title>
"""        

import math
import random
from datetime import datetime

from THREE import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.pyOpenGL.pyGUI import *
from THREE.pyOpenGL.widgets.Stats import *


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


def init(p):
    p.container = pyOpenGL(p)
    p.container.addEventListener('resize', onWindowResize, False)
    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize(window.innerWidth, window.innerHeight)

    #

    p.camera = THREE.PerspectiveCamera(27, window.innerWidth / window.innerHeight, 1, 3500)
    p.camera.position.z = 2750

    p.scene = THREE.Scene()
    p.scene.background = THREE.Color(0x050505)
    p.scene.fog = THREE.Fog(0x050505, 2000, 3500)

    #

    p.scene.add(THREE.AmbientLight(0x444444))

    light1 = THREE.DirectionalLight(0xffffff, 0.5)
    light1.position.set(1, 1, 1)
    p.scene.add(light1)

    light2 = THREE.DirectionalLight(0xffffff, 1.5)
    light2.position.set(0, -1, 0)
    p.scene.add(light2)

    #

    triangles = 500000

    geometry = THREE.BufferGeometry()

    positions = []
    normals = []
    colors = []

    color = THREE.Color()

    n = 800
    n2 = n / 2    # triangles spread in the cube
    d = 12
    d2 = d / 2    # individual triangle size

    pA = THREE.Vector3()
    pB = THREE.Vector3()
    pC = THREE.Vector3()

    cb = THREE.Vector3()
    ab = THREE.Vector3()

    for i in range(triangles):
        # positions

        x = random.random() * n - n2
        y = random.random() * n - n2
        z = random.random() * n - n2

        ax = x + random.random() * d - d2
        ay = y + random.random() * d - d2
        az = z + random.random() * d - d2

        bx = x + random.random() * d - d2
        by = y + random.random() * d - d2
        bz = z + random.random() * d - d2

        cx = x + random.random() * d - d2
        cy = y + random.random() * d - d2
        cz = z + random.random() * d - d2

        positions.extend([ax, ay, az])
        positions.extend([bx, by, bz])
        positions.extend([cx, cy, cz])

        # flat face normals

        pA.set(ax, ay, az)
        pB.set(bx, by, bz)
        pC.set(cx, cy, cz)

        cb.subVectors(pC, pB)
        ab.subVectors(pA, pB)
        cb.cross(ab)

        cb.normalize()

        nx = cb.x
        ny = cb.y
        nz = cb.z

        normals.append([nx * 32767, ny * 32767, nz * 32767])
        normals.append([nx * 32767, ny * 32767, nz * 32767])
        normals.append([nx * 32767, ny * 32767, nz * 32767])

        # colors

        vx = (x / n) + 0.5
        vy = (y / n) + 0.5
        vz = (z / n) + 0.5

        color.setRGB(vx, vy, vz)

        colors.append([color.r * 255, color.g * 255, color.b * 255])
        colors.append([color.r * 255, color.g * 255, color.b * 255])
        colors.append([color.r * 255, color.g * 255, color.b * 255])

    positionAttribute = THREE.Float32BufferAttribute(positions, 3)
    normalAttribute = THREE.Int16BufferAttribute(normals, 3)
    colorAttribute = THREE.Uint8BufferAttribute(colors, 3)

    normalAttribute.normalized = True	 # this will map the buffer values to 0.0f - +1.0f in the shader
    colorAttribute.normalized = True

    geometry.addAttribute('position', positionAttribute)
    geometry.addAttribute('normal', normalAttribute)
    geometry.addAttribute('color', colorAttribute)

    geometry.computeBoundingSphere()

    material = THREE.MeshPhongMaterial({
        'color': 0xaaaaaa, 'specular': 0xffffff, 'shininess': 250,
        'side': THREE.DoubleSide, 'vertexColors': THREE.VertexColors
    })

    p.mesh = THREE.Mesh(geometry, material)
    p.scene.add(p.mesh)

    #
    p.gui = pyGUI(p.renderer)
    p.gui.add(Stats())


def onWindowResize(event, params):
    params.camera.aspect = window.innerWidth / window.innerHeight
    params.camera.updateProjectionMatrix()

    params.renderer.setSize( window.innerWidth, window.innerHeight )


def animate(p):
    time = datetime.now().timestamp() * 0.1

    p.mesh.rotation.x = time * 0.25
    p.mesh.rotation.y = time * 0.5

    p.renderer.render(p.scene, p.camera)
    p.gui.update()


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener('animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
