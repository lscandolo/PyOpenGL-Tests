import OpenGL
OpenGL.ERROR_ON_COPY = True
# OpenGL.ERROR_LOGGING = False
# OpenGL.ERROR_CHECKING = False

OpenGL.FORWARD_COMPATIBLE_ONLY = True #WORKING NOW WOOOHOO

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLX import *
from OpenGL.arrays import vbo
from OpenGL.arrays import *

from OpenGL.GL.framebufferobjects import *

from OpenGL.GL.ARB.vertex_program import *
from OpenGL.GL.ARB.vertex_buffer_object import *

from OpenGL.GL.EXT import *
from OpenGL.GL.ARB import *

import cgkit
import copy

from model import *
 
from cgkit.all import *
from cgkit.cgtypes import *

import numpy

from tangent import calculateTangents

def vbo_offset(offset):
    return ctypes.c_void_p(offset * 4)

def loadObj(filename, debug = False):
    try:
        content = open(filename, 'rb')
    except IOError:
        print "Error loading file: " + filename
        return

    obj = Model_Set()

    a_positions =  Model_Attribute('in_Position')
    a_normals =    Model_Attribute('in_Normal')
    a_tex_coords = Model_Attribute('in_TexCoord')
    a_tangents =   Model_Attribute('in_Tangent')

    elements = []

    lines = [line[0:-1] for line in iter(content)] 

    if (debug):
        print 'Model ' + filename + ' file contents:'
        for line in lines: print line
    
    vertex_count = 0
    for line in lines:
        words = line.split()
        if len(words) < 1: continue
        if words[0] == "v":
            vertex_count+=1

    print 'Vertices:', vertex_count

    arr_nor = numpy.zeros((vertex_count,3),dtype='float32')
    arr_pos = numpy.zeros((vertex_count,3),dtype='float32')
    arr_tex = numpy.zeros((vertex_count,2),dtype='float32')

    normals = []
    positions = []
    tex_coords = []

    element_count = 0
    for line in lines:
        words = line.split()
        if len(words) < 1: continue
            
        if words[0] == "v":
            x = float(words[1])
            y = float(words[2])
            z = float(words[3])
            positions.append((x,y,z))
        elif words[0] == "vn":
            x = float(words[1])
            y = float(words[2])
            z = float(words[3])
            normals.append((x,y,z))
        elif words[0] == "vt":
            s = float(words[1])
            t = float(words[2])
            tex_coords.append((s,t))
            # tex_coords.append((s%1.0,t%1.0))

    for line in lines:
        words = line.split()
        if len(words) < 1: continue


        if words[0] == "f":
            vals = map(lambda x: x.split('/'), words)
            x = int(vals[1][0]) - 1
            for i in range( 3, len(words) ):
                y = int(vals[i-1][0]) -1 
                z = int(vals[i][0]) -1 
                element_count += 1
                elements.append([x,y,z])
                
                if len(vals[1]) == 1:
                    for a in [x,y,z]:
                        arr_pos[a] = positions[a]
                        arr_tex[a] = tex_coords[a]
                        arr_nor[a] = normals[a]
                else:
                    vtx_a = vals[1]
                    vtx_b = vals[i-1]
                    vtx_c = vals[i]
                    pos_ = (int(vtx_a[0])-1,int(vtx_b[0])-1,int(vtx_c[0])-1)
                    tex_ = (int(vtx_a[1])-1,int(vtx_b[1])-1,int(vtx_c[1])-1)
                    nor_ = (int(vtx_a[2])-1,int(vtx_b[2])-1,int(vtx_c[2])-1)

                    for a in range(0,3):
                        arr_pos[pos_[a]] = positions[pos_[a]]
                        # if arr_tex[pos_[a]][0] == 0 and arr_tex[pos_[a]][1] == 0:
                        arr_tex[pos_[a]] = tex_coords[tex_[a]]
                        arr_nor[pos_[a]] = normals[nor_[a]]

                
        elif words[0] == "g":
            if len(words) > 1:
                print 'Loaded model [' + words[1] + ']'
            new_part = Model_Object()
            new_part.elements.offset = element_count
            if len(obj.models) != 0:
                obj.models[-1].elements.elem_count = element_count - obj.models[-1].elements.offset
            obj.models.append(Model_Object())

    if len(obj.models) != 0:
        obj.models[-1].elements.elem_count = element_count - obj.models[-1].elements.offset
    else:
        obj.models = [Model_Object()]
        obj.models[0].elem_count = element_count

    if len(elements) == 0: 
        print "Attempted to load a model with no elements."
        exit()
    
    arr_elems = numpy.array(elements,dtype='uint32')
    model_elements = Model_Elements()
    model_elements.load(arr_elems)
            
    lpos = len(positions)
    lnor = len(normals)
    ltex = len(tex_coords)
    ltan = 0

    if lpos != 0:
        # arr_pos = numpy.array(positions,dtype='float32')
        a_positions.load(arr_pos)
        a_positions.elem_len = 3 
    if lnor != 0:
        # arr_nor = numpy.array(normals,dtype='float32')
        a_normals.load(arr_nor)
        a_normals.elem_len = 3
    if ltex != 0:
        # arr_tex = numpy.array(tex_coords,dtype='float32')
        a_tex_coords.load(arr_tex)
        a_tex_coords.elem_len = 2
    if lpos != 0 and lnor != 0 and ltex != 0:
        arr_tangents = calculateTangents(arr_pos,arr_nor,arr_tex,arr_elems)
        ltan = len(arr_tangents)
        a_tangents.load(arr_tangents)
        a_tangents.elem_len = 4

    for o in obj.models:
        if lpos != 0:
            o.load_attribute(a_positions)
        if lnor != 0:
            o.load_attribute(a_normals)
        if ltex != 0:
            o.load_attribute(a_tex_coords)
        if ltan != 0:
            o.load_attribute(a_tangents)
        o.elements.buffer = model_elements.buffer

    content.close()
    return obj

