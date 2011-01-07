#!/usr/bin/python2.6 -tt
import OpenGL
OpenGL.ERROR_ON_COPY = True
# OpenGL.ERROR_LOGGING = False
# OpenGL.ERROR_CHECKING = False
OpenGL.FORWARD_COMPATIBLE_ONLY = True 

from OpenGL.GL import *
from OpenGL.GLUT import *

import numpy
from scene import Scene,Screen

import cgkit
from cgkit.all import quat, mat4, vec3
from model import Model_Texture, Model_Set, Model_Object

def vbo_offset(offset):
    return ctypes.c_void_p(offset * 4)

def reshape(w,h,screen):
    glViewport(0,0,w,h)
    screen.size = (w,h)

def mouseFunc(x,y,scene,screen):
    (w,h) = screen.size
    delta = 0.01
    az_delta  = delta * float(w/2-x)
    inc_delta = delta * float(h/2-y)

    if (az_delta,inc_delta) != (0,0):
        scene.cam.delta(az_delta, inc_delta)
        glutWarpPointer(w/2,h/2)

def keyPressed(key,x,y,scene):
    delta = 0.05
    cam = scene.cam
    if key == '\033':
        sys.exit(1)
    if key == 'w':
        delta_pos = - cam.rot() * vec3(0,0,1)
        for i in range(0,3):
            cam.pos[i] += delta * delta_pos[i]
    if key == 's':
        delta_pos = cam.rot() * vec3(0,0,1)
        for i in range(0,3):
            cam.pos[i] += delta * delta_pos[i]
    if key == 'a':
        delta_pos = - cam.rot() * vec3(1,0,0)
        for i in range(0,3):
            cam.pos[i] += delta * delta_pos[i]
    if key == 'd':
        delta_pos = cam.rot() * vec3(1,0,0)
        for i in range(0,3):
            cam.pos[i] += delta * delta_pos[i]

def drawScene(scene):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    drawCubemap(scene)

    glClear(GL_DEPTH_BUFFER_BIT)

    glUseProgram(scene.active_program)
    for obj in scene.models:
        drawObject(obj,scene)

    glutSwapBuffers()

def drawCubemap(scene):
    scene.cubemap.use_program()
    mvpTransf = numpy.array(list(scene.cam.projTransf * scene.cam.rotTransf()),
                            dtype="float32")
    scene.cubemap.draw(mvpTransf)

def drawObject(obj, scene, transf = mat4(1.0)):
    cam = scene.cam

    glEnable( GL_TEXTURE_2D )

    if type(obj) == Model_Set:
        new_transf = transf * obj.props.transf()
        for model in obj.models: 
            drawObject(model,scene, new_transf)
    elif type(obj) == Model_Object:
        #Set mv transform
        new_transf = transf * obj.props.transf() 
        modelview =   cam.transf() * new_transf
        transf_array = numpy.array([val for val in modelview], dtype="float32")
        modelview_loc = glGetUniformLocation(scene.active_program,"in_Modelview")
        glUniformMatrix4fv(modelview_loc, 1, GL_FALSE, transf_array)

        #Set projection transform
        proj = numpy.array([val for val in cam.projTransf], dtype="float32")
        projection_loc = glGetUniformLocation(scene.active_program,"in_Projection")
        glUniformMatrix4fv(projection_loc, 1, GL_FALSE, proj)

        #Set texture
        # glActiveTexture(GL_TEXTURE0)
        # tex_sampler = glGetUniformLocation(scene.active_program,"color_tex")
        # shin_sampler = glGetUniformLocation(scene.active_program,"shininess_tex")
        # scene.textures.items()[2][1].bind()
        # glUniform1i(tex_sampler,0)
        # glActiveTexture(GL_TEXTURE1)
        # scene.textures.items()[0][1].bind()
        # glUniform1i(shin_sampler,1)

        # shin_enab_loc= glGetUniformLocation(scene.active_program,'shininess_enabled')
        # # glUniform1f(shin_enab_loc, 1, GL_FALSE, ctypes.c_float(0.2))
        # glUniform1i(shin_enab_loc, 0)
        set3dsMaterial(obj.material,scene)

        #Send draw command
        if obj.set_buffers(scene.active_program):
            vertex_count = obj.elements.elem_count * 3
            glDrawElements(GL_TRIANGLES,
                           vertex_count,
                           GL_UNSIGNED_INT,
                           vbo_offset(obj.elements.offset))

            if glGetError() != GL_NO_ERROR:
                print "Error: " + str(glGetError())

    else:
        return

