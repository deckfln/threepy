"""
/**
 * @author mrdoob / http:# //mrdoob.com/
 */
"""
from THREE.LoadingManager import *


class FileLoader:
    def __init__(self, manager=None ):
        self.manager = manager if manager is not None else DefaultLoadingManager
        self.path = None

    def load(self, url, onLoad, onProgress, onError ):
        global Cache

        if url is None:
            url = ''

        if self.path is not None:
            url = self.path + url

        cached = Cache.get( url )

        if cached is not None:
            return cached

        response = None
        with open(url) as f:
            response = f.read()
            if onLoad:
                onLoad( response )

        self.manager.itemStart( url )

        return response

    def setPath(self, value ):
        self.path = value
        return self

    def setResponseType(self, value ):
        self.responseType = value
        return self

    def setWithCredentials(self, value ):
        self.withCredentials = value
        return self

    def setMimeType(self, value ):
        self.mimeType = value
        return self

    def setRequestHeader(self, value ):
        self.requestHeader = value
        return self
