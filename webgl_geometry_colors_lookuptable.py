"""
        <title>three.js webgl - lookup table</title>
        
        <div id="info"><a href="http:# //threejs.org" target="_blank" rel="noopener">three.js</a> webgl - lookuptable - vertex color values from a range of data values.<br />
        press A: change color map, press S: change numberOfColors, press D: toggle Legend on/off, press F: change Legend layout<br />
        </div>
"""
from THREE import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.Javascript import *
from THREE.math.Lut import *


params = javascriptObject({
    'container': None,
    'camera': None,
    'renderer': None,
    'lut': None,
    'legendLayout': None,
    'position': None,
    'mesh': None,
    'colorMap': None,
    'numberOfColors': None,
    'rotWorldMatrix': None
})


def init(params):
    container = pyOpenGL(params)

    # // SCENE
    scene = THREE.Scene()
    scene.background = THREE.Color(0xffffff)

    # // CAMERA
    camera = THREE.PerspectiveCamera(20, window.innerWidth / window.innerHeight, 1, 10000)
    camera.name = 'camera'
    scene.add(camera)

    # // LIGHT
    ambientLight = THREE.AmbientLight(0x444444)
    ambientLight.name = 'ambientLight'
    scene.add(ambientLight)

    colorMap = 'rainbow'
    numberOfColors = 512

    legendLayout = 'vertical'

    camera.position.x = 17
    camera.position.y = 9
    camera.position.z = 32

    directionalLight = THREE.DirectionalLight(0xffffff, 0.7)
    directionalLight.position.x = 17
    directionalLight.position.y = 9
    directionalLight.position.z = 30
    directionalLight.name = 'directionalLight'
    scene.add(directionalLight)

    renderer = THREE.pyOpenGLRenderer({ 'antialias': True })
    renderer.setSize(window.innerWidth, window.innerHeight)

    container.addEventListener('resize', onWindowResize, False)

    container.addEventListener("keydown", onKeyDown, True)

    params.container = container
    params.renderer = renderer
    params.scene = scene
    params.camera = camera
    params.colorMap = colorMap
    params.numberOfColors = numberOfColors
    params.legendLayout = legendLayout

    loadModel(colorMap, numberOfColors, legendLayout)


def rotateAroundWorldAxis(object, axis, radians):
    if not axis:
        return

    rotWorldMatrix = THREE.Matrix4()
    rotWorldMatrix.makeRotationAxis(axis.normalize(), radians)
    rotWorldMatrix.multiply(object.matrix)

    object.matrix = rotWorldMatrix
    object.rotation.setFromRotationMatrix(object.matrix)


def onWindowResize(event, params):
    params.camera.aspect = window.innerWidth / window.innerHeight
    params.camera.updateProjectionMatrix()

    params. renderer.setSize(window.innerWidth, window.innerHeight)


def animate(params):
    render(params)


def render(params):
    rotateAroundWorldAxis(params.mesh, params.position, math.pi / 180)

    params.renderer.render(params.scene, params.camera)


def loadModel (colorMap, numberOfColors, legendLayout):
    loader = THREE.BufferGeometryLoader()

    def _load(geometry):
        global params
        position = params.position
        scene = params.scene

        geometry.computeVertexNormals()
        geometry.normalizeNormals()

        material = THREE.MeshLambertMaterial({
            'side': THREE.DoubleSide,
            'color': 0xF5F5F5,
            'vertexColors': THREE.VertexColors
        })

        lutColors = Float32Array(geometry.attributes.pressure.count * 9)

        lut = Lut(colorMap, numberOfColors)

        lut.setMax(2000)
        lut.setMin(0)

        i3 = 0
        for colorValue  in geometry.attributes.pressure.array:
            color = lut.getColor(colorValue)

            if color is None:
                print("ERROR: " + colorValue)
            else:
                lutColors[ i3     ] = color.r
                lutColors[ i3 + 1 ] = color.g
                lutColors[ i3 + 2 ] = color.b

            i3 += 3

        geometry.addAttribute('color', THREE.BufferAttribute(lutColors, 3))

        params.mesh = THREE.Mesh (geometry, material)

        geometry.computeBoundingBox()
        boundingBox = geometry.boundingBox
        center = boundingBox.getCenter()

        if position is None:
            params.position = THREE.Vector3(center.x, center.y, center.z)

        scene.add (params.mesh)

        if legendLayout:

            if legendLayout == 'horizontal':
                legend = lut.setLegendOn({ 'layout':'horizontal', 'position': { 'x': 21, 'y': 6, 'z': 5 } })
            else:
                legend = lut.setLegendOn()

            scene.add (legend)

            labels = lut.setLegendLabels({ 'title': 'Pressure', 'um': 'Pa', 'ticks': 5 })

            scene.add (labels['title'])

            for i in labels[ 'ticks' ].keys():
                scene.add (labels[ 'ticks' ][ i ])
                scene.add (labels[ 'lines' ][ i ])

    loader.load("models/json/pressure.json", _load)

    
def cleanScene():
    global params
    scene = params.scene

    elementsInTheScene = scene.children.length

    for i in range(elementsInTheScene-1, -1, -1):
        if scene.children [ i ].name != 'camera' and \
             scene.children [ i ].name != 'ambientLight' and \
             scene.children [ i ].name != 'directionalLight':
            scene.remove (scene.children [ i ])


def onKeyDown(e, param):
    numberOfColors = param.numberOfColors
    colorMap = param.colorMap
    legendLayout = param.legendLayout

    maps = [ 'rainbow', 'cooltowarm', 'blackbody', 'grayscale' ]

    colorNumbers = ['16', '128', '256', '512' ]

    if e.keyCode == 65:
        cleanScene()

        index = 0 if maps.index(colorMap) >= len(maps) - 1 else maps.index(colorMap) + 1

        colorMap = maps [ index ]

        loadModel (colorMap, numberOfColors, legendLayout)
    elif e.keyCode == 83:
        cleanScene()

        index = 0 if colorNumbers.index(numberOfColors) >= len(colorNumbers) - 1 else colorNumbers.index(numberOfColors) + 1

        numberOfColors = colorNumbers [ index ]

        loadModel (colorMap ,  numberOfColors, legendLayout)
    elif e.keyCode == 68:
        if not legendLayout:
            cleanScene()

            legendLayout = 'vertical'

            loadModel (colorMap ,  numberOfColors, legendLayout)
        else:
            cleanScene()

            legendLayout = lut.setLegendOff()

            loadModel (colorMap ,  numberOfColors, legendLayout)

    elif e.keyCode == 70:
        cleanScene()

        if not legendLayout:
            return False

        lut.setLegendOff()

        if legendLayout == 'horizontal':
            legendLayout = 'vertical'
        else:
            legendLayout = 'horizontal'

        loadModel (colorMap ,  numberOfColors, legendLayout)


def main(argv=None):
    global container

    init(params)
    params.container.addEventListener('animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
