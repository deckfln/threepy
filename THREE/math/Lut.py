"""
/**
 * @author daron1337 / http://daron1337.github.io/
 */
"""
from THREE.Color import *
from THREE.Vector3 import *
from THREE.PlaneBufferGeometry import *
from THREE.MeshBasicMaterial import *

import numpy
from PIL import Image, ImageDraw, ImageFont


class _Labels:
    def __init__(self):
        self.fontsize = 24
        self.fontface = 'Arial'
        self.title = ''
        self.um = ''
        self.ticks = 0
        self.decimal = 2
        self.notation = 'standard'


class _Legend:
    def __init__(self):
        self.layout = 'vertical'
        self.position = Vector3(21.5, 8, 5)
        self.dimensions = {'width': 0.5, 'height': 3}
        self.canvas = None
        self.texture = None
        self.legendGeometry = None
        self.legendMaterial = None
        self.mesh = None
        self.labels = _Labels()


class Lut:
    ColorMapKeywords = {

        "rainbow":    [ [ 0.0, '0x0000FF' ], [ 0.2, '0x00FFFF' ], [ 0.5, '0x00FF00' ], [ 0.8, '0xFFFF00' ],  [ 1.0, '0xFF0000' ] ],
        "cooltowarm": [ [ 0.0, '0x3C4EC2' ], [ 0.2, '0x9BBCFF' ], [ 0.5, '0xDCDCDC' ], [ 0.8, '0xF6A385' ],  [ 1.0, '0xB40426' ] ],
        "blackbody" : [ [ 0.0, '0x000000' ], [ 0.2, '0x780000' ], [ 0.5, '0xE63200' ], [ 0.8, '0xFFFF00' ],  [ 1.0, '0xFFFFFF' ] ],
        "grayscale" : [ [ 0.0, '0x000000' ], [ 0.2, '0x404040' ], [ 0.5, '0x7F7F80' ], [ 0.8, '0xBFBFBF' ],  [ 1.0, '0xFFFFFF' ] ]

    }
    
    def __init__(self, colormap, numberofcolors):
        self.lut = []
        self.map = self.ColorMapKeywords[ colormap ]
        self.n = numberofcolors
        self.mapname = colormap
        self.mapname = 'rainbow'
        self.n = 256
        self.minV = 0
        self.maxV = 1
        self.legend = None

        step = 1.0 / self.n

        i = 0
        while i <= 1:
            for j in range(len(self.map) - 1):
                if self.map[ j ][ 0 ] <= i < self.map[ j + 1 ][ 0 ]:
                    min = self.map[ j ][ 0 ]
                    max = self.map[ j + 1 ][ 0 ]

                    minColor = Color(0xffffff).setHex(self.map[ j ][ 1 ])
                    maxColor = Color(0xffffff).setHex(self.map[ j + 1 ][ 1 ])

                    color = minColor.lerp(maxColor, (i - min) / (max - min))

                    self.lut.append(color)
            i += step
        self.set(self)

    def set(self, value):
        if isinstance(value, Lut):
            self.copy(value)

        return self

    def setMin(self, min):
        self.minV = min
        return self

    def setMax(self, max):
        self.maxV = max
        return self

    def changeNumberOfColors(self, numberofcolors):
        self.n = numberofcolors
        return Lut(self.mapname, self.n)

    def changeColorMap(self, colormap):
        self.mapname = colormap
        return Lut(self.mapname, self.n)

    def copy(self, lut):
        self.lut = lut.lut
        self.mapname = lut.mapname
        self.map = lut.map
        self.n = lut.n
        self.minV = lut.minV
        self.maxV = lut.maxV

        return self

    def getColor(self, alpha):
        if alpha <= self.minV:
            alpha = self.minV
        elif alpha >= self.maxV:
            alpha = self.maxV

        alpha = (alpha - self.minV) / (self.maxV - self.minV)

        colorPosition = round (alpha * self.n)
        colorPosition -= 1 if self.n else colorPosition

        return self.lut[ int(colorPosition) ]

    def addColorMap(self, colormapName, arrayOfColors):
        self.ColorMapKeywords[ colormapName ] = arrayOfColors

    def setLegendOn(self, parameters=None):
        if parameters is None:
            parameters = {}

        self.legend = _Legend()
        self.legend.layout = parameters[ 'layout' ] if 'layout' in parameters else 'vertical'

        self.legend.position = parameters[ 'position' ] if 'position' in parameters else Vector3(21.5, 8, 5)

        self.legend.dimensions = parameters[ 'dimensions' ] if 'dimensions' in parameters else { 'width': 0.5, 'height': 3 }

        self.legend.ctx = Image.new("RGBA", (1, self.n))

        self.legend.texture = THREE.Texture(self.legend.ctx)
        data = self.legend.ctx.load()

        self.map = self.ColorMapKeywords[ self.mapname ]

        k = 0

        step = 1.0 / self.n

        i = 1
        while i >= 0:
            for j in range(len(self.map) - 1, -1, -1):
                if self.map[ j - 1 ][ 0 ] <= i < self.map[ j ][ 0 ]:
                    min = self.map[ j - 1 ][ 0 ]
                    max = self.map[ j ][ 0 ]

                    minColor = Color(0xffffff).setHex(self.map[ j - 1 ][ 1 ])
                    maxColor = Color(0xffffff).setHex(self.map[ j ][ 1 ])

                    color = minColor.lerp(maxColor, (i - min) / (max - min))

                    data[0, self.n - k - 1] = (round(color.r * 255), round(color.g * 255), round(color.b * 255), 255)

                    k += 1
            i -= step

        self.legend.texture.needsUpdate = True

        self.legend.legendGeometry = PlaneBufferGeometry(self.legend.dimensions['width'], self.legend.dimensions['height'])
        self.legend.legendMaterial = MeshBasicMaterial({'map': self.legend.texture, 'side': THREE.DoubleSide})

        self.legend.mesh = THREE.Mesh(self.legend.legendGeometry, self.legend.legendMaterial)

        if self.legend.layout == 'horizontal':
            self.legend.mesh.rotation.z = - 90 * (math.pi / 180)

        self.legend.mesh.position.copy(self.legend.position)

        return self.legend.mesh

    def setLegendOff(self):
        self.legend = None

        return self.legend

    def setLegendLayout(self, layout):
        if not self.legend:
            return False

        if self.legend.layout == layout:
            return False

        if layout != 'horizontal' and layout != 'vertical':
            return False

        self.layout = layout

        if layout == 'horizontal':
            self.legend.mesh.rotation.z = 90 * (math.pi / 180)

        if layout == 'vertical':
            self.legend.mesh.rotation.z = - 90 * (math.pi / 180)

        return self.legend.mesh

    def setLegendPosition(self, position):
        self.legend.position = THREE.Vector3(position.x, position.y, position.z)
        return self.legend

    def setLegendLabels(self, parameters=None, callback=None):
        if not self.legend:
            return False

        if parameters is None:
            parameters = {}

        self.legend.labels.fontsize = parameters[ 'fontsize' ] if 'fontsize'in parameters else 24
        self.legend.labels.fontface = parameters[ 'fontface' ]if 'fontface' in parameters else 'Arial'
        self.legend.labels.title = parameters[ 'title' ] if 'title' in parameters else ''
        self.legend.labels.um = ' [ ' + parameters[ 'um' ] + ' ]' if 'um' in parameters else ''
        self.legend.labels.ticks = parameters[ 'ticks' ] if 'ticks' in parameters else 0
        self.legend.labels.decimal = parameters[ 'decimal' ] if 'decimal' in parameters else 2
        self.legend.labels.notation = parameters[ 'notation' ] if 'notation' in parameters else 'standard'

        backgroundColor = (255, 100, 100, 200)
        borderColor = {'r': 255, 'g': 0, 'b': 0, 'a': 1.0}
        borderThickness = 4

        image = Image.new("RGBA", (150, 300))
        fnt = ImageFont.truetype('arial.ttf', self.legend.labels.fontsize)
        d = ImageDraw.Draw(image)
        d.text((borderThickness, self.legend.labels.fontsize + borderThickness ),
               "%s %s" % (self.legend.labels.title, self.legend.labels.um),
               font=fnt,
               fill=backgroundColor)
        del d
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        txtTitle = THREE.CanvasTexture(image)
        txtTitle.minFilter = THREE.LinearFilter

        spriteMaterialTitle = THREE.SpriteMaterial({'map': txtTitle})

        spriteTitle = THREE.Sprite(spriteMaterialTitle)

        spriteTitle.scale.set(2, 1, 1.0)

        if self.legend.layout == 'vertical':
            spriteTitle.position.set(self.legend.position.x + self.legend.dimensions['width'], self.legend.position.y + (self.legend.dimensions['height'] * 0.45), self.legend.position.z)

        if self.legend.layout == 'horizontal':
            spriteTitle.position.set(self.legend.position.x * 1.015, self.legend.position.y + (self.legend.dimensions['height'] * 0.03), self.legend.position.z)

        if self.legend.labels.ticks > 0:
            ticks = {}
            lines = {}

            if self.legend.layout == 'vertical':
                topPositionY = self.legend.position.y + (self.legend.dimensions['height'] * 0.36)
                bottomPositionY = self.legend.position.y - (self.legend.dimensions['height'] * 0.61)

            if self.legend.layout == 'horizontal':
                topPositionX = self.legend.position.x + (self.legend.dimensions['height'] * 0.75)
                bottomPositionX = self.legend.position.x - (self.legend.dimensions['width'] * 1.2 )

            for i in range(self.legend.labels.ticks):
                value = (self.maxV - self.minV) / (self.legend.labels.ticks - 1 ) * i + self.minV

                if callback:
                    value = callback (value)
                else:
                    if self.legend.labels.notation == 'scientific':
                        value = value.toExponential(self.legend.labels.decimal)
                    else:
                        value = value  # // TODO .toFixed(self.legend.labels.decimal)

                imageTick = Image.new("RGBA", (150, 300))
                d = ImageDraw.Draw(imageTick)
                # d.rectangle((0,0,150,300), (128,128,128,255))
                d.text((borderThickness, self.legend.labels.fontsize + borderThickness),
                       str(value),
                       font=fnt,
                       fill=(0, 0, 0, 255))
                del d
                imageTick = imageTick.transpose(Image.FLIP_TOP_BOTTOM)
                txtTick = THREE.CanvasTexture(imageTick)
                txtTick.minFilter = THREE.LinearFilter

                spriteMaterialTick = THREE.SpriteMaterial({'map': txtTick})

                spriteTick = THREE.Sprite(spriteMaterialTick)

                spriteTick.scale.set(2, 1, 1.0)

                if self.legend.layout == 'vertical':
                    position = bottomPositionY + (topPositionY - bottomPositionY) * ((value - self.minV) / (self.maxV - self.minV))
                    spriteTick.position.set(self.legend.position.x + (self.legend.dimensions['width'] * 2.7), position, self.legend.position.z)

                if self.legend.layout == 'horizontal':
                    position = bottomPositionX + (topPositionX - bottomPositionX) * ((value - self.minV) / (self.maxV - self.minV))

                    if self.legend.labels.ticks > 5:
                        if (i % 2) == 0:
                            offset = 1.7
                        else:
                            offset = 2.1
                    else:
                        offset = 1.7

                    spriteTick.position.set(position, self.legend.position.y - self.legend.dimensions['width'] * offset, self.legend.position.z)

                material = THREE.LineBasicMaterial({ 'color': 0x000000, 'linewidth': 2 })

                geometry = THREE.Geometry()

                if self.legend.layout == 'vertical':
                    linePosition = (self.legend.position.y - (self.legend.dimensions['height'] * 0.5) + 0.01) + (self.legend.dimensions['height']) * ((value - self.minV) / (self.maxV - self.minV) * 0.99)
                    geometry.vertices.append(THREE.Vector3(self.legend.position.x + self.legend.dimensions['width'] * 0.55, linePosition, self.legend.position.z ))
                    geometry.vertices.append(THREE.Vector3(self.legend.position.x + self.legend.dimensions['width'] * 0.7, linePosition, self.legend.position.z ))

                if self.legend.layout == 'horizontal':
                    linePosition = (self.legend.position.x - (self.legend.dimensions['height'] * 0.5) + 0.01) + (self.legend.dimensions['height']) * ((value - self.minV) / (self.maxV - self.minV) * 0.99)
                    geometry.vertices.append(THREE.Vector3(linePosition, self.legend.position.y - self.legend.dimensions['width'] * 0.55, self.legend.position.z ))
                    geometry.vertices.append(THREE.Vector3(linePosition, self.legend.position.y - self.legend.dimensions['width'] * 0.7, self.legend.position.z ))

                line = THREE.Line(geometry, material)

                lines[ i ] = line
                ticks[ i ] = spriteTick

        return { 'title': spriteTitle,  'ticks': ticks, 'lines': lines }
