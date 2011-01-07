from model import *
from loader import *
from cubemap import *

class Scene(object):
    def __init__(self):
        self.models = []
        self.textures = dict()
        self.cam = Cam()
        self.cubemap = None
        self.active_program = None

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
    def loadModelsTextures(self):
        for model in self.models:
            loadTexture(model,self.textures)
    def loadTexture(self,tex_name):
        if tex_name in self.textures: return
        tex = Model_Texture()
        tex.set_texture_file(tex_name)
        tex.load()
        print 'Loaded texture [' + tex_name + ']'
        self.textures[tex_name] = tex

    def loadCubemapTextures(self,xp,xn,yp,yn,zp,zn):
        self.cubemap = Cubemap()
        if not self.cubemap.init_shaders(debug = True):
            return False
        return self.cubemap.load_textures(xp,xn,yp,yn,zp,zn)


class Screen(object):
    def __init__(self):
        self.size = (0,0)
        self.walltime = 0
