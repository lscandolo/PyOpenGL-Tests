import loader
import OpenGL

OpenGL.FORWARD_COMPATIBLE_ONLY = True #Working with core profile only

from OpenGL.GL import * #gl* functions
from OpenGL.GLU import * #glu* functions
from OpenGL.GLUT import* #glut* functions
from OpenGL.GLX import* #glx* functions

from OpenGL.GL.EXT import *
from OpenGL.GL.ARB import *

from OpenGL.GL.ARB.vertex_program import *

from OpenGL.GL.ARB.vertex_buffer_object import * #vertex buffer objects

import numpy,ctypes

from OpenGL.arrays import vbo


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH | GLUT_MULTISAMPLE)
    glutInitWindowPosition(100,100)
    glutInitWindowSize(500,500)
    glutCreateWindow("TRY")

    if loader.loadObj("minimal.vert") == 0:
        print "Not loaded"
    else:
        print "loaded"
       

    init()
    initShaders()
    buffers = initBuffers()

    glutDisplayFunc(lambda : drawScene(buffers))
    glutIdleFunc(lambda : drawScene(buffers))

    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyPressed)

    glutMainLoop()

def init():
    glClearColor(0.0,0.0,0.0,0.0)
    glClearDepth(1.0)

def initBuffers():
    buffers = glGenBuffers(2)

    pos_data = [[1.0,0.0,0.0],[0.0,1.0,0.0],[0.0,0.0,0.0]]
    color_data    = [[1.0,0.0,0.0],[0.0,1.0,0.0],[0.0,0.0,1.0]]

    vertex_data = numpy.array(pos_data + color_data,dtype='float32')

    # for i in range(0,len(pos_data)):
    #     vertex_data += pos_data[i] + color_data[i]
    # print vertex_data


    glBindBuffer(GL_ARRAY_BUFFER, buffers[0])
    glBufferData(GL_ARRAY_BUFFER, numpy.array(vertex_data), GL_STATIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER,0)

    element_data = numpy.array([0,1,2])

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, buffers[1])
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, element_data, GL_STATIC_DRAW)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,0)

    return buffers

def drawScene(buffers):

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnableVertexAttribArray(0)
    glEnableVertexAttribArray(1)

    vertex_buffer = buffers[0]
    element_buffer = buffers[1]

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,element_buffer)

    glBindBuffer(GL_ARRAY_BUFFER,vertex_buffer)

    glVertexAttribPointerARB(0,3,GL_FLOAT,GL_FALSE,3,vbo_offset(0))
    glVertexAttribPointerARB(1,3,GL_FLOAT,GL_FALSE,3,vbo_offset(9))

    glDrawElements(GL_TRIANGLES,3,GL_UNSIGNED_INT,None)

    glBindBuffer(GL_ARRAY_BUFFER,0)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,0)

    if (glGetError() != GL_NO_ERROR):
        print "ERROR en DrawElements"

    glutSwapBuffers()

def vbo_offset(offset):
    return ctypes.c_void_p(offset * 4)

def reshape(w,h):
    glViewport(0,0,w,h)

def keyPressed(key,x,y):
    if key == '\033':
        sys.exit(1)

def initShaders():
    v_shader = glCreateShader(GL_VERTEX_SHADER)
    v_shader_source = [open("minimal.vert",'r').read()]
    glShaderSource(v_shader,v_shader_source)

    f_shader = glCreateShader(GL_FRAGMENT_SHADER)
    f_shader_source = [open("minimal.frag",'r').read()]
    glShaderSource(f_shader,f_shader_source)

    program = glCreateProgram()
    glAttachShader(program,v_shader)
    glAttachShader(program,f_shader)

    glCompileShader(v_shader)
    glCompileShader(f_shader)
    
    print glGetShaderInfoLog(v_shader)
    print glGetShaderInfoLog(f_shader)

    glBindAttribLocation(program,0,"in_Position")
    glBindAttribLocation(program,1,"in_Color")

    glLinkProgram(program)
    glValidateProgram(program)
    
    print glGetProgramInfoLog(program)

    glUseProgram(program)

if __name__ == '__main__': main()
