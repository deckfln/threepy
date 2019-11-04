"""
@author deckfln

Implement OpengGL 3.1 Uniform Buffer Objects
"""

import re
import numpy as np

from OpenGL.GL import *
from ctypes import sizeof, c_float, c_void_p, c_uint, string_at, memmove

_cython = False
if _cython:
    from cthree import cUpdateValueArrayElement, cUpdateValueMat3ArrayElement

from THREE.math.Matrix4 import *


_binding_point = 0

_glTypes = {
    GL_FLOAT: 4,
    GL_FLOAT_VEC2: 8,
    GL_FLOAT_VEC3: 12,
    GL_FLOAT_VEC4: 16,
    GL_DOUBLE: 8,
    GL_DOUBLE_VEC2: 16,
    GL_DOUBLE_VEC3: 24,
    GL_DOUBLE_VEC4: 23,
    GL_INT: 2,
    GL_INT_VEC2: 4,
    GL_INT_VEC3: 6,
    GL_INT_VEC4: 8,
    GL_UNSIGNED_INT: 2,
    GL_UNSIGNED_INT_VEC2: 4,
    GL_UNSIGNED_INT_VEC3: 6,
    GL_UNSIGNED_INT_VEC4: 8,
    GL_FLOAT_MAT2: 16,
    GL_FLOAT_MAT3: 36,
    GL_FLOAT_MAT4: 	64,
    GL_FLOAT_MAT2x3: 24,
    GL_FLOAT_MAT2x4: 32,
    GL_FLOAT_MAT3x2: 24,
    GL_FLOAT_MAT3x4: 48,
    GL_FLOAT_MAT4x2: 32,
    GL_FLOAT_MAT4x3: 48
}

_glTypesAlignment = {
    GL_FLOAT: 4,
    GL_FLOAT_VEC2: 8,
    GL_FLOAT_VEC3: 16,
    GL_FLOAT_VEC4: 16,
    GL_INT: 2,
    GL_INT_VEC2: 4,
    GL_INT_VEC3: 8,
    GL_INT_VEC4: 8,
    GL_UNSIGNED_INT: 2,
    GL_UNSIGNED_INT_VEC2: 4,
    GL_UNSIGNED_INT_VEC3: 8,
    GL_UNSIGNED_INT_VEC4: 8,
    GL_FLOAT_MAT4: 16
}

"""
upload data by sub data
"""


def _uploadValue4fm(self, value):
    if value.updated or not self.uploaded:
        OpenGL.raw.GL.VERSION.GL_1_5.glBufferSubData(GL_UNIFORM_BUFFER, self.offset, self.size, value.elements)
    # glBufferData(GL_UNIFORM_BUFFER, self.size, value.elements, GL_STATIC_DRAW)


def _uploadValue1f(self, value):
    OpenGL.raw.GL.VERSION.GL_1_5.glBufferSubData(GL_UNIFORM_BUFFER, self.offset, self.size, value)
    # glBufferData(GL_UNIFORM_BUFFER, self.size, value.elements, GL_STATIC_DRAW)


def _uploadValue3fv(self, value):
    OpenGL.raw.GL.VERSION.GL_1_5.glBufferSubData(GL_UNIFORM_BUFFER, self.offset, self.size, value.elements)


"""
Update data in a single unifoms buffer
"""


def _updateValueMat4(self, value, offset, buffer):
    """
    Update a single uniform or a full array of uniforms
    :param self:
    :param value:
    :param buffer:
    :return:
    """
    ctypes.memmove(buffer + int(offset), value.elements.ctypes.data, self.total_size)


def _updateValueMat3(self, value, buffer):
    """
    Mat3 are stored as 3 rows of vec4 in STD140
    """
    start = buffer + int(self.offset)

    ctypes.memmove(start, value.elements.ctypes.data, 12)
    ctypes.memmove(start + 16, value.elements.ctypes.data + 12, 12)
    ctypes.memmove(start + 32, value.elements.ctypes.data + 24, 12)


def _updateValueArrayElement(self, value, buffer, element):
    """
    Update a single uniform in an array of uniforms
    :param self:
    :param value:
    :param buffer:
    :param element:
    :return:
    """
    global _cython
    if _cython:
        cUpdateValueArrayElement(self, value, buffer, element)
    else:
        ctypes.memmove(buffer + int(self.offset + element * self.element_size), value.elements.ctypes.data, self.size)


