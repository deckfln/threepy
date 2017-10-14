"""
        <title>three.js webgl - geometry - extrude shapes from geodata</title>
"""

"""
# // From d3-threeD.js
/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this file,
 * You can obtain one at http:# //mozilla.org/MPL/2.0/. */
"""
from THREE import *
from THREE.pyOpenGL.pyOpenGL import *


class d3threeD():
    DEGS_TO_RADS = math.pi / 180
    UNIT_SIZE = 100

    DIGIT_0 = 48
    DIGIT_9 = 57
    COMMA = 44
    SPACE = 32
    PERIOD = 46
    MINUS = 45

    def __init__(self):
        self.name="d3threeD"

    def transformSVGPath(self, pathStr):
        path = THREE.ShapePath()

        idx = 1
        l = len(pathStr)
        x = 0
        y = 0
        nx = 0
        ny = 0
        firstX = None
        firstY = None
        x1 = 0
        x2 = 0
        y1 = 0
        y2 = 0
        rx = 0
        ry = 0
        xar = 0
        laf = 0
        sf = 0

        def eatNum():
            nonlocal idx

            isFloat = False
            # // eat delims
            while idx < l:
                c = pathStr[idx]
                if c != ',' and c != ' ':
                    break
                idx += 1

            if c == '-':
                sidx = idx
                idx += 1 
            else:
                sidx = idx
                
            # // eat number
            while idx < l:
                c = pathStr[idx]
                if '0' <= c <= '9':
                    idx += 1
                    continue
                elif c == '.':
                    idx += 1
                    isFloat = True
                    continue

                s = pathStr[sidx:idx]
                return float(s) if isFloat else int(s)

            s = pathStr[sidx:]
            return float(s) if isFloat else int(s)

        def nextIsNum():
            nonlocal idx

            # // do permanently eat any delims...
            while idx < l:
                c = pathStr[idx]
                if c != "." and c != ' ':
                    break
                idx += 1
                
            c = pathStr[idx]
            return c == '-' or ('0' <= c <= '9')

        activeCmd = pathStr[0]
        while idx <= l:
            canRepeat = True
            
            # // moveto commands, become lineto's if repeated
            if activeCmd == 'M':
                x = eatNum()
                y = eatNum()
                path.moveTo(x, y)
                activeCmd = 'L'
                firstX = x
                firstY = y
            elif activeCmd == 'm':
                x += eatNum()
                y += eatNum()
                path.moveTo(x, y)
                activeCmd = 'l'
                firstX = x
                firstY = y
            elif activeCmd == 'Z' or activeCmd == 'z':
                canRepeat = False
                if x != firstX or y != firstY:
                    path.lineTo(firstX, firstY)
            elif activeCmd == 'L' or  activeCmd == 'H' or  activeCmd =='V':
                # // - lines!
                nx = x if (activeCmd == 'V') else eatNum()
                ny = y if (activeCmd == 'H') else eatNum()
                path.lineTo(nx, ny)
                x = nx
                y = ny
            elif activeCmd == 'l' or  activeCmd == 'h' or  activeCmd == 'v':
                nx = x if (activeCmd == 'v') else (x + eatNum())
                ny = y if (activeCmd == 'h') else (y + eatNum())
                path.lineTo(nx, ny)
                x = nx
                y = ny
            elif activeCmd == 'C' or activeCmd == 'S':
                if activeCmd == 'C':
                    # // - cubic bezier
                    x1 = eatNum(); y1 = eatNum()
                elif activeCmd == 'S':
                    x1 = 2 * x - x2; y1 = 2 * y - y2
                x2 = eatNum()
                y2 = eatNum()
                nx = eatNum()
                ny = eatNum()
                path.bezierCurveTo(x1, y1, x2, y2, nx, ny)
                x = nx; y = ny
            elif activeCmd == 'c' or activeCmd == 's':
                if activeCmd == 's':
                    x1 = x + eatNum()
                    y1 = y + eatNum()
                elif activeCmd == 's':
                    x1 = 2 * x - x2
                    y1 = 2 * y - y2
                x2 = x + eatNum()
                y2 = y + eatNum()
                nx = x + eatNum()
                ny = y + eatNum()
                path.bezierCurveTo(x1, y1, x2, y2, nx, ny)
                x = nx; y = ny
            elif activeCmd == 'Q' or activeCmd == 'T':                
                # // - quadratic bezier
                if activeCmd == 'Q':
                    x1 = eatNum(); y1 = eatNum()
                elif activeCmd == 'T':
                    x1 = 2 * x - x1
                    y1 = 2 * y - y1
                nx = eatNum()
                ny = eatNum()
                path.quadraticCurveTo(x1, y1, nx, ny)
                x = nx
                y = ny
            elif activeCmd == 'q' or activeCmd == 't':
                if activeCmd == 'q':
                    x1 = x + eatNum()
                    y1 = y + eatNum()
                elif activeCmd == 't':
                    x1 = 2 * x - x1
                    y1 = 2 * y - y1
                nx = x + eatNum()
                ny = y + eatNum()
                path.quadraticCurveTo(x1, y1, nx, ny)
                x = nx; y = ny
            elif activeCmd == 'A':
                # // - elliptical arc
                rx = eatNum()
                ry = eatNum()
                xar = eatNum() * DEGS_TO_RADS
                laf = eatNum()
                sf = eatNum()
                nx = eatNum()
                ny = eatNum()
                if rx != ry:
                    print ("Forcing elliptical arc to be a circular one :%d, %d" % (rx, ry))
                # // SVG implementation notes does all the math for us! woo!
                # // http:# //www.w3.org/TR/SVG/implnote.html#ArcImplementationNotes
                # // step1, using x1 as x1'
                x1 = math.cos(xar) * (x - nx) / 2 + math.sin(xar) * (y - ny) / 2
                y1 = -math.sin(xar) * (x - nx) / 2 + math.cos(xar) * (y - ny) / 2
                # // step 2, using x2 as cx'
                norm = math.sqrt(
                     (rx*rx * ry*ry - rx*rx * y1*y1 - ry*ry * x1*x1) /
                     (rx*rx * y1*y1 + ry*ry * x1*x1))
                if laf == sf:
                    norm = -norm
                x2 = norm * rx * y1 / ry
                y2 = norm * -ry * x1 / rx
                # // step 3
                cx = math.cos(xar) * x2 - math.sin(xar) * y2 + (x + nx) / 2
                cy = math.sin(xar) * x2 + math.cos(xar) * y2 + (y + ny) / 2

                u = THREE.Vector2(1, 0)
                v = THREE.Vector2((x1 - x2) / rx, (y1 - y2) / ry)
                startAng = math.acos(u.dot(v) / u.length() / v.length())
                if u.x * v.y - u.y * v.x < 0:
                    startAng = -startAng

                # // we can reuse 'v' from start angle as our 'u' for delta angle
                u.x = (-x1 - x2) / rx
                u.y = (-y1 - y2) / ry

                deltaAng = math.acos(v.dot(u) / v.length() / u.length())
                # // This normalization ends up making our curves fail to triangulate...
                if v.x * u.y - v.y * u.x < 0:
                    deltaAng = -deltaAng
                if not sf and deltaAng > 0:
                    deltaAng -= math.pi * 2
                if sf and deltaAng < 0:
                    deltaAng += math.pi * 2

                path.absarc(cx, cy, rx, startAng, startAng + deltaAng, sf)
                x = nx
                y = ny
            else:
                raise RuntimeError("weird path command: " + activeCmd)

            # // just reissue the command
            if canRepeat and nextIsNum():
                continue

            if idx < l:
                activeCmd = pathStr[idx]
            idx += 1

        return path


