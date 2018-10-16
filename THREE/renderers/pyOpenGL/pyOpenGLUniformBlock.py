"""
@author deckfln

Implement OpengGL 3.1 Uniform Buffer Objects
"""

import re
from OpenGL.GL import *
from ctypes import sizeof, c_float, c_void_p, c_uint, string_at, memmove

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


def _updateValue4fm(self, value, offset, buffer):
    """
    Update a single uniform or a full array of uniforms
    :param self:
    :param value:
    :param buffer:
    :return:
    """
    if value.updated or not self.uploaded:
        ctypes.memmove(buffer + int(offset), value.elements.ctypes.data, self.total_size)


def _updateValue4iv(self, value, buffer, element):
    """
    Update a single uniform in an array of uniforms
    :param self:
    :param value:
    :param buffer:
    :param element:
    :return:
    """
    size = self.size
    src = value.elements.ctypes.data
    dst = buffer + int(self.offset) + element * size
    ctypes.memmove(dst, src, size)


def _updateValue(self, value, offset, buffer):
    ctypes.memmove(buffer + int(offset), value.elements.ctypes.data, self.size)


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
    GL_FLOAT_VEC3: _updateValue,
    GL_FLOAT_MAT4: _updateValue4fm,
    GL_INT: _updateValue,
    GL_FLOAT: _updateValue,
    GL_FLOAT_VEC2: _updateValue,
}


class pyOpenGLUniformBuffer:
    def __init__(self, name, gltype, index, offset, total_size, elements):
        self.name = name
        self.index = index
        self.offset = offset
        self.total_size = total_size
        self.size = _glTypes[gltype]
        self.elements = elements
        self.uploaded = False
        self.value = None
        self.values = {}
        self.offsets = []

        self._upload = _glTypesUpload[gltype]
        self._update = _glTypesUpdate[gltype]

    def upload(self, value):
        self._upload(self, value)
        self.uploaded = True

    def update(self, value, buffer):
        self._update(self, value, self.offset, buffer)

    def update_element(self, value, buffer, element):
        self._update(self, value, self.offset + self.size * element, buffer)

    def update_index(self, value, index, buffer):
        offset = self.offsets[index]
        self._update(self, value, offset, buffer)


class _UniformBufferArrayOfStructs:
    """
    define array of structs in a uniform block
    """
    def __init__(self, name):
        self.name = name
        self.attributes = {}
        self.value = None
        self.values = {}

    def set_source(self, source_array):
        self.value = source_array

    def add(self, attr, index, gltype, offset):
        if attr not in self.attributes:
            self.attributes[attr] = pyOpenGLUniformBuffer(attr, gltype, -1, -1, 0, 0)

        self.attributes[attr].offsets.append(offset)

    def add_value(self, value, index):
        self.values[index] = value

    def update(self, buffer):
        for i in range(len(self.value)):
            struct = self.value[i]
            for attrib in struct.__dict__:
                if attrib in self.attributes:
                    v = struct.__dict__[attrib]
                    self.attributes[attrib].update_index(v, i, buffer)


class pyOpenGLUniformBlock:
    def __init__(self, program, name, index):
        self.index = index
        self.name = name

        data_size = arrays.GLintArray.zeros((1,))
        glGetActiveUniformBlockiv(program, index, GL_UNIFORM_BLOCK_DATA_SIZE, data_size)
        self.size = data_size[0]

        active_uniforms = arrays.GLintArray.zeros((1,))
        glGetActiveUniformBlockiv(program, index, GL_UNIFORM_BLOCK_ACTIVE_UNIFORMS, active_uniforms)

        indices = arrays.GLintArray.zeros((active_uniforms[0],))
        glGetActiveUniformBlockiv(program, index, GL_UNIFORM_BLOCK_ACTIVE_UNIFORM_INDICES, indices)

        offsets = arrays.GLintArray.zeros((active_uniforms[0],))
        glGetActiveUniformsiv(program, active_uniforms[0], indices, GL_UNIFORM_OFFSET, offsets)

        self.uniforms = {}
        pattern = '(.*)\[ *(\d)\ *]\.(.*)'
        last_index = -1

        for i in range(len(indices)):
            uniform_index = indices[i]
            offset = offsets[i]

            uname, elements, gltype = glGetActiveUniform(program, uniform_index)
            uname = uname.decode("utf-8")

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
                    self.uniforms[array] = _UniformBufferArrayOfStructs(array)

                self.uniforms[array].add(field, index, gltype, offset)

            else:
                total_size = _glTypes[gltype] * elements
                self.uniforms[uname] = pyOpenGLUniformBuffer(uname, gltype, i, offset, total_size, elements)

        self.binding_point = -1
        self._buffer = -1

    def bind(self, shader):
        global _binding_point

        if self.binding_point < 0:
            self.binding_point = _binding_point
            _binding_point += 1

        glUniformBlockBinding(shader, self.index, self.binding_point)

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

    def update(self):
        glBindBuffer(GL_UNIFORM_BUFFER, self._buffer)
        buffer = glMapBuffer(GL_UNIFORM_BUFFER, GL_WRITE_ONLY)

        for uniform in self.uniforms.values():
            value = uniform.value
            if value is not None:
                uniform.update(value, buffer)

            # for arrays, update a list of individual values
            values = uniform.values
            if len(values) > 0:
                for index in values:
                    uniform.update_element(values[index], buffer, index)
                values.clear()

        glUnmapBuffer(GL_UNIFORM_BUFFER)
        glBindBuffer(GL_UNIFORM_BUFFER, 0)


class pyOpenGLUniformBlocks:
    def __init__(self):
        self.uniform_blocks = {}
        self.uniforms = {}

    def add(self, program, vertex, fragment):
        # list the uniforms block
        ub = glGetProgramiv(program, GL_ACTIVE_UNIFORM_BLOCKS)

        for index in range(ub):
            length = arrays.GLintArray.zeros((1,))
            glGetActiveUniformBlockiv(program, index, GL_UNIFORM_BLOCK_NAME_LENGTH, length)

            name = ctypes.create_string_buffer(int(length))
            glGetActiveUniformBlockName(program, index, length, None, name)
            name = name.value[:int(length)].decode("utf-8")

            if name not in self.uniform_blocks:
                uniform_block = pyOpenGLUniformBlock(program, name, index)
                uniform_block.bind(program)
                uniform_block.create()

                self.uniform_blocks[name] = uniform_block

                for uniform in uniform_block.uniforms.values():
                    self.uniforms[uniform.name] = uniform
            else:
                uniform_block = self.uniform_blocks[name]
                uniform_block.bind(program)

    def uploaded(self, name):
        if name in self.uniforms:
            return self.uniforms[name].uploaded

        return True

    def set_value(self, uniform, value):
        if uniform in self.uniforms:
            self.uniforms[uniform].value = value

    def set_array_value(self, uniform, element, value):
        if uniform in self.uniforms:
            self.uniforms[uniform].values[element] = value

    def upload(self):
        for block in self.uniform_blocks.values():
            block.upload()

    def update(self):
        for block in self.uniform_blocks.values():
            block.update()
