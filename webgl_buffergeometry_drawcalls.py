"""
        <title>three.js webgl - buffergeometry - lines drawcalls</title>
"""
import random
from datetime import datetime
from THREE import *


WIDTH = 640
HEIGHT = 480
camera = None
scene=None
renderer=None
mesh = None
geometry = None

group = None
particlesData = []
positions = None
colors = None
particles = None
particlePositions = None
linesMesh = None

maxParticleCount = 1000
particleCount = 500
r = 800
rHalf = r / 2


class EffectController:
    def __init__(self):
        self.showDots = True
        self.showLines = True
        self.minDistance = 150
        self.limitConnections = False
        self.maxConnections = 20
        self.particleCount = 500


class ParticleData:
    def __init__(self, velocity, numConnections):
        self.velocity = velocity
        self.numConnections = numConnections


effectController = EffectController()


def init():
    global camera, scene, particlePositions,particles,maxParticleCount, particleData, particleCount, linesMesh,pointCloud
    global positions, colors, lineMesh, group

    camera = THREE.PerspectiveCamera( 45, WIDTH / HEIGHT, 1, 4000 )
    camera.position.z = 1750

    scene = THREE.Scene()

    group = THREE.Group()
    scene.add( group )

    helper = THREE.BoxHelper( THREE.Mesh( THREE.BoxGeometry( r, r, r ) ) )
    helper.material.color.setHex( 0x080808 )
    helper.material.blending = THREE.AdditiveBlending
    helper.material.transparent = True
    group.add( helper )

    segments = maxParticleCount * maxParticleCount

    positions = Float32Array( segments * 3 )
    colors = Float32Array( segments * 3 )

    pMaterial = THREE.PointsMaterial( {
        'color': 0xFFFFFF,
        'size': 3,
        'blending': THREE.AdditiveBlending,
        'transparent': True,
        'sizeAttenuation': False
    } )

    particles = THREE.BufferGeometry()
    particlePositions = Float32Array( maxParticleCount * 3 )

    for i in range(maxParticleCount):
        x = random.random() * r - r / 2
        y = random.random() * r - r / 2
        z = random.random() * r - r / 2

        particlePositions[ i * 3     ] = x
        particlePositions[ i * 3 + 1 ] = y
        particlePositions[ i * 3 + 2 ] = z

        # // add it to the geometry
        particlesData.append( ParticleData(
            THREE.Vector3( -1 + random.random() * 2, -1 + random.random() * 2,  -1 + random.random() * 2 ),
            0
        ))

    particles.setDrawRange( 0, particleCount )
    particles.addAttribute( 'position', THREE.BufferAttribute( particlePositions, 3 ).setDynamic( True ) )

    # // create the particle system
    pointCloud = THREE.Points( particles, pMaterial )
    group.add( pointCloud )

    geometry = THREE.BufferGeometry()

    geometry.addAttribute( 'position', THREE.BufferAttribute( positions, 3 ).setDynamic( True ) )
    geometry.addAttribute( 'color', THREE.BufferAttribute( colors, 3 ).setDynamic( True ) )

    geometry.computeBoundingSphere()

    geometry.setDrawRange( 0, 0 )

    material = THREE.LineBasicMaterial( {
        'vertexColors': THREE.VertexColors,
        'blending': THREE.AdditiveBlending,
        'transparent': True
    } )

    linesMesh = THREE.LineSegments( geometry, material )
    group.add( linesMesh )

    # //

    renderer = pyOpenGLRenderer(None, reshape, render, keyboard, mouse, motion, animate)
    renderer.setPixelRatio( 1 )
    renderer.setSize( WIDTH, HEIGHT )

    renderer.gammaInput = True
    renderer.gammaOutput = True

    # //
    return renderer


