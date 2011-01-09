from model import *
from loader import *
from cubemap import *

class Scene(object):
    def __init__(self):
        self.models = []
        self.textures = Texture_Atlas()
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
