"""
Shortcut to access OPenGL feature'faster'
pyOpenGL
"""
from OpenGL.GL import *
glVertexAttribPointer = glVertexAttribPointer.wrappedOperation
glUniformMatrix4fv = glUniformMatrix4fv.wrappedOperation
glBufferData = glBufferData.wrappedOperation
glBufferSubData = glBufferSubData.wrappedOperation
