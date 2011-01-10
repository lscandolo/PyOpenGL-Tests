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

frames = 0

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

    if key == 'z':
        model = scene.models[0]
        for m in model.models:
            m.material.bump_height += 0.005
    if key == 'x':
        model = scene.models[0]
        for m in model.models:
            m.material.bump_height -= 0.005


def drawScene(scene):
    global frames

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    if scene.cubemap != None:
        drawCubemap(scene)
        glClear(GL_DEPTH_BUFFER_BIT)

    glUseProgram(scene.active_program)
    for obj in scene.models:
        drawObject(obj,scene)

    glutSwapBuffers()

    frames += 1
    time = glutGet(GLUT_ELAPSED_TIME)/1000
    if time > scene.time + 1:
        print 'FPS:', frames
        frames = 0
        scene.time = time
        

def drawCubemap(scene):
    scene.cubemap.use_program()
    glActiveTexture(GL_TEXTURE0)
    tex_name = scene.cubemap.texture.name
    scene.cubemap.bindTexture(scene.textures.samplersCM[tex_name])
    mvpTransf = numpy.array(list(scene.cam.projTransf * scene.cam.rotTransf()),
                            dtype="float32")
    scene.cubemap.draw(mvpTransf)

def drawObject(obj, scene, transf = mat4(1.0)):
    cam = scene.cam

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

        setupMaterial(obj.material,scene)

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

def setupMaterial(material,scene):
    current_texture = 0;
    samplers2d = scene.textures.samplers2d
    samplersCM = scene.textures.samplersCM
    program = scene.active_program

    #Float uniforms
    vals  = [material.shininess,material.shin_strength,
             material.transparency,material.self_illum,
             material.self_ilpct,material.bump_height,
             material.bump_bias]
    names = ['mat_shininess','mat_shin_strength',
             'mat_transparency','mat_self_illum',
             'mat_self_ilpct','mat_bump_height',
             'mat_bump_bias']
    for val,name in zip(vals,names):
        loc = glGetUniformLocation(program,name)
        glUniform1f(loc, val)

    #vec4 uniforms
    vals  = [material.ambient,material.diffuse,material.specular]
    names = ['mat_ambient','mat_diffuse','mat_specular']
    for val,name in zip(vals,names):
        loc = glGetUniformLocation(program,name)
        glUniform4f(loc, val[0],val[1],val[2],val[3])
        
    #TextureMap uniforms
    maps = [material.texture1_map,material.texture2_map,
            material.height_map,material.normal_map,
            material.specular_map,material.shininess_map,
            material.self_illum_map,material.opacity_map]
    names = ['texture1_map','texture2_map',
             'height_map','normal_map',
             'specular_map','shininess_map',
             'self_illum_map','opacity_map']
    for val,name in zip(maps,names):
        loc = glGetUniformLocation(program,name + '.set')
        if not val.set:
            glUniform1i(loc, 0)
            continue
        
        glUniform1i(loc, 1)

        loc = glGetUniformLocation(program,name + '.rotation')
        glUniform1f(loc, val.rotation)

        loc = glGetUniformLocation(program,name + '.percent')
        glUniform1f(loc, val.percent)

        loc = glGetUniformLocation(program,name + '.offset')
        glUniform2f(loc, val.offset[0],val.offset[1])

        loc = glGetUniformLocation(program,name + '.scale')
        glUniform2f(loc, val.scale[0],val.scale[1])

        # glActiveTexture(GL_TEXTURE0)
        glActiveTexture(GL_TEXTURE0+current_texture)
        loc = glGetUniformLocation(program,name + '.tex')
        texture = samplers2d[val.name]
        texture.bind()
        glUniform1i(loc, current_texture)
        current_texture += 1

    #If the shader declares and (possibly) uses a cubemap it MUST be set

    #TextureCubemap uniforms
    maps = [material.reflection_map]
    names = ['reflection_map']
    for val,name in zip(maps,names):
        loc = glGetUniformLocation(program,name + '.set')
        sampler_loc = glGetUniformLocation(program,name + '.tex')
        glActiveTexture(GL_TEXTURE0+current_texture)

        #If a cubemap is declared, any cubemap MUST be set, so we set a default one
        if not val.set: 
            glUniform1i(loc, 0)
            texture = samplersCM['default']
        else:
            glUniform1i(loc, 1)

            loc = glGetUniformLocation(program,name + '.rotation')
            glUniform1f(loc, val.rotation)
            loc = glGetUniformLocation(program,name + '.percent')
            glUniform1f(loc, val.percent)

            texture = samplersCM[val.name]

            
        texture.bind()
        glUniform1i(sampler_loc, current_texture)
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

def main():
    screen_size = startOpengl()
    # program = initShaders("shaders/3ds.vert", "shaders/3ds.frag")
    # program = initShaders("shaders/parallax.vert", "shaders/parallax.frag")
    program = initShaders("shaders/relief.vert", "shaders/relief.frag")

    scene = Scene()
    scene.active_program = program

    model_index = scene.loadObjModel('models/floor.obj')
    # model_index = scene.loadObjModel('models/teapot.obj')

    if model_index == None:
        print 'Error loading model'
        exit(-1)

    model = scene.models[model_index]

    model.props.pos = vec3(0,-0.5,3)
    model.props.scale = vec3(1)

    for m in model.models:
        m.material.bump_height = 0.02

        tm = m.material.texture1_map
        nm = m.material.normal_map
        hm = m.material.height_map

        # tm.name = 'textures/uvmap.png'

        tm.name = 'textures/brickwork-texture.jpg'
        hm.name = 'textures/brickwork-height_map.jpg'
        nm.name = 'textures/brickwork-normal_map.jpg'

        # tm.name = 'textures/masonry_wall-texture.jpg'
        # hm.name = 'textures/masonry_wall-height_map.jpg'
        # nm.name = 'textures/masonry_wall-normal_map.jpg'

        sc = 1
        tm.scale = (sc,sc)
        hm.scale = (sc,sc)
        nm.scale = (sc,sc)
        tm.set = True
        hm.set = True
        nm.set = True

        # sm = m.material.shininess_map
        # sm.name = 'textures/brickwork-bump_map.jpg'
        # sm.scale = (sc,sc)
        # sm.set = True

        # rm = m.material.reflection_map
        # rm.set_textures('textures/cubemap/sky_x_pos.jpg',
        #                 'textures/cubemap/sky_x_neg.jpg',
        #                 'textures/cubemap/sky_y_pos.jpg',
        #                 'textures/cubemap/sky_y_neg.jpg',
        #                 'textures/cubemap/sky_z_pos.jpg',
        #                 'textures/cubemap/sky_z_neg.jpg')
        # rm.set = True

    scene.initCubemap('textures/cubemap/sky_x_pos.jpg',
                      'textures/cubemap/sky_x_neg.jpg',
                      'textures/cubemap/sky_y_pos.jpg',
                      'textures/cubemap/sky_y_neg.jpg',
                      'textures/cubemap/sky_z_pos.jpg',
                      'textures/cubemap/sky_z_neg.jpg')

    scene.loadModelTextures()
    scene.cam.pos = vec3(0.,0.,3)
    
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