def animate():
    global particleCount, particlesData, particlePositions,effectController, linesMesh, pointCloud
    global positions, colors

    vertexpos = 0
    colorpos = 0
    numConnected = 0

    for i in range(particleCount):
        particlesData[ i ].numConnections = 0
        # // get the particle
        particleData = particlesData[i]

        particlePositions[ i * 3     ] += particleData.velocity.x
        particlePositions[ i * 3 + 1 ] += particleData.velocity.y
        particlePositions[ i * 3 + 2 ] += particleData.velocity.z

        if particlePositions[ i * 3 + 1 ] < -rHalf or particlePositions[ i * 3 + 1 ] > rHalf:
            particleData.velocity.y = -particleData.velocity.y

        if particlePositions[ i * 3 ] < -rHalf or particlePositions[ i * 3 ] > rHalf:
            particleData.velocity.x = -particleData.velocity.x

        if particlePositions[ i * 3 + 2 ] < -rHalf or particlePositions[ i * 3 + 2 ] > rHalf:
            particleData.velocity.z = -particleData.velocity.z

        if effectController.limitConnections and particleData.numConnections >= effectController.maxConnections:
            continue

        # // Check collision
        for j in range(i + 1, particleCount):
            particleDataB = particlesData[ j ]
            if effectController.limitConnections and particleDataB.numConnections >= effectController.maxConnections:
                continue

            dx = particlePositions[ i * 3     ] - particlePositions[ j * 3     ]
            dy = particlePositions[ i * 3 + 1 ] - particlePositions[ j * 3 + 1 ]
            dz = particlePositions[ i * 3 + 2 ] - particlePositions[ j * 3 + 2 ]
            dist = math.sqrt( dx * dx + dy * dy + dz * dz )

            if dist < effectController.minDistance:
                particleData.numConnections += 1
                particleDataB.numConnections += 1

                alpha = 1.0 - dist / effectController.minDistance

                positions[ vertexpos ] = particlePositions[ i * 3     ]
                positions[ vertexpos + 1 ] = particlePositions[ i * 3 + 1 ]
                positions[ vertexpos + 2 ] = particlePositions[ i * 3 + 2 ]
                vertexpos += 3

                positions[ vertexpos ] = particlePositions[ j * 3     ]
                positions[ vertexpos + 1 ] = particlePositions[ j * 3 + 1 ]
                positions[ vertexpos + 2 ] = particlePositions[ j * 3 + 2 ]
                vertexpos += 3

                colors[ colorpos  ] = alpha
                colors[ colorpos + 1 ] = alpha
                colors[ colorpos + 2 ] = alpha
                colorpos += 3

                colors[ colorpos ] = alpha
                colors[ colorpos + 1 ] = alpha
                colors[ colorpos + 2 ] = alpha
                colorpos += 3

                numConnected += 1

    linesMesh.geometry.setDrawRange( 0, numConnected * 2 )
    linesMesh.geometry.attributes.position.needsUpdate = True
    linesMesh.geometry.attributes.color.needsUpdate = True

    pointCloud.geometry.attributes.position.needsUpdate = True

    render()

def render():
    global group, scene, camera
    time = datetime.now().timestamp()

    group.rotation.y = time * 0.1
    renderer.render( scene, camera )

def reshape(width, height):
    """window reshape callback."""
    global camera, renderer

    camera.aspect = width / height
    camera.updateProjectionMatrix()

    renderer.setSize(width, height)

    glViewport(0, 0, width, height)


def mouse(button, state, x, y):
    if button == GLUT_LEFT_BUTTON:
        rotating = (state == GLUT_DOWN)
    elif button == GLUT_RIGHT_BUTTON:
        scaling = (state == GLUT_DOWN)


def motion(x1, y1):
    glutPostRedisplay()


def keyboard(c, x=0, y=0):
    """keyboard callback."""

    if c == b'q':
        sys.exit(0)

    glutPostRedisplay()


"""
"""


def main(argv=None):
    global renderer, camera, scene

    renderer = init()
    return renderer.loop()


if __name__ == "__main__":
    sys.exit(main())
