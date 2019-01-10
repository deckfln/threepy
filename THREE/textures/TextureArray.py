"""

"""

from THREE.textures.Texture import *
from THREE.Constants import *
from PIL import Image


class TextureArray(Texture):
    isTextureArrayTexture = True

    def __init__(self, image, width: int, height: int, layerCount: int, mipmaps: int = 1,
                 format=RGBAFormat,
                 gltype=UnsignedByteType,
                 mapping=None,
                 wrapS=ClampToEdgeWrapping, wrapT=ClampToEdgeWrapping,
                 magFilter=LinearFilter, minFilter=LinearMipMapLinearFilter,
                 anisotropy=1,
                 encoding=LinearEncoding):
        super().__init__(image, mapping, wrapS, wrapT, magFilter, minFilter, format, gltype, anisotropy, encoding)

        self.set_class(isTextureArray)
        self.width = width
        self.height = height
        self.layerCount = layerCount
        self.mipmaps = mipmaps
        self.images = None
        self._versions = None

        if not isinstance(image, list):
            # rearrange bytes in memory. For a Texture Array images need to be contiguous in memory
            if self.img_data is None:
                self.get_data()

            temp = self.img_data.copy()
            t = 0
            tiles = int(math.sqrt(layerCount))
            size = int(self.width)
            xsize = size * 3
            ysize = tiles * xsize * size
            for ytile in range(tiles):
                p1 = ytile * ysize
                for xtile in range(tiles):
                    p2 = p1 + xtile * xsize
                    # for one tile
                    for ty in range(size):
                        p = p2 + ty * size * tiles * 3
                        for tx in range(size):
                            temp[t] = self.img_data[p]
                            temp[t + 1] = self.img_data[p + 1]
                            temp[t + 2] = self.img_data[p + 2]
                            t += 3
                            p += 3

            self.img_data = temp
        else:
            self.img_data = [None for i in range(len(image))]
            for i in range(len(image)):
                img = image[i]
                if img is not None:
                    img_data = np.fromstring(img.tobytes(), np.uint8)
                    self.img_data[i] = img_data

            self.images = image
            self._versions = np.full(len(image), -1, np.int32)

    @staticmethod
    def fromTexture(source: Texture, layerCount: int, mipmaps: int):
        nb = math.log2(layerCount)
        (width, height) = source.image.size
        size = int(width/nb)
        texArray = TextureArray(source.image, size, size, layerCount, mipmaps, source.format, source.type)
        texArray.needsUpdate = True
        return texArray

    def updateData(self, i: int, img_data: np.ndarray):
        self.img_data[i] = img_data
        self._versions[i] += 1
        self.needsUpdate = True

    def updateImage(self, i: int, image: Image):
        self.image[i] = image
        self.img_data[i] = np.fromstring(image.tobytes(), np.uint8)
        self._versions[i] += 1
        self.needsUpdate = True
