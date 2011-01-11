from model import *
from loader import *
from cubemap import *

class Scene(object):
    def __init__(self):
        self.models = []
        self.textures = Texture_Atlas()
        self.lights = Light_Atlas()
        self.cam = Cam()
        self.cubemap = None
        self.active_program = None
        self.time = 0.
        

    def load3dsModel(self,filename):
        model = load3ds(filename)
        if model != None:
            self.models.append(model)
            return len(self.models) - 1
        return None
    def loadObjModel(self,filename):
        model = loadObj(filename)
        if model != None:
            self.models.append(model)
            return len(self.models) - 1 
        return None

    def loadModelTextures(self):
        for model in self.models:
            loadTexture(model,self.textures)
        if self.cubemap != None:
            tex_map = self.cubemap.texture
            if tex_map.name not in self.textures.samplersCM:
                tex = Model_Cubemap_Texture()
                tex.set_texture_files(tex_map.xp,tex_map.xn,tex_map.yp,
                                 tex_map.yn,tex_map.zp,tex_map.zn)
                tex.load()
                self.textures.samplersCM[tex_map.name] = tex

        def_cm_tex = Model_Cubemap_Texture()
        def_cm_tex.load_default()
        self.textures.samplersCM['default'] = def_cm_tex

    def loadTexture2d(self,tex_name):
        if tex_name in self.textures.samplers2d: return
        tex = Model_Texture()
        tex.set_texture_file(tex_name)
        tex.load()
        print 'Loaded texture [' + tex_name + ']'
        self.textures.samplers2d[tex_name] = tex

    def loadTextureCM(self,xp,xn,yp,yn,zp,zn):
        if xp in self.textures.samplersCM: return
        tex = Model_Cubemap_Texture()
        tex.set_texture_files(xp,xn,yp,yn,zp,zn)
        tex.load()
        print 'Loaded texture [' + tex.name + ']'
        self.textures.samplersCM[tex.name] = tex

    def initCubemap(self,xp,xn,yp,yn,zp,zn):
        self.cubemap = Cubemap()
        if not self.cubemap.init_shaders(debug = True):
            return False
        return self.cubemap.set_textures(xp,xn,yp,yn,zp,zn)


class Screen(object):
    def __init__(self):
        self.size = (0,0)
        self.walltime = 0


class Texture_Atlas():
    def __init__(self):
        self.samplers2d = dict()
        self.samplersCM = dict()

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
        return self.spots[-0]

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
            
            
