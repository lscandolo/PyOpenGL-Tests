import OpenGL
OpenGL.ERROR_ON_COPY = True
from OpenGL.GL import *

from OpenGL.GL.framebufferobjects import glGenerateMipmap
from OpenGL.GL.ARB.vertex_program import *
import Image
import ImageOps
from cgkit.sl import radians

numpy = __import__("numpy")
import cgkit
from cgkit.all import *
from cgkit.cgtypes import *

def vbo_offset(offset):
    return ctypes.c_void_p(offset * 4)

class Model(object):
    def __init__(self):
        self.props = Model_Props()
        self.program = None
        self.name = None

    def transf(self):
        return self.props.transf()

class Model_Set(Model):
    def __init__(self):
        super(Model_Set,self).__init__()
        self.models = []

class Model_Object(Model):
    def __init__(self):
        super(Model_Object,self).__init__()
        self.material = Model_Material()
        self.attributes = dict()
        self.elements = Model_Elements()

    def load_attribute(self, name, vals, elem_len):
        new_attribute = Model_Attribute()
        new_attribute.name = name
        new_attribute.load(vals)
        new_attribute.elem_len = elem_len
        self.attributes[name] = new_attribute
        
    def load_attribute(self, attr):
        self.attributes[attr.name] = attr
        
    def delete_data(self):
        for attribute in attributes:
            attribute.delete()

    def set_buffers(self, program):
        if len(self.attributes) == 0:
            print "Error: No info setup in model [" + self.name + "] before calling set_buffers"
            return False
        for (name,attr) in self.attributes.items():
            location = glGetAttribLocation(program, name)
            if location != -1:
                glBindBuffer(GL_ARRAY_BUFFER,attr.buffer)
                glEnableVertexAttribArray(location)
                glVertexAttribPointerARB(location,attr.elem_len,GL_FLOAT,GL_FALSE,0,vbo_offset(0))
        glBindBuffer(GL_ARRAY_BUFFER,0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,self.elements.buffer)
        return True

class Model_Props:
    def __init__(self):
        self.has_normals = False
        self.has_tex_coords = False
        self.pos = vec3(0,0,0)
        self.ori = quat(1,0,0,0)
        self.scale = vec3(1,1,1)
    def transf(self):
        rot = self.ori.toMat4()
        scale = mat4.scaling(self.scale)
        return   mat4.translation(self.pos) * rot * scale
        # rM = mat4.rotation(self.rpy[0], (0,0,1))
        # rP = mat4.rotation(self.rpy[1],(1,0,0))
        # rY = mat4.rotation(self.rpy[2],(0,1,0))
        # scale = mat4.scaling(self.scale)
        # return mat4.translation(self.pos) * (rM * rP * rY) * scale

        
class  Model_Attribute(object):
    def __init__(self,name):
        self.name = name
        self.buffer = 0
        self.offset = 0
        self.usage = GL_STATIC_DRAW
        self.elem_count = 0
        self.elem_len = 0
    def create_buffer(self):
        self.buffer = glGenBuffers(1)
    def load(self,vals):
        if self.buffer == 0:
            self.buffer = glGenBuffers(1)
        elem_count = len(vals)
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer)
        glBufferData(GL_ARRAY_BUFFER, vals, self.usage)
        glBindBuffer(GL_ARRAY_BUFFER,0)

    def delete_buffer(self):
        glDeleteBuffers([self.buffer])

class Model_Elements(Model_Attribute):
    def __init__(self):
        super(Model_Elements,self).__init__("Elements")
    def load(self,vals):
        if self.buffer == 0:
            self.buffer = glGenBuffers(1)
        self.elem_count = len(vals)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.buffer)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, vals, self.usage)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,0)

