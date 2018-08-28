"""
 * Loads a Wavefront .mtl file specifying materials
 *
 * @author angelxuanchang
"""

from THREE.materials.MeshPhongMaterial import *


class MaterialCreator:
    """
     * Create a THREE-MTLLoader.MaterialCreator
     * @param baseUrl - Url relative to which textures are loaded
     * @param options - Set of options on how to construct the materials
     *                  side: Which side to apply the material
     *                        THREE.FrontSide (default), THREE.BackSide, THREE.DoubleSide
     *                  wrap: What type of wrapping to apply for textures
     *                        THREE.RepeatWrapping (default), THREE.ClampToEdgeWrapping, THREE.MirroredRepeatWrapping
     *                  normalizeRGB: RGBs need to be normalized to 0-1 from 0-255
     *                                Default: False, assumed to be already normalized
     *                  ignoreZeroRGBs: Ignore values of RGBs (Ka,Kd,Ks) that are all 0's
     *                                  Default: False
     * @constructor
    """
    def __init__(self, baseUrl='', options=None):
        self.baseUrl = baseUrl
        self.options = options
        self.materialsInfo = {}
        self.materials = {}
        self.materialsArray = []
        self.nameLookup = {}

        self.side = self.options.side if (self.options and self.options.side) else THREE.FrontSide
        self.wrap = self.options.wrap if (self.options and self.options.wrap) else THREE.RepeatWrapping
        self.crossOrigin = 'Anonymous'

    def setCrossOrigin(self, value):
        self.crossOrigin = value

    def setManager(self, value):
        self.manager = value

    def setMaterials(self, materialsInfo):
        self.materialsInfo = self.convert(materialsInfo)
        self.materials = {}
        self.materialsArray = []
        self.nameLookup = {}

    def convert(self, materialsInfo):
        if not self.options:
            return materialsInfo

        converted = {}

        for mn in materialsInfo:
            # Convert materials info into normalized form based on options
            mat = materialsInfo[mn]

            covmat = {}

            converted[mn] = covmat

            for prop in mat:
                save = True
                value = mat[prop]
                lprop = prop.lower()

                if lprop == 'kd' or lprop == 'ka' or lprop == 'ks':
                        # Diffuse color (color under white light) using RGB values
                        if self.options and self.options.normalizeRGB:
                            value = [value[0] / 255, value[1] / 255, value[2] / 255]

                        if self.options and self.options.ignoreZeroRGBs:
                            if value[0] == 0 and value[1] == 0 and value[2] == 0:
                                # ignore
                                save = False

                if save:
                    covmat[lprop] = value

        return converted

    def preload(self):
        for mn in self.materialsInfo:
            self.create(mn)

    def getIndex(self, materialName):
        return self.nameLookup[materialName]

    def getAsArray(self):
        index = 0

        for mn in self.materialsInfo:
            self.materialsArray[index] = self.create(mn)
            self.nameLookup[mn] = index
            index += 1

        return self.materialsArray

    def create(self, materialName):
        if materialName not in self.materials:
            self.createMaterial_(materialName)

        return self.materials[materialName]

    def createMaterial_(self, materialName):
        # Create material
        scope = self
        mat = self.materialsInfo[materialName]

        params = {
            'name': materialName,
            'side': self.side
        }

        def resolveURL(baseUrl, url):
            if not isinstance(url, str) or url == '':
                return ''

            # Absolute URL
            # if /^https?:\/\#i.test(url)) return url

            return baseUrl + '/' + url

        def setMapForType(mapType, value):
            if mapType in params:
                return  # Keep the first encountered texture

            texParams = scope.getTextureParams(value, params)
            map = scope.loadTexture(resolveURL(scope.baseUrl, texParams['url']))

            map.repeat.copy(texParams['scale'])
            map.offset.copy(texParams['offset'])

            map.wrapS = scope.wrap
            map.wrapT = scope.wrap

            params[mapType] = map

        for prop in mat:
            value = mat[prop]

            if value == '':
                continue

            p = prop.lower()
            # Ns is material specular exponent

            if p == 'kd':
                # Diffuse color (color under white light) using RGB values

                params['color'] = THREE.Color().fromArray(value)

            elif p == 'ks':
                # Specular color (color when light is reflected from shiny surface) using RGB values
                params['specular'] = THREE.Color().fromArray(value)

            elif p == 'map_kd':
                # Diffuse texture map
                setMapForType("map", value)

            elif p == 'map_ks':
                # Specular map
                setMapForType("specularMap", value)

            elif p == 'norm':
                setMapForType("normalMap", value)

            elif p == 'map_bump' or p == 'bump':
                # Bump texture map
                setMapForType("bumpMap", value)

            elif p == 'ns':
                # The specular exponent (defines the focus of the specular highlight)
                # A high exponent results in a tight, concentrated highlight. Ns values normally range from 0 to 1000.
                params['shininess'] = float(value)

            elif p == 'd':
                n = float(value)
                if n < 1:
                    params['opacity'] = n
                    params['transparent'] = True

            elif p == 'tr':
                n = float(value)
                if n > 0:
                    params['opacity'] = 1 - n
                    params['transparent'] = True

        self.materials[materialName] = THREE.MeshPhongMaterial(params)
        return self.materials[materialName]

    def getTextureParams(self, value, matParams):
        texParams = {
            'scale': THREE.Vector2(1, 1),
            'offset': THREE.Vector2(0, 0)
        }

        items = re.split('\s+', value)
        if '-bm' in items:
            pos = items.index('-bm')
            matParams.bumpScale = float(items[pos + 1])
            del items[pos:pos+2]

        if '-s' in items:
            pos = items.index('-s')
            texParams['scale'].set(float(items[pos + 1]), float(items[pos + 2]))
            del items[pos:pos+4]    # we expect 3 parameters here!

        if '-o' in items:
            pos = items.index('-o')
            texParams['offset'].set(float(items[pos + 1]), float(items[pos + 2]))
            del items[pos:pos+4]    # we expect 3 parameters here!

        texParams['url'] = ' '.join(items).strip()
        return texParams

    def loadTexture(self, url, mapping=None, onLoad=None, onProgress=None, onError=None):
        loader = THREE.Loader.Handlers.get(url)
        manager = self.manager if (self.manager is not None) else THREE.DefaultLoadingManager

        if loader is None:
            loader = THREE.TextureLoader(manager)

        if hasattr(loader, 'setCrossOrigin'):
            loader.setCrossOrigin(self.crossOrigin)
        texture = loader.load(url, onLoad, onProgress, onError)

        if mapping is not None:
            texture.mapping = mapping

        return texture


