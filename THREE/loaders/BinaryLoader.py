"""
/**
 * @author alteredq / http:# //alteredqualia.com/
 */
"""
import json
import numpy as np

from THREE.Geometry import *
from THREE.javascriparray import *
from THREE.Vector3 import *
from THREE.FileLoader import *
from THREE.Loader import *


class _Model(Geometry):
    def __init__(self, texturePath, data):
        currentOffset = 0
        normals = []
        uvs = []

        super().__init__()

        def parseString(data, offset, length):
            charArray = data[offset:offset+length]
            text = ""
            for i in range(length):
                text += chr(charArray[i])
            return text

        def parseUChar8(data, offset):
            return data[offset]

        def parseUInt32(data, offset):
            dt = np.dtype(int)
            i = np.frombuffer(data, dt, 1, offset)
            return int(i)
    
        def parseMetaData(data, offset):
            metaData = {
                'signature'               : parseString(data, offset,  12),
                'header_bytes'            : parseUChar8(data, offset + 12),

                'vertex_coordinate_bytes' : parseUChar8(data, offset + 13),
                'normal_coordinate_bytes' : parseUChar8(data, offset + 14),
                'uv_coordinate_bytes'     : parseUChar8(data, offset + 15),

                'vertex_index_bytes'      : parseUChar8(data, offset + 16),
                'normal_index_bytes'      : parseUChar8(data, offset + 17),
                'uv_index_bytes'          : parseUChar8(data, offset + 18),
                'material_index_bytes'    : parseUChar8(data, offset + 19),

                'nvertices'    : parseUInt32(data, offset + 20),
                'nnormals'     : parseUInt32(data, offset + 20 + 4 * 1),
                'nuvs'         : parseUInt32(data, offset + 20 + 4 * 2),

                'ntri_flat'      : parseUInt32(data, offset + 20 + 4 * 3),
                'ntri_smooth'    : parseUInt32(data, offset + 20 + 4 * 4),
                'ntri_flat_uv'   : parseUInt32(data, offset + 20 + 4 * 5),
                'ntri_smooth_uv' : parseUInt32(data, offset + 20 + 4 * 6),

                'nquad_flat'      : parseUInt32(data, offset + 20 + 4 * 7),
                'nquad_smooth'    : parseUInt32(data, offset + 20 + 4 * 8),
                'nquad_flat_uv'   : parseUInt32(data, offset + 20 + 4 * 9),
                'nquad_smooth_uv' : parseUInt32(data, offset + 20 + 4 * 10)
            }
            """
                        console.log("signature: " + metaData.signature)

                        console.log("header_bytes: " + metaData.header_bytes)
                        console.log("vertex_coordinate_bytes: " + metaData.vertex_coordinate_bytes)
                        console.log("normal_coordinate_bytes: " + metaData.normal_coordinate_bytes)
                        console.log("uv_coordinate_bytes: " + metaData.uv_coordinate_bytes)

                        console.log("vertex_index_bytes: " + metaData.vertex_index_bytes)
                        console.log("normal_index_bytes: " + metaData.normal_index_bytes)
                        console.log("uv_index_bytes: " + metaData.uv_index_bytes)
                        console.log("material_index_bytes: " + metaData.material_index_bytes)

                        console.log("nvertices: " + metaData.nvertices)
                        console.log("nnormals: " + metaData.nnormals)
                        console.log("nuvs: " + metaData.nuvs)

                        console.log("ntri_flat: " + metaData.ntri_flat)
                        console.log("ntri_smooth: " + metaData.ntri_smooth)
                        console.log("ntri_flat_uv: " + metaData.ntri_flat_uv)
                        console.log("ntri_smooth_uv: " + metaData.ntri_smooth_uv)

                        console.log("nquad_flat: " + metaData.nquad_flat)
                        console.log("nquad_smooth: " + metaData.nquad_smooth)
                        console.log("nquad_flat_uv: " + metaData.nquad_flat_uv)
                        console.log("nquad_smooth_uv: " + metaData.nquad_smooth_uv)

                        total = metaData.header_bytes
                                  + metaData.nvertices * metaData.vertex_coordinate_bytes * 3
                                  + metaData.nnormals * metaData.normal_coordinate_bytes * 3
                                  + metaData.nuvs * metaData.uv_coordinate_bytes * 2
                                  + metaData.ntri_flat * (metaData.vertex_index_bytes*3 + metaData.material_index_bytes)
                                  + metaData.ntri_smooth * (metaData.vertex_index_bytes*3 + metaData.material_index_bytes + metaData.normal_index_bytes*3)
                                  + metaData.ntri_flat_uv * (metaData.vertex_index_bytes*3 + metaData.material_index_bytes + metaData.uv_index_bytes*3)
                                  + metaData.ntri_smooth_uv * (metaData.vertex_index_bytes*3 + metaData.material_index_bytes + metaData.normal_index_bytes*3 + metaData.uv_index_bytes*3)
                                  + metaData.nquad_flat * (metaData.vertex_index_bytes*4 + metaData.material_index_bytes)
                                  + metaData.nquad_smooth * (metaData.vertex_index_bytes*4 + metaData.material_index_bytes + metaData.normal_index_bytes*4)
                                  + metaData.nquad_flat_uv * (metaData.vertex_index_bytes*4 + metaData.material_index_bytes + metaData.uv_index_bytes*4)
                                  + metaData.nquad_smooth_uv * (metaData.vertex_index_bytes*4 + metaData.material_index_bytes + metaData.normal_index_bytes*4 + metaData.uv_index_bytes*4)
                        console.log("total bytes: " + total)
            """

            return metaData

        def handlePadding(n):
            return (4 - n % 4) if (n % 4) else 0

        def init_vertices(start):
            nonlocal md, data
            nElements = int(md['nvertices'])
            dt = np.dtype(np.float32)
            coordArray = np.frombuffer(data, dt, nElements * 3, start)

            for i in range(nElements):
                x = coordArray[i * 3]
                y = coordArray[i * 3 + 1]
                z = coordArray[i * 3 + 2]

                self.vertices.append(THREE.Vector3(x, y, z))

            return nElements * 3 * dt.itemsize

        def init_normals(start):
            nonlocal md, data
            nElements = int(md['nnormals'])

            if nElements:
                dt = np.dtype(np.int8)
                normalArray = np.frombuffer(data, dt, nElements * 3, start)

                for i in range(nElements):
                    x = normalArray[i * 3]
                    y = normalArray[i * 3 + 1]
                    z = normalArray[i * 3 + 2]

                    normals.extend([x / 127, y / 127, z / 127])

            return nElements * 3 * dt.itemsize

        def init_uvs(start):
            nonlocal md, data
            nElements = int(md['nuvs'])
            dt = np.dtype(np.float32)

            if nElements:
                uvArray = np.frombuffer(data, dt, nElements * 2, start)

                for i in range(nElements):
                    u = uvArray[i * 2]
                    v = uvArray[i * 2 + 1]

                    uvs.extend([u, v])

            return nElements * 2 * dt.itemsize

        def init_faces3_flat(nElements, offsetVertices, offsetMaterials):
            dt = np.dtype(np.uint32)
            vertexIndexBuffer = np.frombuffer(data, dt, 3 * nElements, offsetVertices)
            dt = np.dtype(np.uint16)
            materialIndexBuffer = np.frombuffer(data, dt, nElements , offsetMaterials)

            for i in range(nElements):
                a = vertexIndexBuffer[i * 3]
                b = vertexIndexBuffer[i * 3 + 1]
                c = vertexIndexBuffer[i * 3 + 2]

                m = materialIndexBuffer[i]

                self.faces.push(THREE.Face3(a, b, c, None, None, m))

        def init_uvs3(nElements, offset):
            dt = np.dtype(np.uint32)
            uvIndexBuffer = np.frombuffer(data, dt, 3 * nElements, offset)

            for i in range(nElements):
                uva = uvIndexBuffer[i * 3]
                uvb = uvIndexBuffer[i * 3 + 1]
                uvc = uvIndexBuffer[i * 3 + 2]

                u1 = uvs[uva * 2]
                v1 = uvs[uva * 2 + 1]

                u2 = uvs[uvb * 2]
                v2 = uvs[uvb * 2 + 1]

                u3 = uvs[uvc * 2]
                v3 = uvs[uvc * 2 + 1]

                self.faceVertexUvs[0].append([
                    THREE.Vector2(u1, v1),
                    THREE.Vector2(u2, v2),
                    THREE.Vector2(u3, v3)
               ])
                
        def init_triangles_flat_uv(start):
            nonlocal md
            nElements = int(md['ntri_flat_uv'])

            if nElements:
                offsetUvs = start + nElements * np.uint32.itemsize * 3
                offsetMaterials = offsetUvs + nElements * np.dtype(np.uint32).itemsize * 3

                init_faces3_flat(nElements, start, offsetMaterials)
                init_uvs3(nElements, offsetUvs)

        def init_faces3_smooth(nElements, offsetVertices, offsetNormals, offsetMaterials):
            dt = np.dtype(np.uint32)
            vertexIndexBuffer = np.frombuffer(data, dt, 3 * nElements, offsetVertices)
            normalIndexBuffer = np.frombuffer(data, dt, 3 * nElements, offsetNormals)
            dt = np.dtype(np.uint16)
            materialIndexBuffer = np.frombuffer(data, dt, nElements, offsetMaterials)

            self.faces = [None for i in range(nElements)]
            for i in range(nElements):
                i3 = i * 3
                a = vertexIndexBuffer[i3]
                b = vertexIndexBuffer[i3 + 1]
                c = vertexIndexBuffer[i3 + 2]

                na = normalIndexBuffer[i3]
                nb = normalIndexBuffer[i3 + 1]
                nc = normalIndexBuffer[i3 + 2]

                m = materialIndexBuffer[i]

                na3 = na * 3
                nax = normals[na3]
                nay = normals[na3 + 1]
                naz = normals[na3 + 2]

                nb3 = nb * 3
                nbx = normals[nb3]
                nby = normals[nb3 + 1]
                nbz = normals[nb3 + 2]

                nc3 = nc * 3
                ncx = normals[nc3]
                ncy = normals[nc3 + 1]
                ncz = normals[nc3 + 2]

                self.faces[i] = THREE.Face3(a, b, c, [
                    THREE.Vector3(nax, nay, naz),
                    THREE.Vector3(nbx, nby, nbz),
                    THREE.Vector3(ncx, ncy, ncz)
               ], None, m)

        def init_triangles_smooth_uv(start):
            nonlocal md
            nElements = int(md['ntri_smooth_uv'])

            if nElements:
                offsetNormals = start + nElements * np.dtype(np.uint32).itemsize * 3
                offsetUvs = offsetNormals + nElements * np.dtype(np.uint32).itemsize * 3
                offsetMaterials = offsetUvs + nElements * np.dtype(np.uint32).itemsize * 3

                init_faces3_smooth(nElements, start, offsetNormals, offsetMaterials)
                init_uvs3(nElements, offsetUvs)

        def init_triangles_flat(start):
            nonlocal md
            nElements = int(md['ntri_flat'])

            if nElements:
                offsetMaterials = start + nElements * np.dtype(np.uint32).itemsize * 3
                init_faces3_flat(nElements, start, offsetMaterials)
                
        def init_faces4_flat(nElements, offsetVertices, offsetMaterials):
            dt = np.dtype(np.uint32)
            vertexIndexBuffer = np.frombuffer(data, dt, 4 * nElements, offsetVertices)
            dt = np.dtype(np.uint16)
            materialIndexBuffer = np.frombuffer(data, dt, nElements, offsetMaterials)

            for i in range(nElements):
                a = vertexIndexBuffer[i * 4]
                b = vertexIndexBuffer[i * 4 + 1]
                c = vertexIndexBuffer[i * 4 + 2]
                d = vertexIndexBuffer[i * 4 + 3]

                m = materialIndexBuffer[i]

                self.faces.append(THREE.Face3(a, b, d, None, None, m))
                self.faces.append(THREE.Face3(b, c, d, None, None, m))

        def init_uvs4(nElements, offset):
            dt = np.dtype(np.uint32)
            uvIndexBuffer = np.numpy(data, dt, 4 * nElements, offset)

            for i in range(nElements):
                uva = uvIndexBuffer[i * 4]
                uvb = uvIndexBuffer[i * 4 + 1]
                uvc = uvIndexBuffer[i * 4 + 2]
                uvd = uvIndexBuffer[i * 4 + 3]

                u1 = uvs[uva * 2]
                v1 = uvs[uva * 2 + 1]

                u2 = uvs[uvb * 2]
                v2 = uvs[uvb * 2 + 1]

                u3 = uvs[uvc * 2]
                v3 = uvs[uvc * 2 + 1]

                u4 = uvs[uvd * 2]
                v4 = uvs[uvd * 2 + 1]

                self.faceVertexUvs[0].append([
                    THREE.Vector2(u1, v1),
                    THREE.Vector2(u2, v2),
                    THREE.Vector2(u4, v4)
               ])

                self.faceVertexUvs[0].append([
                    THREE.Vector2(u2, v2),
                    THREE.Vector2(u3, v3),
                    THREE.Vector2(u4, v4)
               ])
                
        def init_quads_flat_uv(start):
            nonlocal md
            nElements = int(md['nquad_flat_uv'])

            if nElements:
                offsetUvs = start + nElements * np.dtype(np.uint32).itemsize * 4
                offsetMaterials = offsetUvs + nElements * np.dtype(np.uint32).itemsize * 4

                init_faces4_flat(nElements, start, offsetMaterials)
                init_uvs4(nElements, offsetUvs)

        def init_faces4_smooth(nElements, offsetVertices, offsetNormals, offsetMaterials):
            dt = np.dtype(np.uint32)
            vertexIndexBuffer = np.numpy(data, dt, 4 * nElements, offsetVertices)
            normalIndexBuffer = np.numpy(data, dt, 4 * nElements, offsetNormals)
            dt = np.dtype(np.uint16)
            materialIndexBuffer = np.frombuffer(data, dt, nElements, offsetMaterials)

            for i in range(nElements):
                a = vertexIndexBuffer[i * 4]
                b = vertexIndexBuffer[i * 4 + 1]
                c = vertexIndexBuffer[i * 4 + 2]
                d = vertexIndexBuffer[i * 4 + 3]

                na = normalIndexBuffer[i * 4]
                nb = normalIndexBuffer[i * 4 + 1]
                nc = normalIndexBuffer[i * 4 + 2]
                nd = normalIndexBuffer[i * 4 + 3]

                m = materialIndexBuffer[i]

                nax = normals[na * 3]
                nay = normals[na * 3 + 1]
                naz = normals[na * 3 + 2]

                nbx = normals[nb * 3]
                nby = normals[nb * 3 + 1]
                nbz = normals[nb * 3 + 2]

                ncx = normals[nc * 3]
                ncy = normals[nc * 3 + 1]
                ncz = normals[nc * 3 + 2]

                ndx = normals[nd * 3]
                ndy = normals[nd * 3 + 1]
                ndz = normals[nd * 3 + 2]

                self.faces.append(THREE.Face3(a, b, d, [
                    THREE.Vector3(nax, nay, naz),
                    THREE.Vector3(nbx, nby, nbz),
                    THREE.Vector3(ndx, ndy, ndz)
               ], None, m))

                self.faces.append(THREE.Face3(b, c, d, [
                    THREE.Vector3(nbx, nby, nbz),
                    THREE.Vector3(ncx, ncy, ncz),
                    THREE.Vector3(ndx, ndy, ndz)
               ], None, m))

        def init_quads_flat(start):
            nonlocal md
            nElements = int(md['nquad_flat'])

            if nElements:
                offsetMaterials = start + nElements * np.dtype(np.uint32).itemsize * 4
                init_faces4_flat(nElements, start, offsetMaterials)
                
        def init_quads_smooth(start):
            nonlocal md
            nElements = int(md['nquad_smooth'])

            if nElements:
                offsetNormals = start + nElements * np.dtype(np.uint32).itemsize * 4
                offsetMaterials = offsetNormals + nElements * np.dtype(np.uint32).itemsize * 4

                init_faces4_smooth(nElements, start, offsetNormals, offsetMaterials)

        def init_quads_smooth_uv(start):
            nonlocal md
            nElements = md['nquad_smooth_uv']

            if nElements:
                offsetNormals = start + nElements * np.dtype(np.uint32).itemsize * 4
                offsetUvs = offsetNormals + nElements * np.dtype(np.uint32).itemsize * 4
                offsetMaterials = offsetUvs + nElements * np.dtype(np.uint32).itemsize * 4

                init_faces4_smooth(nElements, start, offsetNormals, offsetMaterials)
                init_uvs4(nElements, offsetUvs)

        def init_triangles_smooth(start):
            nonlocal md
            nElements = md['ntri_smooth']

            if nElements:
                offsetNormals = start + nElements * np.dtype(np.uint32).itemsize * 3
                offsetMaterials = offsetNormals + nElements * np.dtype(np.uint32).itemsize * 3

                init_faces3_smooth(nElements, start, offsetNormals, offsetMaterials)

        md = parseMetaData(data, currentOffset)

        currentOffset += md['header_bytes']
        # // buffers sizes

        tri_size =  md['vertex_index_bytes'] * 3 + md['material_index_bytes']
        quad_size = md['vertex_index_bytes'] * 4 + md['material_index_bytes']

        len_tri_flat      = md['ntri_flat']      * (tri_size)
        len_tri_smooth    = md['ntri_smooth']   * (tri_size + md['normal_index_bytes'] * 3)
        len_tri_flat_uv   = md['ntri_flat_uv']   * (tri_size + md['uv_index_bytes'] * 3)
        len_tri_smooth_uv = md['ntri_smooth_uv'] * (tri_size + md['normal_index_bytes'] * 3 + md['uv_index_bytes'] * 3)

        len_quad_flat      = md['nquad_flat']      * (quad_size)
        len_quad_smooth    = md['nquad_smooth']    * (quad_size + md['normal_index_bytes'] * 4)
        len_quad_flat_uv   = md['nquad_flat_uv']   * (quad_size + md['uv_index_bytes'] * 4)

        # // read buffers

        currentOffset += init_vertices(currentOffset)

        currentOffset += init_normals(currentOffset)
        currentOffset += handlePadding(md['nnormals'] * 3)

        currentOffset += init_uvs(currentOffset)

        start_tri_flat         = currentOffset
        start_tri_smooth    = start_tri_flat    + len_tri_flat    + handlePadding(md['ntri_flat'] * 2)
        start_tri_flat_uv   = start_tri_smooth  + len_tri_smooth  + handlePadding(md['ntri_smooth'] * 2)
        start_tri_smooth_uv = start_tri_flat_uv + len_tri_flat_uv + handlePadding(md['ntri_flat_uv'] * 2)

        start_quad_flat     = start_tri_smooth_uv + len_tri_smooth_uv  + handlePadding(md['ntri_smooth_uv'] * 2)
        start_quad_smooth   = start_quad_flat     + len_quad_flat       + handlePadding(md['nquad_flat'] * 2)
        start_quad_flat_uv  = start_quad_smooth   + len_quad_smooth    + handlePadding(md['nquad_smooth'] * 2)
        start_quad_smooth_uv = start_quad_flat_uv  + len_quad_flat_uv   + handlePadding(md['nquad_flat_uv'] * 2)

        # // have to first process faces with uvs
        # // so that face and uv indices match

        init_triangles_flat_uv(start_tri_flat_uv)
        init_triangles_smooth_uv(start_tri_smooth_uv)

        init_quads_flat_uv(start_quad_flat_uv)
        init_quads_smooth_uv(start_quad_smooth_uv)

        # // now we can process untextured faces

        init_triangles_flat(start_tri_flat)
        init_triangles_smooth(start_tri_smooth)

        init_quads_flat(start_quad_flat)
        init_quads_smooth(start_quad_smooth)

        self.computeFaceNormals()

        
