import OpenGL
OpenGL.FORWARD_COMPATIBLE_ONLY = True 
from OpenGL.GL import *

from OpenGL.GL.ARB.vertex_program import glVertexAttribPointerARB

import math
import numpy
from model import Model_Cube_Map

class Cubemap:
    def __init__(self,debug = False,clockwise = True):
        self.program = None
        self.texture = None
        self.vertex_shader = None
        self.fragment_shader = None
        # self.active_texture = GL_TEXTURE0
        self.cubemap_sampler_name = None
        self.pos_attr_name = None
        self.rot_transf_name = None

        self.cubemap_pos_buf,self.cubemap_elem_buf = glGenBuffers(2)
        glBindBuffer(GL_ARRAY_BUFFER,self.cubemap_pos_buf)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,self.cubemap_elem_buf)
        
        cubemap_pos = numpy.array(cubemapVals(20,clockwise),dtype='float32')
        cubemap_elems = numpy.array(range(0,36),dtype='int32')

        #Yes, yes, this is not optimal, but I'm not going to sacrifice 
        #simplicity for a few hundred bytes
        
        glBufferData(GL_ARRAY_BUFFER,cubemap_pos, GL_STATIC_DRAW)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER,cubemap_elems, GL_STATIC_DRAW)
        
        glBindBuffer(GL_ARRAY_BUFFER,0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,0)
    
        if debug:
            print "Cubemap creation succesful"

    def init_shaders(self,debug = False):
        if self.vertex_shader == None or self.fragment_shader == None:
            v_shader_source = [\
            """
            #version 330
            in vec4 pos;
            uniform mat4 mvpTransf;
            varying vec3 ex_texcoord;
            void main(void){
            ex_texcoord = pos.xyz;
            gl_Position = mvpTransf * pos;}
            """]
            f_shader_source = [\
            """
            #version 330
            out vec4 fragColor;
            uniform samplerCube cubemap;
            varying vec3 ex_texcoord;
            void main(void){fragColor = texture(cubemap, ex_texcoord);}
            """]

            self.cubemap_sampler_name = 'cubemap'
            self.pos_attr_name = 'pos'
            self.rot_transf_name = 'mvpTransf'

        else:
            v_shader_source = [open(self.vertex_shader,'r').read()]
            f_shader_source = [open(self.fragment_shader,'r').read()]

        self.vertex_shader_id = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(self.vertex_shader_id,v_shader_source)
        
        self.fragment_shader_id = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(self.fragment_shader_id,f_shader_source)
        
        program = glCreateProgram()
        glAttachShader(program,self.vertex_shader_id)
        glAttachShader(program,self.fragment_shader_id)
        
        glCompileShader(self.vertex_shader_id)
        glCompileShader(self.fragment_shader_id)
        
        glLinkProgram(program)
        glValidateProgram(program)

        print "////////////////Cubemap shaders status:"
        print glGetShaderInfoLog(self.vertex_shader_id)
        print glGetShaderInfoLog(self.fragment_shader_id)
        print glGetProgramInfoLog(program)
        print "///////////////////////////////////////"
        self.program = program
        return True

    def set_textures(self,xp,xn,yp,yn,zp,zn,debug = False):
        if self.program == None:
            print 'No program defined'
            return False
        self.texture = Model_Cube_Map('cubemap')
        self.texture.set_textures(xp,xn,yp,yn,zp,zn)

    def bindTexture(self,tex):
        glUseProgram(self.program)
        loc = glGetUniformLocation(self.program,'cubemap')
        tex.bind()
        glUniform1i(loc,0)

    def use_program(self):
        glUseProgram(self.program)

    def draw(self,rotTransf):

        if self.cubemap_sampler_name == None:
            print "Error: No cubemap sampler name defined"
            return False

        # glActiveTexture(self.active_texture)

        glBindBuffer(GL_ARRAY_BUFFER,self.cubemap_pos_buf)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,self.cubemap_elem_buf)

        # glBindTexture(GL_TEXTURE_CUBE_MAP,self.texture.location)

        # cubemap_sampler = glGetUniformLocation(self.program,
        #                                        self.cubemap_sampler_name)
        # glUniform1i(cubemap_sampler,0)

        pos_attr_loc = glGetAttribLocation(self.program,self.pos_attr_name)
        glEnableVertexAttribArray(pos_attr_loc)
        glVertexAttribPointerARB(pos_attr_loc,3,GL_FLOAT,GL_FALSE,0,vbo_offset(0))

        location = glGetUniformLocation(self.program,self.rot_transf_name)
        glUniformMatrix4fv(location, 1, GL_FALSE, rotTransf)


        glDrawElements(GL_TRIANGLES,36,GL_UNSIGNED_INT,None)

        if glGetError() != GL_NO_ERROR:
            print "Error: " + str(glGetError())
            
        glBindBuffer(GL_ARRAY_BUFFER,0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,0)


