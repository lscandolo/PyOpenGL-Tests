import scene
import numpy
from OpenGL.GL.framebufferobjects import *
from OpenGL.GL import *

class ShadowFB(object):
    def __init__(self):
        self.fb = 0
        self.rb = 0
        self.resolution = 0

    def allocate(self, resolution = 2048):
        self.fb = glGenFramebuffers(1)
        self.rb = glGenRenderbuffers(1)
        self.resolution = resolution

        #Don't write color
        glBindFramebuffer(GL_FRAMEBUFFER, self.fb)
        glBindRenderbuffer(GL_RENDERBUFFER, self.rb)

        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT32,resolution,resolution)

        bdata = numpy.array([GL_NONE],dtype='uint32')
        glDrawBuffers(bdata)

        self.vshader = glCreateShader(GL_VERTEX_SHADER)
        self.fshader = glCreateShader(GL_FRAGMENT_SHADER)
        v_shader_source = [\
        """
        #version 330
        uniform mat4 in_Modelview;  
        uniform mat4 in_Projection; 
        in  vec3 in_Position;       
        void main(void){            
        gl_Position = in_Projection * in_Modelview * vec4(in_Position, 1.0);}
        """]
        f_shader_source = [\
        """
        #version 330     
        uniform mat4 in_Modelview;  
        uniform mat4 in_Projection; 
        void main(void){ 
        gl_FragDepth = gl_FragCoord.z;
        }
        """]
        glShaderSource(self.vshader,v_shader_source)
        glShaderSource(self.fshader,f_shader_source)
        self.program = glCreateProgram()
        glAttachShader(self.program,self.vshader)
        glAttachShader(self.program,self.fshader)
        glCompileShader(self.vshader)
        glCompileShader(self.fshader)
        glLinkProgram(self.program)
        # glValidateProgram(self.program)
        # print "/////////////////Shadow shaders status:"
        # print glGetShaderInfoLog(self.vshader)
        # print glGetShaderInfoLog(self.fshader)
        # print glGetProgramInfoLog(self.program)
        # print "///////////////////////////////////////"
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def setup(self,texture):
        glClearDepth(1.)

        #Depth functions
        glClear(GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glDepthMask( GL_TRUE );

        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,GL_NEAREST)
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_DEPTH_TEXTURE_MODE, GL_INTENSITY) # GL_LUMINANCE
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_FUNC, GL_GEQUAL)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_MODE, 
                        GL_COMPARE_R_TO_TEXTURE)

        glBindFramebuffer(GL_FRAMEBUFFER, self.fb)
        glBindRenderbuffer(GL_RENDERBUFFER, self.rb)
        glBindTexture(GL_TEXTURE_2D, texture)

        # glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT,
        #                           GL_RENDERBUFFER,self.rb)
        glFramebufferTexture2D(GL_DRAW_FRAMEBUFFER,GL_DEPTH_ATTACHMENT,
                               GL_TEXTURE_2D,texture,0)

        #Color draw and read buffers are empty
        # bdata = numpy.array([GL_NONE],dtype='uint32')
        # glDrawBuffers(bdata)
        # glReadBuffer(GL_NONE)

        if not checkBufferStatus(self.fb):
            return False

        return True

    def unbind(self):
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        
def checkBufferStatus(fb):
    status = glCheckFramebufferStatus(GL_DRAW_FRAMEBUFFER)
    if status == GL_FRAMEBUFFER_COMPLETE:
        return True
    elif status == GL_FRAMEBUFFER_UNDEFINED:
        print 'GL_FRAMEBUFFER_UNDEFINED'
    elif status == GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT:
        print 'GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT'
    elif status == GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT:
        print 'GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT'
    elif status == GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER:
        print 'GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER'
    elif status == GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER:
        print 'GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER'
    elif status == GL_FRAMEBUFFER_UNSUPPORTED:
        print 'GL_FRAMEBUFFER_UNSUPPORTED'
    elif status == GL_FRAMEBUFFER_INCOMPLETE_MULTISAMPLE:
        print 'GL_FRAMEBUFFER_INCOMPLETE_MULTISAMPLE'
    else: # status == GL_FRAMEBUFFER_INCOMPLETE_LAYER_TARGETS
        print 'GL_FRAMEBUFFER_INCOMPLETE_LAYER_TARGETS'
    return False
    