class Model_Material():
    def __init__(self):
        self.ambient = vec4(0, 0, 0, 0)
        self.diffuse = vec4(1.0, 1.0, 1.0, 1.0)
        self.specular = vec4(1.0, 1.0, 1.0, 1.0)
        self.shininess = 1.0
        self.shin_strength = 0
        self.use_blur = 0
        self.transparency = 0.0
        self.falloff = 0
        self.additive = 0
        self.use_falloff = 0
        self.self_illum = False
        self.self_ilpct = 0.0
        self.shading = 0
        self.soften = 0
        self.face_map = 0
        self.two_sided = 0
        self.map_decal = 0
        self.use_wire = 0,
        self.use_wire_abs = 0
        self.wire_size = 0
        self.density = 0
        self.texture1_map = Model_Material_Texture()
        self.texture2_map = Model_Material_Texture()
        self.opacity_map = Model_Material_Texture()
        self.bump_map = Model_Material_Texture()
        self.specular_map = Model_Material_Texture()
        self.shininess_map = Model_Material_Texture()
        self.self_illum_map = Model_Material_Texture()
        self.reflection_map = Model_Material_Texture()
        self.bump_size = 1.0

    def texture_names(self):
        names = []
        for a in [self.texture1_map,self.texture2_map,
                  self.opacity_map,self.bump_map,
                  self.specular_map,self.shininess_map,
                  self.self_illum_map,self.reflection_map]:
            if a.set:
                names.append(a.name)
                
        return names

class Model_Material_Texture():
    def __init__(self):
        self.set = False
        self.name = ''
        self.scale = (1,1)
        self.offset = (0,0)
        self.rotation = 0.
        self.percent = 1.

    def load3dsTextureMap(self,tm):
        if tm != None:
            self.name = tm.name
            self.set = True
            self.scale = tm.scale
            self.offset = tm.offset
            self.rotation = radians(tm.rotation)
            self.percent = tm.percent

class Model_Texture():
    def __init__(self):
        self.location = 0
        self.tex_file = None
        self.mag_filter = GL_LINEAR
        self.min_filter = GL_LINEAR_MIPMAP_LINEAR
        self.create_mipmap = True
        self.mag_filter = GL_LINEAR
        self.min_filter = GL_LINEAR_MIPMAP_LINEAR
        self.wrap_s = GL_REPEAT
        self.wrap_t = GL_REPEAT

    def set_texture_file(self,f,debug = False):
        self.tex_file = f

    def load(self):
        if self.tex_file == None:
            print "Error: No texture file image set"
            return False

        self.location = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D,self.location)

        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S,self.wrap_s)
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T,self.wrap_t)
        glTexParameteri( GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,self.mag_filter)
        glTexParameteri( GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,self.min_filter)

        try:
            im = ImageOps.flip(Image.open(self.tex_file).convert('RGB'))
        except IOError:
            print "Error opening file", tex_file
            exit(-1)

        texdata = im.getdata()
        buf = numpy.array(texdata,dtype='uint8',order='C')
        buf_shape = (im.size[0],im.size[1],3)
        data = numpy.reshape(buf,buf_shape,order='C')
        # data = ndarray(shape=buf_shape, buffer=buf,dtype="uint8",order='C')

        # valiter = texdata.__iter__()
        # for i in range(0,buf_shape[0]):
        #     for j in range(0,buf_shape[1]):
        #         for k in range(0,buf_shape[2]):
        #             try:
        #                 data.itemset((i,j,k),valiter.next())
        #             except StopIteration:
        #                 print '(i,j,k)', i,j,k
        #                 break
        
        glTexImage2Dub(GL_TEXTURE_2D, 0, 3, 0, GL_RGB, data)
        
        if self.create_mipmap:
            glGenerateMipmap(GL_TEXTURE_2D)

        return True

    def bind(self):
        glBindTexture(GL_TEXTURE_2D, self.location)

