from model import *
from loader import *
from cubemap import *
from light import Light_Atlas
from shadow import ShadowFB

class Scene(object):
    def __init__(self):
        self.models = []
        self.textures = Texture_Atlas()
        self.lights = Light_Atlas()
        self.cam = Cam()
        self.cubemap = None
        self.active_program = None
        self.frame_textures = 0
        self.time = 0.
        self.frames = 0
        self.shadowfb = ShadowFB()
        self.screen = Screen()
        self.shadow_map_resolution = 512

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

    def initShadowFB(self):
        self.shadowfb.allocate(self.shadow_map_resolution)

    def new_spot_light(self,generate_shadow_map = True):
        return (self.lights.new_spot_light(generate_shadow_map,self.shadow_map_resolution))

    def drawScene(self):
    #Draw to shadow map textures 
        self.drawSpotLightShadows()

    #Attach default framebuffer and clear it
        # self.shadowfb.unbind()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    #Draw cubemap 
        if self.cubemap != None:
            self.drawCubemap()
            glClear(GL_DEPTH_BUFFER_BIT)

    #Set shaders
        glUseProgram(self.active_program)
            
    #Draw Objects
        for obj in self.models:
            self.drawObject(obj)

    #Swap buffer
        glutSwapBuffers()

    #FPS computation
        self.frames += 1
        time = glutGet(GLUT_ELAPSED_TIME)/1000
        if time > self.time + 1:
            print 'FPS:', self.frames
            self.frames = 0
            self.time = time
        
    def drawSpotLightShadows(self):

    # Set viewport for shadow texture buffer
        shadow_res = self.shadowfb.resolution
        glViewport(0,0,shadow_res,shadow_res)
        for l in self.lights.spots:
            if l.generates_shadow_map:
    # Set shadowbuffer shaders
                glUseProgram(self.shadowfb.program)
    # Setup shadow framebuffer
                if not self.shadowfb.setup(l.shadow_texture.location):
                    print 'Error drawing spotlight: Problem generating framebuffer'
                    return
    # Draw Objects
                glClear(GL_DEPTH_BUFFER_BIT)
                for obj in self.models:
                    self.drawObjectShadow(obj,l.cam())
                self.shadowfb.unbind()
                glUseProgram(self.active_program)
                glBindFramebuffer(GL_FRAMEBUFFER, 0)

    # Set viewport for normal drawing
        glViewport(0,0,self.screen.size[0],self.screen.size[1])

    def drawCubemap(self):
        self.cubemap.use_program()
        glActiveTexture(GL_TEXTURE0)
        tex_name = self.cubemap.texture.name
        self.cubemap.bindTexture(self.textures.samplersCM[tex_name])
        mvpTransf = numpy.array(list(self.cam.projTransf * self.cam.rotTransf()),
                                dtype="float32")
        self.cubemap.draw(mvpTransf)

    def drawObject(self,obj, transf = mat4(1.0)):

        cam = self.cam
        # cam = self.lights.spots[0].cam()

        if type(obj) is Model_Set:
            new_transf = transf * obj.props.transf()
            for model in obj.models: 
                self.drawObject(model, new_transf)
        elif type(obj) is Model_Object:

        #Reset the texture count
            self.frame_textures = 0
            
        #Set mv transform
            modelview =  cam.transf() * transf * obj.props.transf()

        #Modelview transform
            transf_array = numpy.array([val for val in modelview], dtype="float32")
            loc = glGetUniformLocation(self.active_program,"in_Modelview")
            glUniformMatrix4fv(loc, 1, GL_FALSE, transf_array)

        #Modelview inverse transform
            modelviewInv = modelview.inverse()
            transf_array = numpy.array([val for val in modelviewInv], dtype="float32")
            loc = glGetUniformLocation(self.active_program,"in_ModelviewInv")
            glUniformMatrix4fv(loc, 1, GL_FALSE, transf_array)

        #View transform
            view = cam.transf()
            transf_array = numpy.array([val for val in view], dtype="float32")
            loc = glGetUniformLocation(self.active_program,"in_View")
            glUniformMatrix4fv(loc, 1, GL_FALSE, transf_array)

        #View inverse transform
            viewInv = cam.transf().inverse()
            transf_array = numpy.array([val for val in viewInv], dtype="float32")
            loc = glGetUniformLocation(self.active_program,"in_ViewInv")
            glUniformMatrix4fv(loc, 1, GL_FALSE, transf_array)

        #Set projection transform
            proj = numpy.array([val for val in cam.projTransf], dtype="float32")
            loc = glGetUniformLocation(self.active_program,"in_Projection")
            glUniformMatrix4fv(loc, 1, GL_FALSE, proj)

        #Setup material uniforms
            obj.material.setup(self)

        #Setup light uniforms
            self.lights.setup(self)

        #Setup object buffers
            obj.setup(self.active_program)
        
        #Send draw command
            if obj.elements.elem_count > 0:
                vertex_count = obj.elements.elem_count * 3
                glDrawElements(GL_TRIANGLES,
                               vertex_count,
                               GL_UNSIGNED_INT,
                               vbo_offset(obj.elements.offset))

                if glGetError() != GL_NO_ERROR:
                    print "Error: " + str(glGetError())

        else:
            return

    def drawObjectShadow(self,obj, cam, transf = mat4(1.0)):

        program = self.shadowfb.program
        if type(obj) is Model_Set:
            new_transf = transf * obj.props.transf()
            for model in obj.models: 
                self.drawObjectShadow(model, cam, new_transf)
        elif type(obj) is Model_Object:

        #Set mv transform
            modelview =  cam.transf() * transf * obj.props.transf()

        #Modelview transform
            transf_array = numpy.array([val for val in modelview], dtype="float32")
            loc = glGetUniformLocation(program,"in_Modelview")
            glUniformMatrix4fv(loc, 1, GL_FALSE, transf_array)

        #Set projection transform
            proj = numpy.array([val for val in cam.projTransf], dtype="float32")
            loc = glGetUniformLocation(program,"in_Projection")
            glUniformMatrix4fv(loc, 1, GL_FALSE, proj)

        #Setup object buffers
            obj.setup(program)
        
        #Send draw command
            if obj.elements.elem_count > 0:
                vertex_count = obj.elements.elem_count * 3
                glDrawElements(GL_TRIANGLES,
                               vertex_count,
                               GL_UNSIGNED_INT,
                               vbo_offset(obj.elements.offset))

                if glGetError() != GL_NO_ERROR:
                    print "Error: " + str(glGetError())

        else:
            return



class Screen(object):
    def __init__(self):
        self.size = (0,0)
        self.walltime = 0


class Texture_Atlas():
    def __init__(self):
        self.samplers2d = dict()
        self.samplersCM = dict()

