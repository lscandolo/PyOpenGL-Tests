from cgkit.all import vec3,quat
# from OpenGL.GL import glUniform3f, glUniform1f, glUniform1i, glGetUniformLocation
# from OpenGL.GL import  glActiveTexture, GL_TEXTURE0, glBindTexture, GL_TEXTURE_2D,glTexParameteri
from OpenGL.GL import *
from model import Model_Shadow_Texture,Cam
from math import acos

class Model_Ambient_Light(object):
    def __init__(self):
        self.intensity = 0.5
        self.color = vec3(1.0,1.0,1.0)
        self.uniform = 'ambient_light'
        
class Model_Spot_Light(object):
    def __init__(self,uniform):
        self.uniform = uniform
        self.intensity = 1.
        self.color = vec3(1.,1.,1.)
        self.pos = vec3(0.,0.,0.)
        self.dir = vec3(0.,0.,1.)
        self.aperture = 1. #half angle of aperture
        self.reach   = 1. #maximum reach
        self.ang_dimming = 2. #dimming factor as it faces away from a normal
        self.dist_dimming = 0.5 #linear dimming factor as the object is further
        self.specular_exponent = 32
        self.generates_shadow_map = True
        
    def cam(self):
        cam = Cam()
        cam.pos = self.pos
            
        if self.dir.normalize() == vec3(0.,0.,1.):
            rot_axis = vec3(1.,0.,0.)
            cos_alpha = vec3(0.,self.dir[1],self.dir[2]).normalize() * vec3(1.,0.,0.)
            angle = acos(cos_alpha)
        else:
            rot_axis = self.dir.cross(vec3(0.,0.,1.)).normalize()
            cos_alpha = vec3(self.dir[0],self.dir[1],0.).normalize() * self.dir.normalize()
            angle = acos(cos_alpha)

        cam.ori.fromAngleAxis(angle,rot_axis)
        return cam

class Light_Atlas():
    def __init__(self):
        self.ambient = Model_Ambient_Light()
        self.spots = []
        self.dirs  = []

    def new_spot_light(self,generate_shadow_map = True, shadow_resolution = 500):
        if len(self.spots) > 9:
            return None

        uniform = 'spot_light[' + str(len(self.spots)) + ']'
        light = Model_Spot_Light(uniform)
        light.generate_shadow_map = generate_shadow_map
        if generate_shadow_map:
            light.shadow_texture = Model_Shadow_Texture()
            light.shadow_texture.allocate(shadow_resolution)

        self.spots.append(light)
        return self.spots[-1] # Last element

    def setup(self,scene):
        program = scene.active_program

        loc = glGetUniformLocation(program,self.ambient.uniform + '.color')
        glUniform3f(loc,
                    self.ambient.color[0],
                    self.ambient.color[1],
                    self.ambient.color[2])

        loc = glGetUniformLocation(program,self.ambient.uniform + '.intensity')
        glUniform1f(loc,self.ambient.intensity)
        
        loc = glGetUniformLocation(program,'spot_light_count')
        glUniform1i(loc,len(self.spots));
        print 'spot_light_count(loc' + str(loc) + ') =', len(self.spots)

        for l in self.spots:
            loc = glGetUniformLocation(program,l.uniform + '.color')
            glUniform3f(loc,l.color[0],l.color[1],l.color[2])

            loc = glGetUniformLocation(program,l.uniform + '.intensity')
            glUniform1f(loc,l.intensity)

            loc = glGetUniformLocation(program,l.uniform + '.aperture')
            glUniform1f(loc,l.aperture)

            loc = glGetUniformLocation(program,l.uniform + '.reach')
            glUniform1f(loc,l.reach)

            loc = glGetUniformLocation(program,l.uniform + '.ang_dimming')
            glUniform1f(loc,l.ang_dimming)

            loc = glGetUniformLocation(program,l.uniform + '.dist_dimming')
            glUniform1f(loc,l.dist_dimming)

            loc = glGetUniformLocation(program,l.uniform + '.specular_exponent')
            glUniform1i(loc,l.specular_exponent)

            loc = glGetUniformLocation(program,l.uniform + '.position')
            glUniform3f(loc,l.pos[0],l.pos[1],l.pos[2])

            loc = glGetUniformLocation(program,l.uniform + '.direction')
            glUniform3f(loc,l.dir[0],l.dir[1],l.dir[2])

            loc = glGetUniformLocation(program,l.uniform + '.has_shadow_map')
            if l.generates_shadow_map:
                glUniform1i(loc,1)
            else:
                glUniform1i(loc,0)
                
            glActiveTexture(GL_TEXTURE0+scene.frame_textures)
            glBindTexture(GL_TEXTURE_2D, l.shadow_texture.location)

            glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,GL_NEAREST)
            glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,GL_NEAREST)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_DEPTH_TEXTURE_MODE, GL_LUMINANCE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_FUNC, GL_LEQUAL)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_MODE, 
                            GL_COMPARE_R_TO_TEXTURE)

            tex_loc = glGetUniformLocation(program,l.uniform + '.shadow_map')
            glUniform1i(tex_loc,scene.frame_textures)
            print l.uniform + '.shadow_map uniform location:', tex_loc
            print l.uniform + '.shadow_map TIU number:', scene.frame_textures
            print l.uniform + '.shadow_map texture location:', l.shadow_texture.location
            glActiveTexture(GL_TEXTURE0) #Probably useless
            scene.frame_textures += 1            