class Model_Cubemap_Texture():
    def __init__(self):
        self.location = 0
        self.tex_xpos = None
        self.tex_ypos = None
        self.tex_zpos = None
        self.tex_xneg = None
        self.tex_yneg = None
        self.tex_zneg = None
        self.mag_filter = GL_LINEAR
        self.min_filter = GL_LINEAR_MIPMAP_LINEAR
        self.create_mipmaps = True

    def load(self,debug = False):
        # if self.program == None:
        #     print "No program defined"
        #     return False
        
        # glUseProgram(self.program)
        # glActiveTexture(self.active_texture)

        self.location = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP,self.location)

        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER,self.mag_filter)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER,self.min_filter)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE);
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE);
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R,GL_CLAMP_TO_EDGE);

        if self.tex_xpos == None or \
           self.tex_ypos == None or \
           self.tex_zpos == None or \
           self.tex_xneg == None or \
           self.tex_yneg == None or \
           self.tex_zneg == None:
            print 'Error: Cubemap textures not set' 
            return False
        
        try:
            Image.open(self.tex_xpos).verify()
            Image.open(self.tex_ypos).verify()
            Image.open(self.tex_zpos).verify()
            Image.open(self.tex_xneg).verify()
            Image.open(self.tex_yneg).verify()
            Image.open(self.tex_zneg).verify()
        except a:
            print 'Error loading cubemap images', a
            return False

        xp_img = Image.open(self.tex_xpos).convert('RGB')
        yp_img = Image.open(self.tex_ypos).convert('RGB')
        zp_img = Image.open(self.tex_zpos).convert('RGB')
        xn_img = Image.open(self.tex_xneg).convert('RGB')
        yn_img = Image.open(self.tex_yneg).convert('RGB')
        zn_img = Image.open(self.tex_zneg).convert('RGB')

        imgs = [xp_img,xn_img,yp_img,yn_img,zp_img,zn_img]
        targets =  [GL_TEXTURE_CUBE_MAP_POSITIVE_X,GL_TEXTURE_CUBE_MAP_NEGATIVE_X]
        targets += [GL_TEXTURE_CUBE_MAP_POSITIVE_Y,GL_TEXTURE_CUBE_MAP_NEGATIVE_Y]
        targets += [GL_TEXTURE_CUBE_MAP_POSITIVE_Z,GL_TEXTURE_CUBE_MAP_NEGATIVE_Z]
        
        for img,trg in zip(imgs,targets):

            texdata = img.getdata()
            buf = numpy.array(texdata,dtype='uint8',order='C')
            buf_shape = (img.size[0],img.size[1],3)
            data = numpy.reshape(buf,buf_shape,order='C')
            glTexImage2Dub(trg, 0, 3, 0, GL_RGB, data)

            if debug:
                print "Loaded", trg, "Size:", img.size

        if self.create_mipmaps:
            glGenerateMipmap(GL_TEXTURE_CUBE_MAP)
            if debug: print "Generated cubemap mipmaps"
    
        return True

    def set_texture_files(self,xp,xn,yp,yn,zp,zn,debug = False):
        self.tex_xpos = xp
        self.tex_ypos = yp
        self.tex_zpos = zp
        self.tex_xneg = xn
        self.tex_yneg = yn
        self.tex_zneg = zn

    def bind(self):
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.location)

class Cam:
    def __init__(self):
        self.pos = vec3(0.,0.,1.)
        self.ori = quat(1,0,0,0)
        self.inclination = 0.
        self.azimuthal = 0.
        self.projTransf = mat4().perspective(50.,5./4.,0.1,100)

    def delta(self, az, inc):
        
        self.inclination += inc
        self.azimuthal += az

        self.inclination = min( numpy.pi/2 , self.inclination)
        self.inclination = max(-numpy.pi/2, self.inclination)

        self.azimuthal = self.azimuthal%(numpy.pi * 2)
                                
        az_rot = quat(self.azimuthal, vec3(0,1,0))
        inc_rot = quat(self.inclination, vec3(1,0,0))
        
        self.ori = az_rot * inc_rot

    def transf(self):
        rot = self.ori.conjugate().toMat4()
        trans = mat4.translation([-self.pos.x, -self.pos.y, -self.pos.z])
        return rot * trans

        # rM = mat4.rotation(self.rpy[0],(0.,0.,1.))
        # pM = mat4.rotation(self.rpy[1],(-1.,0.,0.))
        # yM = mat4.rotation(self.rpy[2],(0.,1.,0.))
        # return  rM * pM * yM * tM

    def rotTransf(self):
        return self.ori.conjugate().toMat4()

    def rot(self):
        return self.ori.toMat3()
        # rM = mat4.rotation(self.rpy[0], (0.,0.,-1.))
        # pM = mat4.rotation(self.rpy[1],(1.,0.,0.))
        # yM = mat4.rotation(self.rpy[2],(0.,-1.,0.))
        # return  yM * pM * rM