def cubemapVals(radius, clockwise = True):

    a = math.sqrt(3 * (radius**2))
        
    #ZPOS
    pos =  [(-a,a,a),(a,a,a),(-a,-a,a)]
    pos += [(-a,-a,a),(a,a,a),(a,-a,a)]
    #ZNEG
    pos += [(a,a,-a),(-a,a,-a),(-a,-a,-a)]
    pos += [(a,a,-a),(-a,-a,-a),(a,-a,-a)]
    #XNEG
    pos += [(-a,a,-a),(-a,a,a),(-a,-a,-a)]
    pos += [(-a,-a,-a),(-a,a,a),(-a,-a,a)]
    #XPOS
    pos += [(a,a,a),(a,a,-a),(a,-a,-a)]
    pos += [(a,a,a),(a,-a,-a),(a,-a,a)]
    #YPOS
    pos += [(-a,a,a),(-a,a,-a),(a,a,a)]
    pos += [(a,a,a),(-a,a,-a),(a,a,-a)]
    #YNEG
    pos += [(-a,-a,-a),(-a,-a,a),(a,-a,a)]
    pos += [(-a,-a,-a),(a,-a,a),(a,-a,-a)]

    if not clockwise:
        for i in range(0,36,3):
            vn = pos[i]
            pos[i] = pos[i+1]
            pos[i+1] = vn

    return pos

def vbo_offset(offset):
    return ctypes.c_void_p(offset * 4)



#For later use if I set a uniform type

        # for var,val in uniforms:
        #     shape = val.shape
        #     dtype = val.dtype
        #     location = glGetUniformLocation(self.program,var)

        #     if shape == (4,4) and dtype == 'float32':
        #         glUniformMatrix4fv(location, 1, GL_FALSE, val)
        #     elif shape == (4,4) and dtype == 'int32':
        #         glUniformMatrix4iv(location, 1, GL_FALSE, val)
        #     elif shape == (4,4) and dtype == 'uint32':
        #         glUniformMatrix4uv(location, 1, GL_FALSE, val)

        #     elif shape == (3,3) and dtype == 'float32':
        #         glUniformMatrix3fv(location, 1, GL_FALSE, val)
        #     elif shape == (3,3) and dtype == 'int32':
        #         glUniformMatrix3iv(location, 1, GL_FALSE, val)
        #     elif shape == (3,3) and dtype == 'uint32':
        #         glUniformMatrix3uv(location, 1, GL_FALSE, val)

        #     elif shape == (4) and dtype == 'float32':
        #         glUniform4fv(location, 1, GL_FALSE, val)
        #     elif shape == (4) and dtype == 'int32':
        #         glUniform4iv(location, 1, GL_FALSE, val)
        #     elif shape == (4) and dtype == 'uint32':
        #         glUniform4uv(location, 1, GL_FALSE, val)

        #     elif shape == (3) and dtype == 'float32':
        #         glUniform3fv(location, 1, GL_FALSE, val)
        #     elif shape == (3) and dtype == 'int32':
        #         glUniform3iv(location, 1, GL_FALSE, val)
        #     elif shape == (3) and dtype == 'uint32':
        #         glUniform3uv(location, 1, GL_FALSE, val)

        #     elif shape == (2) and dtype == 'float32':
        #         glUniform2fv(location, 1, GL_FALSE, val)
        #     elif shape == (2) and dtype == 'int32':
        #         glUniform2iv(location, 1, GL_FALSE, val)
        #     elif shape == (2) and dtype == 'uint32':
        #         glUniform2uv(location, 1, GL_FALSE, val)

        #     elif shape == (1) and dtype == 'float32':
        #         glUniform1fv(location, 1, GL_FALSE, val)
        #     elif shape == (1) and dtype == 'int32':
        #         glUniform1iv(location, 1, GL_FALSE, val)
        #     elif shape == (1) and dtype == 'uint32':
        #         glUniform1uv(location, 1, GL_FALSE, val)