d3g = d3threeD()


# /// Part from g0v/twgeojson
# /// Graphic Engine and Geo Data Init Functions

def addGeoObject( group, svgObject ):
    results = []
    thePaths = svgObject['paths']
    theAmounts = svgObject['amounts']
    theColors = svgObject['colors']
    theCenter = svgObject['center']

    l = len(thePaths)
    for i in range(l):
        path = d3g.transformSVGPath( thePaths[i] )
        color = THREE.Color( theColors[i] )
        material = THREE.MeshLambertMaterial({
            'color': color,
            'emissive': color
        })
        amount = theAmounts[i]
        simpleShapes = path.toShapes(True)
        len1 = len(simpleShapes)
        for j in range(len1):
            simpleShape = simpleShapes[j]
            shape3d = ExtrudeGeometry (simpleShape, {
                'amount': amount,
                'bevelEnabled': False
            })
            mesh = THREE.Mesh(shape3d, material)
            mesh.rotation.x = math.pi
            mesh.translateZ( - amount - 1)
            mesh.translateX( - theCenter['x'])
            mesh.translateY( - theCenter['y'])
            group.add(mesh)

# // Main

class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.container = None
        self.mesh = None
        self.controls = None
        self.group = None
        self.targetRotation = 0
        self.targetRotationOnMouseDown = 0
        self.mouseX = 0
        self.mouseXOnMouseDown = 0
        self.windowHalfX = window.innerWidth / 2
        self.windowHalfY = window.innerHeight / 2