def set3dsMaterial(material,scene):
    current_texture = 0;
    textures = scene.textures
    program = scene.active_program

    #Float uniforms
    vals  = [material.shininess,material.shin_strength,
             material.transparency,material.self_illum,
             material.self_ilpct,material.bump_size]
    names = ['mat_shininess','mat_shin_strength',
             'mat_transparency','mat_self_illum',
             'mat_self_ilpct','mat_bump_size']
    for val,name in zip(vals,names):
        loc = glGetUniformLocation(program,name)
        glUniform1f(loc, val)

    #vec4 uniforms
    vals  = [material.ambient,material.diffuse,material.specular]
    names = ['mat_ambient','mat_diffuse','mat_specular']
    for val,name in zip(vals,names):
        loc = glGetUniformLocation(program,name)
        glUniform4f(loc, val[0],val[1],val[2],val[3])
        
    #Texture_map uniforms
    maps = [material.texture1_map,material.texture2_map,
            material.bump_map,material.specular_map,
            material.shininess_map,material.self_illum_map,
            material.self_illum_map,material.reflection_map]
    names = ['texture1_map','texture2_map','bump_map','specular_map',
             'shininess_map','self_illum_map','self_illum_map','reflection_map']
    for val,name in zip(maps,names):
        loc = glGetUniformLocation(program,name + '.set')
        if not val.set:
            glUniform1i(loc, 0)
            continue
        else: glUniform1i(loc, 1)

        loc = glGetUniformLocation(program,name + '.rotation')
        glUniform1f(loc, val.rotation)

        loc = glGetUniformLocation(program,name + '.percent')
        glUniform1f(loc, val.percent)

        loc = glGetUniformLocation(program,name + '.offset')
        glUniform2f(loc, val.offset[0],val.offset[1])

        loc = glGetUniformLocation(program,name + '.scale')
        glUniform2f(loc, val.scale[0],val.scale[1])

        glActiveTexture(GL_TEXTURE0+current_texture)
        loc = glGetUniformLocation(program,name + '.tex')
        texture = textures[val.name]
        texture.bind()
        glUniform1i(loc, current_texture)
        current_texture += 1


def initShaders(v_filename, f_filename):
    v_shader = glCreateShader(GL_VERTEX_SHADER)
    v_shader_source = [open(v_filename,'r').read()]
    glShaderSource(v_shader,v_shader_source)

    f_shader = glCreateShader(GL_FRAGMENT_SHADER)
    f_shader_source = [open(f_filename,'r').read()]
    glShaderSource(f_shader,f_shader_source)

    program = glCreateProgram()
    glAttachShader(program,v_shader)
    glAttachShader(program,f_shader)

    glCompileShader(v_shader)
    glCompileShader(f_shader)
    
    print glGetShaderInfoLog(v_shader)
    print glGetShaderInfoLog(f_shader)

    glLinkProgram(program)
    glValidateProgram(program)
    
    print glGetProgramInfoLog(program)

    glUseProgram(program)

    print "active_program:", program

    return program

def startOpengl():
    # global screen_size
    glutInit(sys.argv)
    # glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH | GLUT_MULTISAMPLE)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH )
    glutInitWindowPosition(100,100)
    glutInitWindowSize(500,500)
    screen_size = (500,500)
    glutCreateWindow("TRY")
    glClearColor(0.0,0.0,0.0,0.0)
    glClearDepth(1.0)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glCullFace(GL_FRONT)
    # glEnable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_TEXTURE_CUBE_MAP)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glutSwapBuffers()
    return screen_size

