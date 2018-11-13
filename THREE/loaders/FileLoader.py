"""
/**
 * @author mrdoob / http:# //mrdoob.com/
 */
"""
from THREE.loaders.LoadingManager import *


class FileLoader:
    def __init__(self, manager=None ):
        self.manager = manager if manager is not None else DefaultLoadingManager
        self.path = None
        self.responseType = ''
        self.withCredentials = False
        self.mimeType = None
        self.requestHeader = None

    def load(self, url, onLoad=None, onProgress=None, onError=None):
        global Cache

        if url is None:
            url = ''

        if self.path is not None:
            url = self.path + '/'+ url

        cached = Cache.get( url )

        if cached is not None:
            return cached

        response = None
        flag = 'r'+self.responseType
        if self.responseType == '':
            # print("FileLoader: warning utf8")
            with open(url, flag, encoding='utf-8') as f:
                response = f.read()
                if onLoad:
                    onLoad( response )
        else:
            with open(url, flag) as f:
                response = f.read()
                if onLoad:
                    onLoad( response )

        self.manager.itemStart( url )

        return response

    def setPath(self, value ):
        self.path = value
        return self

    def setResponseType(self, value ):
        if value == 'arraybuffer':
            self.responseType = 'b'
        else:
            self.responseType = ''
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
