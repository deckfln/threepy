"""
/**
 * @author mrdoob / http://mrdoob.com/
 * @author fde
 */
"""
from THREE.loaders.LoadingManager import *
from PIL import Image


class ImageLoader:
    def __init__(self, manager=None ):
        self.manager = manager if manager else DefaultLoadingManager
        self.path = None
        self.target = None

    def load(self, url, onLoad=None, onProgress=None, onError=None):
        global Cache

        if url is None:
            url = ''

        if self.path is not None:
            url = self.path + url

        cached = Cache.get( url )

        if cached:
            return cached

        try:
            image = Image.open(url).transpose(Image.FLIP_TOP_BOTTOM)
        except FileNotFoundError:
            if onError:
                onError("File %s not found" % url)
                return
            else:
                raise RuntimeError('ImageLoader: File %s not found' % url)

        # img_data = numpy.fromstring(image.tobytes(), numpy.uint8)
        # width, height = image.size
        if image.palette:
            image = image.convert('RGBA')

        self.manager.itemEnd(url)

        Cache.add(url, image)

        self.manager.itemStart( url )

        if onLoad:
            onLoad(url, self.target)

        return image

    def setPath(self, value ):
        self.path = value
        return self

    def setTarget(self, target):
        self.target = target