#!/usr/bin/python2.6 -tt
import OpenGL
OpenGL.ERROR_ON_COPY = True
# OpenGL.ERROR_LOGGING = False
# OpenGL.ERROR_CHECKING = False
OpenGL.FORWARD_COMPATIBLE_ONLY = True 

from OpenGL.GL import *
from OpenGL.GLUT import *

# from OpenGL.GL.ARB.framebuffer_object import *
# from OpenGL.GL.EXT.framebuffer_object import *
from OpenGL.GL.framebufferobjects import *


import numpy
from scene import Scene,Screen

import cgkit
from cgkit.all import quat, mat4, vec3, vec4
from model import Model_Texture, Model_Set, Model_Object

frames = 0

def vbo_offset(offset):
    return ctypes.c_void_p(offset * 4)

def reshape(w,h,scene):
    glViewport(0,0,w,h)
    scene.screen.size = (w,h)
    scene.cam.projTransf = mat4().perspective(50.,w/float(h),0.01,100)

def mouseFunc(x,y,scene):
    (w,h) = scene.screen.size
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

            
    light = scene.lights.spots[0]
    model = scene.models[1]

    if key == 't':
        model.props.pos.x += 0.1
    if key == 'r':
        model.props.pos.x -= 0.1
    if key == 'g':
        model.props.pos.z += 0.1
    if key == 'f':
        model.props.pos.z -= 0.1
    if key == 'b':
        model.props.pos.y += 0.1
    if key == 'v':
        model.props.pos.y -= 0.1

    if key == 'h':
        light.pos.x += 0.1
    if key == 'k':
        light.pos.x -= 0.1
    if key == 'u':
        light.pos.z += 0.1
    if key == 'j':
        light.pos.z -= 0.1
    if key == 'o':
        light.intensity += 0.1
    if key == 'l':
        light.intensity -= 0.1
    if key == 'y':
        light.pos.y += 0.1
    if key == 'i':
        light.pos.y -= 0.1
            
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
    
    glLinkProgram(program)
    glValidateProgram(program)
    
    print "/////////////////Main  shaders status:"
    print glGetShaderInfoLog(v_shader)
    print glGetShaderInfoLog(f_shader)
    print glGetProgramInfoLog(program)
    print "Main program location:", program
    print "///////////////////////////////////////"

    glUseProgram(program)
    return program

def startOpengl(w,h):
    glutInit(sys.argv)
    # glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH | GLUT_MULTISAMPLE)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH )
    glutInitWindowPosition(100,100)
    glutInitWindowSize(w,h)
    glutCreateWindow("TRY")
    glClearColor(0.0,0.0,0.0,0.0)
    glClearDepth(1.0)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glCullFace(GL_BACK)
    glEnable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_TEXTURE_CUBE_MAP)

    # print glGetString(GL_VERSION)
    # print glGetString(GL_VENDOR)
    # print glGetString(GL_EXTENSIONS)
    # print glGetString(GL_SHADING_LANGUAGE_VERSION)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glutSwapBuffers()

def main():

    scene = Scene()
    scene.screen.size = (500,400)
    startOpengl(scene.screen.size[0],scene.screen.size[1])

    scene.active_program = initShaders("shaders/3ds.vert", "shaders/3ds.frag")
    # scene.active_program = initShaders("shaders/parallax.vert", "shaders/parallax.frag")
    # scene.active_program = initShaders("shaders/relief.vert", "shaders/relief.frag")

    scene.initShadowFB()

    floor_index = scene.loadObjModel('models/floor.obj')
    teapot_index = scene.loadObjModel('models/teapot.obj')

    if floor_index or teapot_index == None:
        print 'Error loading model'
        exit(-1)

    floor = scene.models[floor_index]
    teapot = scene.models[teapot_index]

    floor.props.pos = vec3(0,-0.5,3)
    floor.props.scale = vec3(1)

    for m in teapot.models:
        m.material.ambient = vec4(1,0.2,0.2,1)
        tm = m.material.texture1_map
        nm = m.material.normal_map
        hm = m.material.height_map
        tm.name = 'textures/masonry_wall-texture.jpg'
        hm.name = 'textures/masonry_wall-height_map.jpg'
        nm.name = 'textures/masonry_wall-normal_map.jpg'
        sc = 4
        tm.scale = (sc,sc)
        hm.scale = (sc,sc)
        nm.scale = (sc,sc)
        tm.set = False
        hm.set = False
        nm.set = False

    for m in floor.models:
        m.material.bump_height = 0.015
        m.material.ambient = vec4(0.8,0.8,1,1)

        tm = m.material.texture1_map
        nm = m.material.normal_map
        hm = m.material.height_map

        tm.name = 'textures/brickwork-texture.jpg'
        hm.name = 'textures/brickwork-height_map.jpg'
        nm.name = 'textures/brickwork-normal_map.jpg'

        sc = 2
        tm.scale = (sc,sc)
        hm.scale = (sc,sc)
        nm.scale = (sc,sc)
        tm.set = False
        hm.set = False
        nm.set = False

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
    scene.cam.pos = vec3(0.,1,3.)

    scene.lights.ambient.intensity = 0.6

    # spot_light = scene.lights.new_spot_light()
    # spot_light.pos = vec3(0,5,0)
    # spot_light.dir = vec3(0,-1,0).normalize()
    # spot_light.reach = 10
    # spot_light.dist_dimming = 0.5
    # spot_light.ang_dimming = 0.5
    # spot_light.color = vec3(1,1,1)

    spot_light = scene.new_spot_light()
    spot_light.pos = vec3(0,3,-1)
    spot_light.dir = vec3(0,-1,1).normalize()
    spot_light.reach = 20
    spot_light.dist_dimming = 0.5
    spot_light.ang_dimming = 0.5
    spot_light.color = vec3(1,1,1)

    glutDisplayFunc(lambda : scene.drawScene())
    glutIdleFunc(lambda : scene.drawScene())
    glutReshapeFunc(lambda w,h: reshape(w,h,scene))

    glutKeyboardFunc(lambda key,x,y : keyPressed(key,x,y,scene))
    glutMotionFunc(lambda x,y : mouseFunc(x,y,scene))
    # glutPassiveMotionFunc(lambda x,y : mouseFunc(x,y,scene,screen_size))

    glutWarpPointer(250,250)

    glutMouseFunc
    glutMainLoop()


if __name__ == '__main__':main()