def _updateValueMat3ArrayElement(self, value, buffer, element):
    """
    Mat3 are stored as 3 rows of vec4 in STD140
    """
    global _cython
    if _cython:
        cUpdateValueMat3ArrayElement(self, value, buffer, element)
    else:
        start = buffer + int(self.offset + element * self.element_size)

        ctypes.memmove(start, value.elements.ctypes.data, 12)
        ctypes.memmove(start + 16, value.elements.ctypes.data + 12, 12)
        ctypes.memmove(start + 32, value.elements.ctypes.data + 24, 12)


_int16 = np.zeros(1, np.int16)
_float = np.zeros(1, np.float32)


def _updateValueArray(self, value, offset, buffer):
    ctypes.memmove(buffer + int(offset), value.np.ctypes.data, self.size)


def _updateValueInt(self, value, offset, buffer):
    _int16[0] = value
    ctypes.memmove(buffer + int(offset), _int16.ctypes.data, self.size)


def _updateValueFloat(self, value, offset, buffer):
    _float[0] = value
    ctypes.memmove(buffer + int(offset), _float.ctypes.data, self.size)


_glTypesUpload = {
    GL_FLOAT: _uploadValue1f,
    GL_FLOAT_VEC2: None,
    GL_FLOAT_VEC3: _uploadValue3fv,
    GL_FLOAT_VEC4: None,
    GL_DOUBLE: None,
    GL_DOUBLE_VEC2: None,
    GL_DOUBLE_VEC3: None,
    GL_DOUBLE_VEC4: None,
    GL_INT: None,
    GL_INT_VEC2: None,
    GL_INT_VEC3: None,
    GL_INT_VEC4: None,
    GL_UNSIGNED_INT: None,
    GL_UNSIGNED_INT_VEC2: None,
    GL_UNSIGNED_INT_VEC3: None,
    GL_UNSIGNED_INT_VEC4: None,
    GL_FLOAT_MAT2: None,
    GL_FLOAT_MAT3: None,
    GL_FLOAT_MAT4: _uploadValue4fm,
    GL_FLOAT_MAT2x3: None,
    GL_FLOAT_MAT2x4: None,
    GL_FLOAT_MAT3x2: None,
    GL_FLOAT_MAT3x4: None,
    GL_FLOAT_MAT4x2: None,
    GL_FLOAT_MAT4x3: None
}


_glTypesUpdate = {
    GL_FLOAT_VEC2: _updateValueArray,
    GL_FLOAT_VEC3: _updateValueArray,
    GL_FLOAT_MAT3: _updateValueMat3,
    GL_FLOAT_MAT4: _updateValueMat4,
    GL_INT: _updateValueInt,
    GL_FLOAT: _updateValueFloat,
}

_glTypesUpdateArray = {
    GL_FLOAT_VEC3: _updateValueArrayElement,
    GL_FLOAT_MAT3: _updateValueMat3ArrayElement,
    GL_FLOAT_MAT4: _updateValueArrayElement,
    GL_INT: _updateValueArrayElement,
    GL_FLOAT: _updateValueArrayElement,
    GL_FLOAT_VEC2: _updateValueArrayElement,
}


class pyOpenGLUniformBuffer:
    def __init__(self, name, gltype, index, offset, total_size, elements, block):
        self.name = name
        self.index = index
        self.offset = offset
        self.total_size = total_size
        self.size = _glTypes[gltype]
        self.element_size = int(total_size/elements)
        self.uploaded = False
        self.value = None
        self.values = {}
        self.offsets = []
        self.uniforms_block = block

        self._upload = _glTypesUpload[gltype]
        self._update = _glTypesUpdate[gltype]
        self._update_array_element = _glTypesUpdateArray[gltype]

    def block(self):
        return self.uniforms_block

    def upload(self, value):
        self._upload(self, value)
        self.uploaded = True

    def update(self, value, buffer):
        self._update(self, value, self.offset, buffer)

    def update_array_element(self, value, buffer, element):
        self._update_array_element(self, value, buffer, element)

    def update_offset(self, value, index, buffer):
        offset = self.offsets[index]
        self._update(self, value, offset, buffer)


class _UniformBufferArrayOfStructs:
    """
    define array of structs in a uniform block
    """
    def __init__(self, name, block):
        self.name = name
        self.attributes = {}
        self.value = None
        self.values = {}
        self.uniforms_block = block

    def block(self):
        return self.uniforms_block

    def set_source(self, source_array):
        self.value = source_array

    def add(self, attr, index, gltype, offset):
        if attr not in self.attributes:
            self.attributes[attr] = pyOpenGLUniformBuffer(attr, gltype, -1, -1, 0, 1, self.uniforms_block)

        self.attributes[attr].offsets.append(offset)

    def add_value(self, value, index):
        self.values[index] = value

    def update(self, value, buffer):
        for i in range(len(value)):
            struct = value[i]
            for attrib in struct.__dict__:
                if attrib in self.attributes:
                    v = struct.__dict__[attrib]
                    self.attributes[attrib].update_offset(v, i, buffer)


