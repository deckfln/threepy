"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""


class LoadingManager:
    def __init__(self, onLoad=None, onProgress=None, onError=None ):
        self.isLoading = False
        self.itemsLoaded = 0
        self.itemsTotal = 0

        self.onStart = None
        self.onLoad = onLoad
        self.onProgress = onProgress
        self.onError = onError

    def itemStart(self, url ):
        self.itemsTotal +=1

        if not self.isLoading:
            if self.onStart:
                self.onStart( url, self.itemsLoaded, self.itemsTotal )

        self.isLoading = True

    def itemEnd(self, url ):
        self.itemsLoaded += 1

        if self.onProgress:
            self.onProgress( url, self.itemsLoaded, self.itemsTotal )

        if self.itemsLoaded == self.itemsTotal:
            self.isLoading = False

            if self.onLoad:
                self.onLoad()

    def itemError(self, url ):
        if self.onError:
            self.onError( url )


DefaultLoadingManager = LoadingManager()

"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""


class _Cache:
    def __init__(self):
        self.enabled = False
        self.files = {}

    def add(self, key, file ):
        if not self.enabled:
            return None
        # // console.log( 'THREE.Cache', 'Adding key:', key );
        self.files[ key ] = file

    def get(self, key ):
        if not self.enabled:
            return None

        if key not in self.files:
            return None

        # // console.log( 'THREE.Cache', 'Checking key:', key );
        return self.files[ key ]

    def remove(self, key ):
        del self.files[ key ]

    def clear(self):
        self.files = {}


Cache = _Cache()