# //

def init(p):
    # /// Global : renderer
    p.container = pyOpenGL(p)
    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize( window.innerWidth, window.innerHeight )

    # /// Global : scene
    p.scene = THREE.Scene()
    p.scene.background = THREE.Color( 0xb0b0b0 )

    # /// Global : camera
    p.camera = THREE.PerspectiveCamera( 50, window.innerWidth / window.innerHeight, 1, 1000 )
    p.camera.position.set( 0, 0, 200 )

    # /// Global : group
    p.group = THREE.Group()
    p.scene.add( p.group )

    # /// direct light
    light = THREE.DirectionalLight( 0x404040 )
    light.position.set( 0.75, 0.75, 1.0 ).normalize()
    p.scene.add( light )

    # /// ambient light
    ambientLight = THREE.AmbientLight(0x404040)
    p.scene.add( ambientLight )

    # /// backgroup grids
    helper = THREE.GridHelper( 160, 10 )
    helper.rotation.x = math.pi / 2
    p.group.add( helper )

    obj = initSVGObject()

    addGeoObject( p.group, obj )

    p.container.addEventListener( 'mousedown', onDocumentMouseDown, False )
    p.container.addEventListener( 'touchstart', onDocumentTouchStart, False )
    p.container.addEventListener( 'touchmove', onDocumentTouchMove, False )
    p.container.addEventListener( 'resize', onWindowResize, False )


def initSVGObject():
    obj = {}

    # /// The geo data from Taipei City, Keelung City, Taipei County in SVG form
    obj['paths'] = [
        # /// Taipei City
        "M366.2182,108.9780 L368.0329,110.3682 L367.5922,112.4411 L369.9258,116.0311 L368.9827,117.3543 " +
        "L371.5686,119.8491 L370.5599,121.7206 L372.9314,124.8009 L368.8889,126.7603 L369.2695,130.7622 " +
        "L366.1499,130.3388 L363.4698,128.1161 L362.9256,125.6018 L360.8153,126.4025 L360.2968,124.3588 " +
        "L361.9519,121.1623 L360.4475,118.7162 L358.1163,117.8678 L358.7094,115.7577 L361.6243,112.4576 Z",
        # /// Keelung City
        "M380.2689,113.3850 L383.5604,114.2370 L383.7404,114.2386 L385.4082,115.6247 L384.9725,117.4631 " +
        "L381.6681,117.9439 L383.0209,121.0914 L379.4649,122.7061 L373.4987,118.8487 L372.0980,114.7589 " +
        "L377.9716,112.0707 Z",
        # /// Taipei County
        "M359.4486,155.6690 L357.0422,152.7420 L355.1688,148.0173 L357.1186,145.8045 L354.1323,141.2242 " +
        "L351.1807,141.6609 L348.9387,140.5372 L349.5415,137.8396 L347.5174,136.1694 L347.6299,129.2327 " +
        "L351.4192,128.8067 L354.2518,125.3113 L352.5805,121.8038 L349.3190,120.9429 L344.3277,116.7676 " +
        "L350.9772,115.1221 L354.5759,112.5371 L354.5667,110.6949 L357.4098,105.7489 L362.3963,101.8443 " +
        "L364.4415,101.0819 L364.5314,101.0828 L364.6209,101.1230 L364.7698,101.2029 L368.1221,101.5115 " +
        "L371.7216,104.1338 L372.2958,106.7261 L375.5949,109.6971 L377.0415,108.8875 L377.0737,108.6526 " +
        "L377.4037,108.6165 L376.8840,109.7091 L376.7323,109.9037 L377.9416,112.0705 L371.7970,114.8736 " +
        "L374.0935,119.4031 L380.7848,122.7963 L382.6529,121.9897 L381.5792,117.8256 L385.0339,117.3069 " +
        "L385.4082,115.6247 L388.7014,116.3969 L389.8697,116.6024 L390.0206,116.4860 L391.0396,116.6118 " +
        "L394.6665,116.9929 L394.4694,119.2255 L394.3172,119.4987 L395.3792,121.8977 L395.2728,124.0526 " +
        "L397.2123,125.6350 L401.1709,126.2516 L401.2612,126.2130 L401.4086,126.6060 L400.1992,127.7733 " +
        "L399.7769,128.0446 L399.6247,128.3179 L398.1779,129.0521 L394.2418,129.2969 L388.7324,130.9385 " +
        "L389.2782,134.0003 L383.7237,137.0111 L381.7445,139.9336 L379.7001,139.9546 L376.1539,143.0580 " +
        "L371.3022,144.1094 L368.6009,146.5914 L368.7361,151.1399 L363.6153,154.4980 " +
        # /// Taipei County hole.
        "M363.4600,128.3904 L366.6300,130.3829 L369.3732,129.3913 L369.5603,125.6695 L374.3989,125.1677 " +
        "L370.8412,123.6440 L371.0684,118.8252 L369.0431,117.3157 L369.6882,115.7936 L367.8578,112.8749 " +
        "L368.1217,110.4867 L366.5152,109.2554 L361.9554,112.3435 L358.1163,117.8678 L361.7218,120.2192 " +
        "L360.7261,126.3232 L362.8064,125.5221 Z"]

    obj['amounts'] = [ 19, 20, 21 ]
    obj['colors'] =  [ 0xC07000, 0xC08000, 0xC0A000 ]
    obj['center'] = { 'x':365, 'y':125 }

    return obj