def try_cubemap(scene):
    if not scene.loadCubemapTextures(
        'textures/cubemap/sky_x_pos.jpg',
        'textures/cubemap/sky_x_neg.jpg',
        'textures/cubemap/sky_y_pos.jpg',
        'textures/cubemap/sky_y_neg.jpg',
        'textures/cubemap/sky_z_pos.jpg',
        'textures/cubemap/sky_z_neg.jpg'):
        exit(-1)

def main():
    screen_size = startOpengl()
    # program = initShaders("minimal.vert", "minimal.frag")
    program = initShaders("3ds.vert", "3ds.frag")

    # model = scene.loadObjModel('models/teapot.obj')
    # model = scene.loadObjModel('models/human/cate_human.obj')
    # model = scene.load3dsModel('models/bunny.3ds')
    # model = scene.load3dsModel('models/human/cate_human.3DS')
    # model = scene.load3dsModel('models/gib/gib.3DS')
    # model = scene.load3dsModel('models/theodora/theodora.3DS')
    # model = scene.load3dsModel('models/irongirl/irongirl_mesh.3DS')

    scene = Scene()
    scene.active_program = program

    # model_index = scene.load3dsModel('models/irongirl/irongirl_mesh.3DS')
    # model_index = scene.load3dsModel('models/human/cate_human.3DS')
    # model_index = scene.load3dsModel('models/gib/gib.3DS')
    # model_index = scene.load3dsModel('models/quarian/cate_quarian.3DS')
    # model_index = scene.load3dsModel('models/girl/girlnpc.3DS')
    # model_index = scene.load3dsModel('models/bmw/bmw.3DS')
    # model_index = scene.load3dsModel('models/bus/Busall.3ds')
    # model_index = scene.load3dsModel('models/toy/stand toy.3DS')
    # model_index = scene.load3dsModel('models/toy/sitting toy.3DS')
    # model_index = scene.load3dsModel('models/bike/sidecar2.3ds')
    # model_index = scene.load3dsModel('models/bot/plx.3DS')
    model_index = scene.loadObjModel('models/teapot.obj')
    # model_index = scene.loadObjModel('models/human/cate_human.obj')

    if model_index == None:
        print 'Error loading model'
        exit(-1)

    model = scene.models[model_index]

    model.props.pos = vec3(0,0,0)
    # model.props.scale = vec3(0.01)
    # model.props.ori = quat(-1.57,vec3(1,0,0))
    model.props.scale = vec3(1)
    model.props.ori = quat(-1.57,vec3(0,1,0))

    for m in model.models:
        tm = m.material.texture1_map
        tm.name = 'textures/masonry-wall-texture.jpg'
        tm.scale = (10,10)
        tm.set = True

        bm = m.material.bump_map
        bm.scale = (10,10)
        bm.name = 'textures/masonry-wall-normal-map.jpg'
        bm.set = True

    scene.loadModelsTextures()

    scene.cam.pos = vec3(0.,0.,3)
    
    try_cubemap(scene)

    screen = Screen()
    screen.size = screen_size

    glutDisplayFunc(lambda : drawScene(scene))
    glutIdleFunc(lambda : drawScene(scene))
    glutReshapeFunc(lambda w,h: reshape(w,h,screen))

    glutKeyboardFunc(lambda key,x,y : keyPressed(key,x,y,scene))
    glutMotionFunc(lambda x,y : mouseFunc(x,y,scene,screen))
    # glutPassiveMotionFunc(lambda x,y : mouseFunc(x,y,scene,screen_size))

    glutWarpPointer(250,250)

    glutMouseFunc
    glutMainLoop()


if __name__ == '__main__':main()