def load3ds(filename):
    try:
        load(filename)
    except IOError:
        print "Error loading file: " + filename
        return 


    scene = getScene()

    print "\n\n LOADING " + filename + "\n\n"

    model_set = Model_Set()

    for obj in scene.walkWorld():
        model = loadSceneObject(obj,scene)
        if model != None:
            model_set.models.append(model)
            print "Loaded model [" + model.name +"]"

    scene.clear()

    return model_set

def loadSceneObject(mesh,scene):
        
    meshname = mesh.name

    if type(mesh) != cgkit.trimesh.TriMesh:
        # print "Mesh object ["+meshname+"] is not a mesh."
        return

    print vars(mesh)
    # if meshname != 'cate 1 hu0':return
    # if meshname == 'greaves':return
    # if meshname == 'harness':return
    # if meshname == 'iron boots':return
    # if meshname == 'iron pants':return
    # if meshname == 'irongloves':return
    # if meshname == 'krause':return
    # if meshname == 'tara_catsu':return
    # if meshname == 'tara_cats0':return
    # if meshname == 'Object03':return
    # if meshname == 'Sphere03':return
    
    if len(mesh.faces) is 0: return

    model = Model_Object()
    model.name = meshname

    mat = mesh.getMaterial()
    if mat != None:
        model.material = loadMaterial(mat,scene)
    else:
        print 'Warning: no material set for mesh', meshname
        model.material = Model_Material()
        
    positions = numpy.array(mesh.verts,dtype="float32")
    elements = numpy.array(mesh.faces,dtype="uint32")

    normals = []
    normal_desc = mesh.findVariable("N")
    if normal_desc == None:
        print 'Mesh ['+meshname+'] has no Normals.'
        None
    else:
        n_name, n_storage, n_type, n_mult = normal_desc
        if n_storage == VARYING and n_type == NORMAL and n_mult == 1:
            normals = numpy.array([norm for norm in mesh.geom.slot("N")],dtype="float32")
        elif n_storage == USER and n_type == NORMAL and n_mult == 1:
            if mesh.findVariable("Nfaces") == None:
                print 'Mesh ['+meshname+'] has no well defined normals.'

            f_name, f_storage, f_type, f_mult = mesh.findVariable("Nfaces")
            if f_storage == UNIFORM and f_type == INT and f_mult == 3:
                normals = numpy.zeros((len(positions),3),dtype='float32')
                for face,nface in zip (mesh.faces,mesh.geom.slot("Nfaces")):
                    va,vb,vc = face
                    na,nb,nc = nface
                    normals[va] = mesh.geom.slot("N")[na]
                    normals[vb] = mesh.geom.slot("N")[nb]
                    normals[vc] = mesh.geom.slot("N")[nc]
            else:
                print 'Mesh ['+meshname+'] has no well defined normals.'

        else:
            print 'Mesh ['+meshname+'] has no well defined normals.'


    tex_coords = []
    tex_desc = mesh.findVariable("st")
    if tex_desc == None:
        None
    else:
        t_name, t_storage, t_type, t_mult = tex_desc
        if t_storage == VARYING and t_type == FLOAT and t_mult == 2:
            tex_coords = numpy.array(mesh.geom.slot('st'),dtype="float32")
        else:
            print 'Mesh ['+ meshname+'] has no well defined texture coordinates specified.'

    model.elements.load(elements)

    if len(positions) != 0:
        a_positions = Model_Attribute('in_Position')
        a_positions.load(positions)
        a_positions.elem_len = 3
        model.load_attribute(a_positions)
    if len(normals) != 0:
        a_normals = Model_Attribute('in_Normal')
        a_normals.load(normals)
        a_normals.elem_len = 3
        model.load_attribute(a_normals)
    if len(tex_coords) != 0:
        a_tex_coords = Model_Attribute('in_TexCoord')
        a_tex_coords.load(tex_coords)
        a_tex_coords.elem_len = 2
        model.load_attribute(a_tex_coords)

    if len(positions) != 0 and len(normals) != 0 and len(tex_coords) != 0:
        tangents = calculateTangents(positions,normals,tex_coords,elements)
        a_tangents = Model_Attribute('in_Tangent')
        a_tangents.load(tangents)
        a_tangents.elem_len = 4
        model.load_attribute(a_tangents)

    model.props.pos = mesh.pos
    model.props.scale = mesh.scale
    model.props.ori.fromMat(mesh.rot)
    return model
    