class BinaryLoader(Loader):
    def __init__(self, manager=None):

        if isinstance(manager, bool):
            print('THREE.BinaryLoader: showStatus parameter has been removed from constructor.')
            manager = None

        self.manager = manager if manager else THREE.DefaultLoadingManager
        self.texturePath = None
        self.binaryPath = None

    # // Load models generated by slim OBJ converter with BINARY option (converter_obj_three_slim.py -t binary)
    # //  - binary models consist of two files: JS and BIN
    # //  - parameters
    # //        - url (required)
    # //        - callback (required)
    # //        - texturePath (optional: if not specified, textures will be assumed to be in the same folder as JS model file)
    # //        - binaryPath (optional: if not specified, binary file will be assumed to be in the same folder as JS model file)
    def load(self, url, onLoad=None, onProgress=None, onError=None):

        # // todo: unify load API to for easier SceneLoader use

        texturePath = self.texturePath or THREE.Loader.extractUrlBase(url)
        binaryPath  = self.binaryPath or THREE.Loader.extractUrlBase(url)

        # // #1 load JS part via web worker
        jso = []

        def _load1(bufData):
            nonlocal jso
            # // IEWEBGL needs self ???
            # //buffer = (Uint8Array(xhr.responseBody)).buffer

            # //# // iOS and other XMLHttpRequest level 1 ???
            self.parse(bufData, onLoad, texturePath, jso['materials'])
        
        def _load(data):
            nonlocal jso
            jso = json.loads(data)

            bufferUrl = binaryPath + jso['buffers']

            bufferLoader = THREE.FileLoader(self.manager)
            bufferLoader.setResponseType('arraybuffer')
            bufferLoader.load(bufferUrl, _load1)
        
        jsonloader = THREE.FileLoader(self.manager)
        jsonloader.load(url, _load)

    def setBinaryPath(self, value):
        self.binaryPath = value

    def setCrossOrigin(self, value):
        self.crossOrigin = value

    def setTexturePath(self, value):
        self.texturePath = value

    def parse(self, data, callback, texturePath, jsonMaterials):
        geometry = _Model(texturePath, data)
        materials = THREE.Loader.initMaterials(jsonMaterials, texturePath, True)

        callback(geometry, materials)