class pyOpenGLUniformBlock:
    def __init__(self, program, name, index):
        self.name = name
        self.buffer = None

        data_size = arrays.GLintArray.zeros((1,))
        # https://forge.univ-lyon1.fr/Alexandre.Meyer/gkit2light/commit/972d7fb4ed2cb8b36da81ba6e72219663f59cee4
        # glGetActiveUniformBlockiv(program, index, GL_UNIFORM_BLOCK_DATA_SIZE, data_size)
        glGetProgramResourceiv(program, GL_UNIFORM_BLOCK, index, 1, GL_BUFFER_DATA_SIZE, 1, None, data_size)
        self.size = data_size[0]

        active_uniforms = arrays.GLintArray.zeros((1,))
        # glGetActiveUniformBlockiv(program, index, GL_UNIFORM_BLOCK_ACTIVE_UNIFORMS, active_uniforms)
        glGetProgramResourceiv(program, GL_UNIFORM_BLOCK, index, 1, GL_NUM_ACTIVE_VARIABLES, 1, None, active_uniforms)
        nbuniforms = active_uniforms[0]

        indices = arrays.GLintArray.zeros((nbuniforms,))
        # glGetActiveUniformBlockiv(program, index, GL_UNIFORM_BLOCK_ACTIVE_UNIFORM_INDICES, indices)
        glGetProgramResourceiv(program, GL_UNIFORM_BLOCK, index, 1, GL_ACTIVE_VARIABLES, nbuniforms, None, indices)

        # offsets = arrays.GLintArray.zeros((nbuniforms,))
        # glGetActiveUniformsiv(program, active_uniforms[0], indices, GL_UNIFORM_OFFSET, offsets)

        self.uniforms = {}
        pattern = '(.*)\[ *(\d)\ *]\.(.*)'
        last_index = -1

        query = arrays.GLintArray.zeros((4,))
        query[0] = GL_OFFSET
        query[1] = GL_NAME_LENGTH
        query[2] = GL_TYPE
        query[3] = GL_ARRAY_SIZE

        result = arrays.GLintArray.zeros((4,))

        for i in range(len(indices)):
            uniform_index = indices[i]

            glGetProgramResourceiv(program, GL_UNIFORM, uniform_index, 4, query, 4, None, result)
            offset = result[0]
            name_len = result[1]
            gltype = result[2]
            elements = result[3]

            uname = ctypes.create_string_buffer(int(name_len))
            glGetProgramResourceName(program, GL_UNIFORM, uniform_index, name_len, None, uname)
            uname = uname.value[:int(name_len)].decode("utf-8")

            # uname, elements, gltype = glGetActiveUniform(program, uniform_index)
            # uname = uname.decode("utf-8")

            # if elements > 0 and we see an indices
            # mark basic variables + numbers : "vec3 data[10]" => 10 elements of data[0]
            if '[0]' in uname and elements > 1:
                uname = uname.replace('[0]', '')

            # find structured variables + numbers :
            # struct {
            #   vec3 v3
            #   int  i
            # }
            # structure data[10]
            # => 1 elements of data[0].v3
            # => 1 elements of data[0].i
            # => 1 elements of data[1].v3
            # => 1 elements of data[1].i
            aindices = re.search(pattern, uname)
            if aindices is not None:
                array = uname[aindices.regs[1][0] : aindices.regs[1][1]]
                index = int(uname[aindices.regs[2][0] : aindices.regs[2][1]])
                field = uname[aindices.regs[3][0] : aindices.regs[3][1]]

                if array not in self.uniforms:
                    self.uniforms[array] = _UniformBufferArrayOfStructs(array, self)

                self.uniforms[array].add(field, index, gltype, offset)

            else:
                self.uniforms[uname] = pyOpenGLUniformBuffer(uname, gltype, i, offset, data_size[0], elements, self)

        self.binding_point = -1
        self._buffer = -1

    def bind(self, index, shader):
        global _binding_point

        if self.binding_point < 0:
            self.binding_point = _binding_point
            _binding_point += 1

        glUniformBlockBinding(shader, index, self.binding_point)

    def create(self):
        self._buffer = glGenBuffers(1)

        glBindBuffer(GL_UNIFORM_BUFFER, self._buffer)
        glBufferData(GL_UNIFORM_BUFFER, self.size, None, GL_STATIC_DRAW)
        glBindBuffer(GL_UNIFORM_BUFFER, 0)

        glBindBufferBase(GL_UNIFORM_BUFFER, self.binding_point, self._buffer)

    def upload(self):
        glBindBuffer(GL_UNIFORM_BUFFER, self._buffer)
        for uniform in self.uniforms.keys():
            value = uniform.value
            if value is not None:
                uniform.upload(value)
        glBindBuffer(GL_UNIFORM_BUFFER, 0)

    def lock(self):
        if self.buffer is None:
            glBindBuffer(GL_UNIFORM_BUFFER, self._buffer)
            self.buffer = glMapBuffer(GL_UNIFORM_BUFFER, GL_WRITE_ONLY)
            # glUnmapBuffer(GL_UNIFORM_BUFFER)

    def unlock(self):
        if self.buffer is not None:
            glBindBuffer(GL_UNIFORM_BUFFER, self._buffer)
            glUnmapBuffer(GL_UNIFORM_BUFFER)
            self.buffer = None

    def get_uniform(self, uniform):
        if uniform in self.uniforms:
            return self.uniforms[uniform]

        return None

    def update_array_element(self, name, index, value):
        uniform = self.uniforms[name]
        uniform._update_array_element(uniform, value, self.buffer, index)

    def update_value(self, name, value):
        uniform = self.uniforms[name]
        uniform.update(value, self.buffer)

    def update(self):
        for uniform in self.uniforms.values():
            value = uniform.value
            if value is not None:
                uniform.update(value, self.buffer)

            # for arrays, update a list of individual values
            values = uniform.values
            if len(values) > 0:
                for index in values:
                    uniform.update_array_element(values[index], self.buffer, index)
                values.clear()