def loadMaterial(material,scene):
    if type(material) == cgkit.material3ds.Material3DS:
        new_mat = Model_Material()
        new_mat.ambient = material.ambient
        new_mat.diffuse = material.diffuse
        new_mat.specular = material.specular
        new_mat.shininess = material.shininess
        new_mat.shin_strength = material.shin_strength
        # new_mat.use_blur = material.use_blur
        new_mat.transparency = material.transparency
        # new_mat.falloff = material.falloff
        # new_mat.additive = material.additive
        # new_mat.use_falloff = material.use_falloff
        new_mat.self_illum = material.self_illum
        new_mat.self_ilpct = material.self_ilpct
        # new_mat.shading = material.shading
        # new_mat.soften = material.soften
        # new_mat.face_map = material.face_map
        # new_mat.two_sided = material.two_sided
        # new_mat.map_decal = material.map_decal
        # new_mat.use_wire = material.use_wire
        # new_mat.use_wire_abs = material.use_wire_abs
        # new_mat.wire_size = material.wire_size
        new_mat.density = material.density


        new_mat.texture1_map.load3dsTextureMap(material.texture1_map)
        if material.texture1_map != None:
            print "-------------texture1-------------"
            print "Map:\n", material.texture1_map
            print "Mask:\n",material.texture1_mask


        new_mat.texture2_map.load3dsTextureMap(material.texture2_map)
        if material.texture2_map != None:
            print "-------------texture2-------------"
            print "Map:\n", material.texture2_map
            print "Mask:\n",material.texture2_mask

        new_mat.opacity_map.load3dsTextureMap(material.opacity_map)

        if material.opacity_map != None:
            print "-------------opacity-------------"
            print "Map:\n", material.opacity_map
            print "Mask:\n",material.opacity_mask


        # if material.bump_map != None:
            # new_mat.bump_map = copy.deepcopy(new_mat.texture1_map)
            # new_mat.bump_map.scale = (0.3,0.3)
            # new_mat.bump_map.name = '/home/leo/Projects/PyOpenGL/textures/normal.jpg'

        if material.bump_map != None:
            new_mat.bump_map.load3dsTextureMap(material.bump_map)
            print "-------------bump-------------"
            print "Map:\n", material.bump_map
            print "Mask:\n",material.bump_mask
            print "Bump Size:\n", material.bump_size

        new_mat.specular_map.load3dsTextureMap(material.specular_map)

        if material.specular_map != None:
            print "-------------specular-------------"
            print "Map:\n", material.specular_map
            print "Mask:\n",material.specular_mask

        new_mat.shininess_map.load3dsTextureMap(material.shininess_map)

        if material.shininess_map != None:
            print "-------------shininess-------------"
            print "Map:\n", material.shininess_map
            print "Mask:\n",material.shininess_mask

        new_mat.self_illum_map.load3dsTextureMap(material.self_illum_map)

        if material.self_illum_map != None:
            print "-------------self_illum-------------"
            print "Map:\n", material.self_illum_map
            print "Mask:\n",material.self_illum_mask

        new_mat.reflection_map.load3dsTextureMap(material.reflection_map)

        if material.reflection_map != None:
            print "-------------reflection-------------"
            print "Map:\n", material.reflection_map
            print "Mask:\n",material.reflection_mask

        new_mat.bump_size = material.bump_size

        return new_mat
    elif type(material) == cgkit.glmaterial.GLMaterial:
        new_mat = Model_Material()
        
        new_mat.ambient = material.ambient
        new_mat.diffuse = material.diffuse
        new_mat.specular = material.specular
        new_mat.shininess = material.shininess

        print 'glMaterial textures:', material.getNumTextures()
        #new_mat.self_ilpct = material.emission ?
        return new_mat
    else:
        print 'Unknown Material type encountered:', type(material)
        return Model_Material()

def loadTexture(model,textures):
    if type(model) == Model_Set:
        for mod in model.models:
            loadTexture(mod,textures)
    elif type(model) == Model_Object:
        mat = model.material
        for tex_name in mat.texture2d_names():
            if tex_name not in textures.samplers2d:
                tex = Model_Texture()
                tex.set_texture_file(tex_name)
                tex.load()
                print 'Loaded texture [' + tex_name + ']'
                textures.samplers2d[tex_name] = tex

        for name,xp,xn,yp,yn,zp,zn in mat.textureCM_names():
            if name not in textures.samplersCM:
                tex = Model_Cubemap_Texture()
                tex.set_texture_files(xp,xn,yp,yn,zp,zn)
                tex.load()
                textures.samplersCM[name] = tex

def main():
    obj = model()
    print obj.positions
    
if __name__ == '__main__': main()


