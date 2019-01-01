"""
        <title>three.js webgl - geometry - vertex colors</title>
"""
import sys, os.path
mango_dir = (os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(mango_dir)

from PIL import Image
from THREE import *

import math
from THREE.pyOpenGL.pyOpenGL import *


class Params:
    def __init__(self):
        self.container = None
        self.camera = None
        self.scene = None
        self.renderer = None
        self.mouseX = 0
        self.mouseY = 0
        self.windowHalfX = 0
        self.windowHalfY = 0


def init(p):
    p.container = pyOpenGL(p)

    p.windowHalfX = window.innerWidth / 2
    p.windowHalfY = window.innerHeight / 2

    p.camera = THREE.PerspectiveCamera(20, window.innerWidth / window.innerHeight, 1, 10000)
    p.camera.position.z = 1800

    p.scene = THREE.Scene()
    p.scene.background = THREE.Color(0xffffff)

    p.light = THREE.DirectionalLight(0xffffff)
    p.light.position.set(0, 0, 1)
    p.scene.add(p.light)

    # // shadow
    #  https: // stackoverflow.com / questions / 30608035 / plot - gradients - using - pil - in -python
    image = Image.new('RGBA', (128, 128))  # Create the image
    innerColor = [210, 210, 210]  # Color at the center
    outerColor = [255, 255, 255]  # Color at the corners

    for y in range(128):
        for x in range(128):
            # Find the distance to the center
            distanceToCenter = math.sqrt((x - 128 / 2) ** 2 + (y - 128 / 2) ** 2)

            # Make it on a scale from 0 to 1
            distanceToCenter = float(distanceToCenter) / (math.sqrt(2) * 128 / 2)

            # Calculate r, g, and b values
            r = outerColor[0] * distanceToCenter + innerColor[0] * (1 - distanceToCenter)
            g = outerColor[1] * distanceToCenter + innerColor[1] * (1 - distanceToCenter)
            b = outerColor[2] * distanceToCenter + innerColor[2] * (1 - distanceToCenter)

            # Place the pixel
            image.putpixel((x, y), (int(r), int(g), int(b)))

    shadowTexture = THREE.Texture(image)
    shadowTexture.needsUpdate = True

    shadowMaterial = THREE.MeshBasicMaterial({'map': shadowTexture})
    shadowGeo = THREE.PlaneBufferGeometry(300, 300, 1, 1)

    shadowMesh = THREE.Mesh(shadowGeo, shadowMaterial)
    shadowMesh.position.y = - 250
    shadowMesh.rotation.x = - math.pi / 2
    p.scene.add( shadowMesh )

    shadowMesh = THREE.Mesh(shadowGeo, shadowMaterial)
    shadowMesh.position.y = - 250
    shadowMesh.position.x = - 400
    shadowMesh.rotation.x = - math.pi / 2
    p.scene.add( shadowMesh )

    shadowMesh = THREE.Mesh(shadowGeo, shadowMaterial)
    shadowMesh.position.y = - 250
    shadowMesh.position.x = 400
    shadowMesh.rotation.x = - math.pi / 2
    p.scene.add( shadowMesh )

    radius = 200

    geometry1 = THREE.IcosahedronBufferGeometry(radius, 1)

    count = geometry1.attributes.position.count
    geometry1.addAttribute('color', THREE.BufferAttribute(Float32Array(count * 3), 3))

    geometry2 = geometry1.clone()
    geometry3 = geometry1.clone()

    color = THREE.Color()
    positions1 = geometry1.attributes.position
    positions2 = geometry2.attributes.position
    positions3 = geometry3.attributes.position
    colors1 = geometry1.attributes.color
    colors2 = geometry2.attributes.color
    colors3 = geometry3.attributes.color

    for i in range(count):
        color.setHSL( ( positions1.getY( i ) / radius + 1 ) / 2, 1.0, 0.5 )
        colors1.setXYZ( i, color.r, color.g, color.b )

        color.setHSL( 0, ( positions2.getY( i ) / radius + 1 ) / 2, 0.5 )
        colors2.setXYZ( i, color.r, color.g, color.b )

        color.setRGB( 1, 0.8 - ( positions3.getY( i ) / radius + 1 ) / 2, 0 )
        colors3.setXYZ( i, color.r, color.g, color.b )

    material = THREE.MeshPhongMaterial( {
        'color': 0xffffff,
        'flatShading': True,
        'vertexColors': THREE.VertexColors,
        'shininess': 0
    } )

    wireframeMaterial = THREE.MeshBasicMaterial({'color': 0x000000, 'wireframe': True, 'transparent': True})

    mesh = THREE.Mesh(geometry1, material)
    wireframe = THREE.Mesh(geometry1, wireframeMaterial)
    mesh.add(wireframe)
    mesh.position.x = - 400
    mesh.rotation.x = - 1.87
    p.scene.add(mesh)

    mesh = THREE.Mesh(geometry2, material)
    wireframe = THREE.Mesh(geometry2, wireframeMaterial)
    mesh.add(wireframe)
    mesh.position.x = 400
    p.scene.add(mesh)

    mesh = THREE.Mesh(geometry3, material)
    wireframe = THREE.Mesh(geometry3, wireframeMaterial)
    mesh.add(wireframe)
    p.scene.add(mesh)

    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize(window.innerWidth, window.innerHeight)

    p.container.addEventListener('mousemove', onDocumentMouseMove, False)

    # //

    p.container.addEventListener('resize', onWindowResize, False)


def onWindowResize(event, p):
    p.windowHalfX = window.innerWidth / 2
    p.windowHalfY = window.innerHeight / 2

    p.camera.aspect = window.innerWidth / window.innerHeight
    p.camera.updateProjectionMatrix()

    p.renderer.setSize(window.innerWidth, window.innerHeight)

    
def onDocumentMouseMove( event, p ):
    p.mouseX = (event.clientX - p.windowHalfX)
    p.mouseY = (event.clientY - p.windowHalfY)


def animate(p):
    render(p)


def render(p):
    p.camera.position.x += (p.mouseX - p.camera.position.x) * 0.05
    p.camera.position.y += (- p.mouseY - p.camera.position.y) * 0.05

    p.camera.lookAt(p.scene.position)

    p.renderer.render(p.scene, p.camera)


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener('animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
