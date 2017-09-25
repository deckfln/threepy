"""
        <title>three.js webgl - buffergeometry - lines drawcalls</title>
"""
import random
from datetime import datetime
from THREE import *
from THREE.pyOpenGL.pyOpenGL import *


WIDTH = 640
HEIGHT = 480
camera = None
scene=None
renderer=None
mesh = None
geometry = None

container = None
group = None
particlesData = []
positions = None
colors = None
particles = None
particlePositions = None
linesMesh = None

maxParticleCount = 1000
particleCount = 200
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
    global positions, colors, lineMesh, group, container, renderer

    container = pyOpenGL()
    container.addEventListener( 'resize', onWindowResize, False )
    container.addEventListener( 'animationRequest', animate )

    renderer = pyOpenGLRenderer({ 'antialias': False })
    size = renderer.getSize()

    camera = THREE.PerspectiveCamera( 45, size['width'] / size['height'], 1, 4000 )

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

    renderer.gammaInput = True
    renderer.gammaOutput = True

    # //
    return renderer


def animate():
    global particleCount, particlesData, particlePositions,effectController, linesMesh, pointCloud
    global positions, colors, renderer

    vertexpos = 0
    colorpos = 0
    numConnected = 0

    profiler.start()

    for particleData in particlesData:
        particleData.numConnections = 0

    for i in range(particleCount):
        # // get the particle
        particleData = particlesData[i]

        p = i*3
        particlePositions[ p     ] += particleData.velocity.x
        particlePositions[ p + 1 ] += particleData.velocity.y
        particlePositions[ p + 2 ] += particleData.velocity.z

        if particlePositions[ p + 1 ] < -rHalf or particlePositions[ p + 1 ] > rHalf:
            particleData.velocity.y = -particleData.velocity.y

        if not -rHalf <= particlePositions[ p ] <= rHalf:
            particleData.velocity.x = -particleData.velocity.x

        if not -rHalf <= particlePositions[ p + 2 ] <= rHalf:
            particleData.velocity.z = -particleData.velocity.z

        if effectController.limitConnections and particleData.numConnections >= effectController.maxConnections:
            continue

        # // Check collision
        for j in range(i + 1, particleCount):
            particleDataB = particlesData[ j ]
            if effectController.limitConnections and particleDataB.numConnections >= effectController.maxConnections:
                continue

            j3 = j * 3
            dx = particlePositions[ p     ] - particlePositions[ j3     ]
            dy = particlePositions[ p + 1 ] - particlePositions[ j3 + 1 ]
            dz = particlePositions[ p + 2 ] - particlePositions[ j3 + 2 ]
            dist = math.sqrt(dx * dx + dy * dy + dz * dz)

            if dist < effectController.minDistance:
                particleData.numConnections += 1
                particleDataB.numConnections += 1

                alpha = 1.0 - dist / effectController.minDistance

                positions[ vertexpos ] = particlePositions[ p     ]
                positions[ vertexpos + 1 ] = particlePositions[ p + 1 ]
                positions[ vertexpos + 2 ] = particlePositions[ p + 2 ]
                vertexpos += 3

                positions[ vertexpos ] = particlePositions[ j3     ]
                positions[ vertexpos + 1 ] = particlePositions[ j3 + 1 ]
                positions[ vertexpos + 2 ] = particlePositions[ j3 + 2 ]
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

    profiler.stop()

    render()

def render():
    global group, scene, camera
    time = datetime.now().timestamp()

    group.rotation.y = time * 0.1
    renderer.render( scene, camera )


def onWindowResize(event):
    global camera, controls, scene, renderer, cross, container
    height = event.height
    width = event.width

    camera.aspect = width / height
    camera.updateProjectionMatrix()

    renderer.setSize( width, height )


def keyboard(c, x=0, y=0):
    """keyboard callback."""

    if c == b'q':
        sys.exit(0)


"""
"""


def main(argv=None):
    global container

    init()
    return container.loop()


if __name__ == "__main__":
    sys.exit(main())