class MTLLoader:
    def __init__(self, manager=None):
        self.manager = manager if manager is not None else THREE.DefaultLoadingManager
        self.path = ""
        self.texturePath = ""
        self.crossOrigin = True
        self.materialOptions = None
        self.mtl = None

    def load(self, url, onLoad=None, onProgress=None, onError=None):
        """
         * Loads and parses a MTL asset from a URL.
         *
         * @param {String} url - URL to the MTL file.
         * @param {Function} [onLoad] - Callback invoked with the loaded object.
         * @param {Function} [onProgress] - Callback for download progress.
         * @param {Function} [onError] - Callback for download errors.
         *
         * @see setPath setTexturePath
         *
         * @note In order for relative texture references to resolve correctly
         * you must call setPath and/or setTexturePath explicitly prior to load.
        """

        scope = self

        loader = THREE.FileLoader(self.manager)
        loader.setPath(self.path)

        def _onLoad(text):
            scope.mtl = scope.parse(text)
            if onLoad:
                onLoad(scope.parse(text))

        loader.load(url, _onLoad, onProgress, onError)
        return self.mtl

    def setPath(self, path):
        """
         * Set base path for resolving references.
         * If set self path will be prepended to each loaded and found reference.
         *
         * @see setTexturePath
         * @param {String} path
         *
         * @example
         *     mtlLoader.setPath('assets/obj/')
         *     mtlLoader.load('my.mtl', ...)
        """
        self.path = path

    def setTexturePath(self, path):
        """
         * Set base path for resolving texture references.
         * If set self path will be prepended found texture reference.
         * If not set and setPath is, it will be used as texture base path.
         *
         * @see setPath
         * @param {String} path
         *
         * @example
         *     mtlLoader.setPath('assets/obj/')
         *     mtlLoader.setTexturePath('assets/textures/')
         *     mtlLoader.load('my.mtl', ...)
        """
        self.texturePath = path

    def setBaseUrl(self, path):
        print('THREE.MTLLoader: .setBaseUrl() is deprecated. Use .setTexturePath(path) for texture path or .setPath(path) for general base path instead.')
        self.setTexturePath(path)

    def setCrossOrigin(self, value):
        self.crossOrigin = value

    def setMaterialOptions(self, value):
        self.materialOptions = value

    def parse(self, text):
        """
         * Parses a MTL file.
         *
         * @param {String} text - Content of MTL file
         * @return {THREE.MTLLoader.MaterialCreator}
         *
         * @see setPath setTexturePath
         *
         * @note In order for relative texture references to resolve correctly
         * you must call setPath and/or setTexturePath explicitly prior to parse.
        """
        lines = text.split('\n')
        info = {}
        delimiter_pattern = '\s+'
        materialsInfo = {}

        for line in lines:
            line = line.strip()

            if len(line) == 0 or line[0] == '#':
                # Blank line or comment ignore
                continue

            pos = line.find(' ')

            key = line[0:pos] if pos >= 0 else line
            key = key.lower()

            value = line[pos + 1:] if pos >= 0 else ''
            value = value.strip()

            if key == 'newmtl':
                # New material
                info = {'name': value}
                materialsInfo[value] = info

            elif info:
                if key == 'ka' or key == 'kd' or key == 'ks':
                    ss = re.split(delimiter_pattern, value)
                    info[key] = [float(ss[0]), float(ss[1]), float(ss[2])]
                else:
                    info[key] = value

        materialCreator = MaterialCreator(self.texturePath or self.path, self.materialOptions)
        materialCreator.setCrossOrigin(self.crossOrigin)
        materialCreator.setManager(self.manager)
        materialCreator.setMaterials(materialsInfo)

        return materialCreator
