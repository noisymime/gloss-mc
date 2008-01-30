import clutter
import pygtk
import gtk
import random
import math
from ReflectionTexture import Texture_Reflection

class image_previewer(clutter.Group):
    tex1 = None
    tex2 = None
    tex3 = None
    frontTex = None
    behave1 = None
    behave2 = None
    behave3 = None
    
    scale_start = 0.6
    seconds = 8
    fps = 25
    
    def __init__(self, stage):
        clutter.Group.__init__(self)
        self.textures = []
        self.stage = stage
        
        self.timeline1 = clutter.Timeline((self.seconds*self.fps), self.fps)
        self.timeline1.set_loop(True)
        self.timeline1.connect('completed', self.next_image)
        self.handler_id1 = self.timeline1.connect('new-frame', self.kickoff)
        
        self.timeline2 = clutter.Timeline((self.seconds*self.fps), self.fps)
        self.timeline2.set_loop(True)
        self.timeline2.connect('completed', self.next_image)
        self.handler_id2 = self.timeline2.connect('new-frame', self.kickoff)
        
        self.timeline3 = clutter.Timeline((self.seconds*self.fps), self.fps)
        self.timeline3.set_loop(True)
        self.timeline3.connect('completed', self.next_image)
        self.timeline3.connect('new-frame', self.kickoff)
        
        self.connect('show', self.start)
        
        self.alpha1 = clutter.Alpha(self.timeline1, clutter.ramp_inc_func)
        self.alpha2 = clutter.Alpha(self.timeline2, clutter.ramp_inc_func)
        self.alpha3 = clutter.Alpha(self.timeline3, clutter.ramp_inc_func)
        
        #self.behaviour_scale = clutter.BehaviourScale(x_scale_start=self.scale_start, y_scale_start=self.scale_start, x_scale_end=1, y_scale_end=1, alpha=self.alpha)
        self.behaviour_depth1 = clutter.BehaviourDepth(depth_start=-800, depth_end=200, alpha=self.alpha1)
        self.behaviour_depth2 = clutter.BehaviourDepth(depth_start=-800, depth_end=200, alpha=self.alpha2)
        self.behaviour_depth3 = clutter.BehaviourDepth(depth_start=-800, depth_end=200, alpha=self.alpha3)
        
        
    def add_texture(self, texture_src):
        self.textures.append(texture_src)
    
    def start(self, data):
        if len(self.textures) == 0:
            return None
        
        self.tex1 = self.get_rand_tex()
        self.tex2 = self.get_rand_tex()
        self.tex3 = self.get_rand_tex()
        
        self.behave1 = clutter.BehaviourPath(self.alpha1, self.get_texture_knots(self.tex1))
        self.behave2 = clutter.BehaviourPath(self.alpha2, self.get_texture_knots(self.tex2))
        self.behave3 = clutter.BehaviourPath(self.alpha3, self.get_texture_knots(self.tex3))
        
        #self.tex1.set_scale(self.scale_start, self.scale_start)
        self.behaviour_depth1.apply(self.tex1)
        self.behave1.apply(self.tex1)
        self.behaviour_depth2.apply(self.tex2)
        self.behave2.apply(self.tex2)
        self.behaviour_depth3.apply(self.tex3)
        self.behave3.apply(self.tex3)
        
        #Special opacity behaviour to brin ghte fist texture in
        timeline_opacity = clutter.Timeline(20, self.fps)
        alpha_opacity = clutter.Alpha(timeline_opacity, clutter.ramp_inc_func)
        self.behaviour_opacity = clutter.BehaviourOpacity(opacity_start=0, opacity_end=255, alpha=alpha_opacity)
        self.tex1.set_opacity(0)
        self.behaviour_opacity.apply(self.tex1)
        
        
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
        self.timeline1.start()
        timeline_opacity.start()
        self.nextTexture = self.get_rand_tex()
        
    #This starts the various timelines at the appropriate points
    def kickoff(self, timeline, frame_no):
        if frame_no == (math.floor(self.fps*self.seconds/3)) or frame_no == (2*math.floor(self.fps*self.seconds/3)):
            if timeline == self.timeline1:
                self.add(self.tex2)
                self.tex2.show()
                self.timeline2.start()
                self.timeline1.disconnect(self.handler_id1)
                self.handler_id1 = None
            if timeline == self.timeline2:
                self.add(self.tex3)
                self.tex3.show()
                self.timeline3.start()
                self.timeline2.disconnect(self.handler_id2)
                self.handler_id2 = None
            
        
        
    def get_rand_tex(self):
        rand = random.randint(0, len(self.textures)-1)
        
        texture = clutter.Texture()
        pixbuf = gtk.gdk.pixbuf_new_from_file(self.textures[rand])
        texture.set_pixbuf(pixbuf)
        xy_ratio = float(texture.get_width()) / texture.get_height()
        #texture.set_height(self.get_height())
        width = int(texture.get_height() * xy_ratio)
        reflectionTexture = Texture_Reflection(texture)
        
        textureGroup = clutter.Group()
        textureGroup.add(texture)
        textureGroup.add(reflectionTexture)
        texture.show()
        reflectionTexture.show()
        #texture.set_width(width)
        return textureGroup
        
    def next_image(self, data):
        texture = self.nextTexture
        
        
        #Remove the old texture
        self.remove(self.frontTex)
        
        #Setup the path behaviour specific to this tex
        knots = self.get_texture_knots(texture)
        
        #Set the appropriate tex
        if self.frontTex == self.tex1:
            self.tex1 = texture
            self.behave1 = clutter.BehaviourPath(self.alpha1, knots)
            self.behave1.apply(self.tex1)
            self.behaviour_depth1.apply(self.tex1)
            self.frontTex = self.tex2
            
            #texture.lower(self.tex2)
            #texture.lower(self.tex3)
            
        elif self.frontTex == self.tex2:
            self.tex2 = texture
            self.behave2 = clutter.BehaviourPath(self.alpha2, knots)
            self.behave2.apply(self.tex2)
            self.behaviour_depth2.apply(self.tex2)
            self.frontTex = self.tex3
            
        elif self.frontTex == self.tex3:
            self.tex3 = texture
            self.behave3 = clutter.BehaviourPath(self.alpha3, knots)
            self.behave3.apply(self.tex3)
            self.behaviour_depth3.apply(self.tex3)
            self.frontTex = self.tex1
            
            #texture.lower(self.tex1)
            #texture.lower(self.tex2)
            
        #Special opacity behaviour to bring texture in
        timeline_opacity = clutter.Timeline(20, self.fps)
        alpha_opacity = clutter.Alpha(timeline_opacity, clutter.ramp_inc_func)
        self.behaviour_opacity = clutter.BehaviourOpacity(opacity_start=0, opacity_end=255, alpha=alpha_opacity)
        texture.set_opacity(0)
        self.behaviour_opacity.apply(texture)
        timeline_opacity.start()
        
        self.add(texture)
        texture.show()
        self.nextTexture = self.get_rand_tex()
        
    def get_texture_knots(self, texture):
        knots = (\
                (0, 0),\
                #(int(self.get_width()*0.2), int(self.get_height()*0.2)),\
                #(int(self.stage.get_width()*0.1), int(self.stage.get_height()*0.1)),\
                #int(self.get_height()*0.3))\
                (int(-texture.get_width()), 0)\
                )
        
        return knots
        