class pyOpenGLUniformBlocks:
    def __init__(self):
        self.uniform_blocks = {}
        self.uniforms = {}
        self._mapping = np.full(1024, -1, np.int16)    # mapping table for the modelMatrices UBO
        self._mapping_max = 0

    def add(self, program, vertex, fragment):
        # list the uniforms block
        ub = glGetProgramInterfaceiv(program, GL_UNIFORM_BLOCK, GL_ACTIVE_RESOURCES)

        query = arrays.GLintArray.zeros((1,))
        query[0] = GL_NAME_LENGTH
        length = arrays.GLintArray.zeros((1,))

        for index in range(ub):
            # length = arrays.GLintArray.zeros((1,))
            # glGetActiveUniformBlockiv(program, index, GL_UNIFORM_BLOCK_NAME_LENGTH, length)
            glGetProgramResourceiv(program, GL_UNIFORM_BLOCK, index, 1, query, 1, None, length)

            name = ctypes.create_string_buffer(int(length[0]))
            # glGetActiveUniformBlockName(program, index, length, None, name)
            glGetProgramResourceName(program, GL_UNIFORM_BLOCK, index, length, None, name)
            name = name.value[:int(length)].decode("utf-8")

            if name not in self.uniform_blocks:
                uniform_block = pyOpenGLUniformBlock(program, name, index)
                uniform_block.bind(index, program)
                uniform_block.create()

                self.uniform_blocks[name] = uniform_block

                for uniform in uniform_block.uniforms.values():
                    self.uniforms[uniform.name] = uniform
            else:
                uniform_block = self.uniform_blocks[name]
                uniform_block.bind(index, program)

    def uploaded(self, name):
        if name in self.uniforms:
            return self.uniforms[name].uploaded

        return True

    def get_uniform(self, uniform):
        if uniform in self.uniforms:
            block = self.uniforms[uniform].block()
            return block.get_uniform(uniform)

        return None

    def get_block(self, uniform):
        if uniform in self.uniforms:
            return self.uniforms[uniform].block()

        return None

    def set_value(self, uniform, value):
        if uniform in self.uniforms:
            block = self.uniforms[uniform].block()
            block.update_value(uniform, value)

    def set_array_value(self, uniform, element, value):
        if uniform in self.uniforms:
            block = self.uniforms[uniform].block()
            block.update_array_element(uniform, element, value)

    def upload(self):
        for block in self.uniform_blocks.values():
            block.upload()

    def lock(self):
        for block in self.uniform_blocks.values():
            block.lock()

    def unlock(self):
        for block in self.uniform_blocks.values():
            block.unlock()

        glBindBuffer(GL_UNIFORM_BUFFER, 0)

    def update(self, block=None):
        return

    def map_id(self, id: int):
        index = self._mapping[id]
        if index < 0:
            index = self._mapping_max
            self._mapping[index] = id
            self._mapping_max += 1

        return index

