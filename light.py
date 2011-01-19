from cgkit.all import vec3
from OpenGL.GL import glUniform3f, glUniform1f, glUniform1i, glGetUniformLocation

class Model_Ambient_Light(object):
    def __init__(self):
        self.intensity = 0.5
        self.color = vec3(1.0,1.0,1.0)
        self.uniform = 'ambient_light'
        
class Model_Spot_Light(object):
    def __init__(self,uniform):
        self.uniform = uniform
        self.intensity = 1
        self.color = vec3(1.0,1.0,1.0)
        self.pos = vec3(0,0,0)
        self.dir = vec3(0,0,1)
        self.aperture = 1 #half angle of aperture
        self.reach   = 1 #maximum reach
        self.ang_dimming = 2 #dimming factor as it faces away from a normal
        self.dist_dimming = 0.5 #linear dimming factor as the object is further
        self.specular_exponent = 32

class Light_Atlas():
    def __init__(self):
        self.ambient = Model_Ambient_Light()
        self.spots = []
        self.dirs  = []

    def new_spot_light(self):
        if len(self.spots) > 9:
            return None

        uniform = 'spot_light[' + str(len(self.spots)) + ']'
        light = Model_Spot_Light(uniform)
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
            
            
