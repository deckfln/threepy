"""
        <title>three.js webgl - buffergeometry - lines drawcalls</title>
"""
import random
from datetime import datetime
from THREE import *
from THREE.pyOpenGL.pyOpenGL import *
from numba import jit,prange


WIDTH = 640
HEIGHT = 480


class EffectController:
    def __init__(self):
        self.showDots = True
        self.showLines = True
        self.minDistance = 127
        self.limitConnections = False
        self.maxConnections = 20
        self.particleCount = 500


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.mesh = None
        self.geometry = None

        self.container = None
        self.group = None
        self.particlesData = []
        self.positions = None
        self.colors = None
        self.particles = None
        self.particlePositions = None
        self.linesMesh = None

        self.maxParticleCount = 1000
        self.particleCount = 400
        self.r = 1024
        self.rHalf = self.r / 2

        self.pointCloud = None
        self.effectController = EffectController()


class ParticleData:
    def __init__(self, velocity, numConnections):
        self.velocity = velocity
        self.numConnections = numConnections


def init(params):
    maxParticleCount = params.maxParticleCount
    particleCount = params.particleCount
    r = params.r
    rHalf = params.rHalf

    container = pyOpenGL(params)
    container.addEventListener( 'resize', onWindowResize, False )
    container.addEventListener( 'animationRequest', animate )

    renderer = pyOpenGLRenderer({ 'antialias': False })
    size = renderer.getSize()

    camera = THREE.PerspectiveCamera( 45, size['width'] / size['height'], 1, 4000 )

    camera.position.z = 1950

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

    particlesData = []

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
    params.camera = camera
    params.scene = scene
    params.renderer = renderer
    params.geometry = geometry

    params.container = container
    params.group = group
    params.particlesData = particlesData
    params.positions = positions
    params.colors = colors
    params.particles = particles
    params.particlePositions = particlePositions
    params.linesMesh = linesMesh
    params.pointCloud = pointCloud

    params.rHalf = params.r / 2


def animate(params):
    camera = params.camera
    scene = params.scene
    renderer = params.renderer
    geometry = params.geometry

    container = params.container
    group = params.group
    particlesData = params.particlesData
    positions = params.positions
    colors = params.colors
    particles = params.particles
    particlePositions = params.particlePositions
    linesMesh = params.linesMesh
    particleCount = params.particleCount
    pointCloud = params.pointCloud
    effectController = params.effectController

    rHalf = params.rHalf

    vertexpos = 0
    colorpos = 0
    numConnected = 0

    for particleData in particlesData:
        particleData.numConnections = 0

    # octree 16x16x16 x,y,z
    octree = [[[[] for k in range(16)] for j in range(16)] for i in range(16)]

    profiler.start("animate1")

    for i in range(particleCount):
        # // get the particle
        particleData = particlesData[i]

        p = i*3
        x = particlePositions[ p ]
        y = particlePositions[ p + 1 ]
        z = particlePositions[ p + 2 ]

        x += particleData.velocity.x
        y += particleData.velocity.y
        z += particleData.velocity.z

        if not -rHalf <= x <= rHalf:
            particleData.velocity.x = -particleData.velocity.x
            x += particleData.velocity.x

        if not -rHalf <= y <= rHalf:
            particleData.velocity.y = -particleData.velocity.y
            y += particleData.velocity.y

        if not -rHalf <= z <= rHalf:
            particleData.velocity.z = -particleData.velocity.z
            z += particleData.velocity.z

        if effectController.limitConnections and particleData.numConnections >= effectController.maxConnections:
            continue

        # store the particle in the octree
        ox = int((x + rHalf) / 256)
        if ox < 0:
            ox = 0
        elif ox > 3:
            ox = 3
        oy = int((y + rHalf) / 256)
        if oy < 0:
            oy = 0
        elif oy >3:
            oy = 3
        oz = int((z + rHalf) / 256)
        if oz < 0:
            oz = 0
        elif oz > 3:
            oz = 3

        octree[ox][oy][oz].append(i)

        particlePositions[ p ] = x
        particlePositions[ p + 1 ] = y
        particlePositions[ p + 2 ]  = z

    # // Check collision
    # use the octree to find the nearest points
    for i in range(particleCount):
        # // get the particle
        particleData = particlesData[i]
        i3 = i*3
        x = particlePositions[ i3 ]
        y = particlePositions[ i3 + 1 ]
        z = particlePositions[ i3 + 2 ]

        # get the particle in the octree
        ox = int((x + rHalf) / 256)
        oy = int((y + rHalf) / 256)
        oz = int((z + rHalf) / 256)

        for px in range(ox-1, ox+1):
            for py in range(oy-1, oy+1):
                for pz in range(oz-1, oz+1):
                    if not (0 <= px <= 3 and 0 <= py <= 3 and 0 <= pz <= 3):
                        continue

                    points = octree[px][py][pz]

                    for j in points:
                        if i == j:
                            continue

                        particleDataB = particlesData[ j ]
                        if effectController.limitConnections and particleDataB.numConnections >= effectController.maxConnections:
                            continue

                        j3 = j * 3
                        dx = particlePositions[ i3     ] - particlePositions[ j3     ]
                        dy = particlePositions[ i3 + 1 ] - particlePositions[ j3 + 1 ]
                        dz = particlePositions[ i3 + 2 ] - particlePositions[ j3 + 2 ]
                        dist = math.sqrt(dx * dx + dy * dy + dz * dz)

                        if dist < effectController.minDistance:
                            particleData.numConnections += 1
                            particleDataB.numConnections += 1

                            alpha = 1.0 - dist / 150

                            positions[ vertexpos ] = particlePositions[ i3     ]
                            positions[ vertexpos + 1 ] = particlePositions[ i3 + 1 ]
                            positions[ vertexpos + 2 ] = particlePositions[ i3 + 2 ]
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

    profiler.stop("animate1")

    linesMesh.geometry.setDrawRange( 0, numConnected * 2 )
    linesMesh.geometry.attributes.position.needsUpdate = True
    linesMesh.geometry.attributes.color.needsUpdate = True

    pointCloud.geometry.attributes.position.needsUpdate = True

    render(params)

def render(params):
    time = datetime.now().timestamp()

    params.group.rotation.y = time * 0.1
    params.renderer.render( params.scene, params.camera )


def onWindowResize(event, params):
    height = event.height
    width = event.width

    params.camera.aspect = width / height
    params.camera.updateProjectionMatrix()

    params.renderer.setSize( width, height )


def main(argv=None):
    global container

    params = Params()

    init(params)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