# /// Events from extrude shapes example

def onWindowResize(event, p):
    p.windowHalfX = window.innerWidth / 2
    p.windowHalfY = window.innerHeight / 2

    p.camera.aspect = window.innerWidth / window.innerHeight
    p.camera.updateProjectionMatrix()

    p.renderer.setSize( window.innerWidth, window.innerHeight )

    
def onDocumentMouseDown( event, p ):
    event.preventDefault()

    p.container.addEventListener( 'mousemove', onDocumentMouseMove, False )
    p.container.addEventListener( 'mouseup', onDocumentMouseUp, False )
    p.container.addEventListener( 'mouseout', onDocumentMouseOut, False )

    p.mouseXOnMouseDown = event.clientX - p.windowHalfX
    p.targetRotationOnMouseDown = p.targetRotation

    
def onDocumentMouseMove( event, p ):
    p.mouseX = event.clientX - p.windowHalfX

    p.targetRotation = p.targetRotationOnMouseDown + ( p.mouseX - p.mouseXOnMouseDown ) * 0.02


def onDocumentMouseUp( event,p ):
    p.container.removeEventListener( 'mousemove', onDocumentMouseMove, False )
    p.container.removeEventListener( 'mouseup', onDocumentMouseUp, False )
    p.container.removeEventListener( 'mouseout', onDocumentMouseOut, False )


def onDocumentMouseOut( event,p ):
    p.container.removeEventListener( 'mousemove', onDocumentMouseMove, False )
    p.container.removeEventListener( 'mouseup', onDocumentMouseUp, False )
    p.container.removeEventListener( 'mouseout', onDocumentMouseOut, False )


def onDocumentTouchStart( event, p ):
    if event.touches.length == 1:
        event.preventDefault()

        p.mouseXOnMouseDown = event.touches[ 0 ].pageX - p.windowHalfX
        p.targetRotationOnMouseDown = p.targetRotation

        
def onDocumentTouchMove( event, p ):
    if event.touches.length == 1:
        event.preventDefault()

        p.mouseX = event.touches[ 0 ].pageX - p.windowHalfX
        p.targetRotation = p.targetRotationOnMouseDown + ( p.mouseX - p.mouseXOnMouseDown ) * 0.05


def animate(p):
    # /// compatibility : http:# //caniuse.com/requestanimationframe

    render(p)


def render(p):
    p.group.rotation.y += ( p.targetRotation - p.group.rotation.y ) * 0.05
    p.renderer.render( p.scene, p.camera )


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener( 'animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
