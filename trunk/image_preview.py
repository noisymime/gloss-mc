import clutter
import pygtk
import gtk
import random

class image_previewer(clutter.Group):
    tex1 = None
    tex2 = None
    tex3 = None
    frontTex = None
    behave1 = None
    behave2 = None
    behave3 = None
    
    scale_start = 0.6
    
    def __init__(self, stage):
        clutter.Group.__init__(self)
        self.textures = []
        self.stage = stage
        self.timeline = clutter.Timeline(200, 25)
        self.timeline.set_loop(True)
        self.timeline.connect('completed', self.next_image)
        
        self.connect('show', self.start)
        
        self.alpha = clutter.Alpha(self.timeline, clutter.ramp_inc_func)
        
        self.behaviour_scale = clutter.BehaviourScale(x_scale_start=self.scale_start, y_scale_start=self.scale_start, x_scale_end=1, y_scale_end=1, alpha=self.alpha)
        self.behaviour_depth = clutter.BehaviourDepth(depth_start=-300, depth_end=200, alpha=self.alpha)
        
        
    def add_texture(self, texture_src):
        self.textures.append(texture_src)
    
    def start(self, data):
        if len(self.textures) == 0:
            return None
        
        self.tex1 = self.get_rand_tex()
        self.tex2 = self.get_rand_tex()
        self.tex3 = self.get_rand_tex()
        
        self.behave1 = clutter.BehaviourPath(self.alpha, self.get_texture_knots(self.tex1))
        self.behave2 = clutter.BehaviourPath(self.alpha, self.get_texture_knots(self.tex2))
        self.behave3 = clutter.BehaviourPath(self.alpha, self.get_texture_knots(self.tex3))
        
        #self.tex1.set_scale(self.scale_start, self.scale_start)
        self.behaviour_depth.apply(self.tex1)
        self.behave1.apply(self.tex1)
        
        
        self.add(self.tex1)
        parent = self.get_parent()
        if parent is None:
            print "Parent is none!"
        parent.show()
        #self.set_depth(100)
        #self.tex1.set_depth(100)
        #self.set_opacity(255)
        self.frontTex = self.tex1
        self.tex1.show()
        self.show()
        #parent.add(self)
        self.timeline.start()
        
    def get_rand_tex(self):
        rand = random.randint(0, len(self.textures)-1)
        
        texture = clutter.Texture()
        pixbuf = gtk.gdk.pixbuf_new_from_file(self.textures[rand])
        texture.set_pixbuf(pixbuf)
        xy_ratio = float(texture.get_width()) / texture.get_height()
        #texture.set_height(self.get_height())
        width = int(texture.get_height() * xy_ratio)
        #texture.set_width(width)
        return texture
        
    def next_image(self, data):
        texture = self.get_rand_tex()
        self.add(texture)
        
        
        #Remove the old texture
        self.remove(self.frontTex)
        
        #Setup the path behaviour specific to this tex
        knots = self.get_texture_knots(texture)
        
        #Set the appropriate tex
        if self.frontTex == self.tex1:
            self.tex1 = texture
            self.behave1 = clutter.BehaviourPath(self.alpha, knots)
            currentBehave = self.behave1
            self.frontTex = self.tex2
            
            #texture.lower(self.tex2)
            #texture.lower(self.tex3)
            
        elif self.frontTex == self.tex2:
            self.tex2 = texture
            self.behave2 = clutter.BehaviourPath(self.alpha, knots)
            currentBehave = self.behave2
            self.frontTex = self.tex3
            
            #texture.lower(self.tex1)
            #texture.lower(self.tex3)
            
        elif self.frontTex == self.tex3:
            self.tex3 = texture
            self.behave3 = clutter.BehaviourPath(self.alpha, knots)
            currentBehave = self.behave3
            self.frontTex = self.tex1
            
            #texture.lower(self.tex1)
            #texture.lower(self.tex2)
        
        currentBehave.apply(texture)
        
        texture.show()
        
    def get_texture_knots(self, texture):
        knots = (\
                (0, 0),\
                #(int(self.get_width()*0.2), int(self.get_height()*0.2)),\
                #(int(self.stage.get_width()*0.1), int(self.stage.get_height()*0.1)),\
                (int(-texture.get_width()), int(self.get_height()*0.3))\
                )
        
        return knots
        