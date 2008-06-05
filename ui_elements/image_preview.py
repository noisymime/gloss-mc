import clutter
import pygtk
import gtk
import gobject
import random
import math
from ReflectionTexture import Texture_Reflection
from ui_elements.image_frame import ImageFrame

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
    
    #These are just defaults incase whatever uses image previewer forgets to set them
    max_img_width = 400
    max_img_height = 400
    
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
        self.connect('hide', self.stop)
        
        self.alpha1 = clutter.Alpha(self.timeline1, clutter.ramp_inc_func)
        self.alpha2 = clutter.Alpha(self.timeline2, clutter.ramp_inc_func)
        self.alpha3 = clutter.Alpha(self.timeline3, clutter.ramp_inc_func)
        
        #self.behaviour_scale = clutter.BehaviourScale(x_scale_start=self.scale_start, y_scale_start=self.scale_start, x_scale_end=1, y_scale_end=1, alpha=self.alpha)
        self.behaviour_depth1 = clutter.BehaviourDepth(depth_start=-800, depth_end=200, alpha=self.alpha1)
        self.behaviour_depth2 = clutter.BehaviourDepth(depth_start=-800, depth_end=200, alpha=self.alpha2)
        self.behaviour_depth3 = clutter.BehaviourDepth(depth_start=-800, depth_end=200, alpha=self.alpha3)
        
    #This max boundaries for the preview image size
    def set_max_img_dimensions(self, width, height):
        self.max_img_width = width
        self.max_img_height = height
    
    def add_texture(self, texture_src):
        #Determine the largest size for the image
        if self.max_img_height > self.max_img_width:
            img_size = self.max_img_height
        else:
            img_size = self.max_img_width
        
        try:
            pixbuf = gtk.gdk.pixbuf_new_from_file(texture_src)
            texture = ImageFrame(pixbuf, img_size, use_reflection = True, quality = ImageFrame.QUALITY_FAST)
            self.textures.append(texture)
        except gobject.GError, e:
            print "Could not load file: %s" % texture_src
    
    def start(self, data):
        if len(self.textures) == 0:
            return None
        
        #Check if this previewer has already run before
        if self.tex1 is None:
            self.tex1 = self.get_rand_tex()
            self.tex2 = self.get_rand_tex()
            self.tex3 = self.get_rand_tex()
            
            self.behave1 = clutter.BehaviourPath(self.alpha1, self.get_texture_knots(self.tex1))
            self.behave2 = clutter.BehaviourPath(self.alpha2, self.get_texture_knots(self.tex2))
            self.behave3 = clutter.BehaviourPath(self.alpha3, self.get_texture_knots(self.tex3))
            
            self.behaviour_rotate1 = clutter.BehaviourRotate(axis=clutter.Y_AXIS, direction=clutter.ROTATE_CCW, angle_start=0, angle_end=270, alpha=self.alpha1)
            self.behaviour_rotate2 = clutter.BehaviourRotate(axis=clutter.Y_AXIS, direction=clutter.ROTATE_CCW, angle_start=0, angle_end=270, alpha=self.alpha2)
            self.behaviour_rotate3 = clutter.BehaviourRotate(axis=clutter.Y_AXIS, direction=clutter.ROTATE_CCW, angle_start=0, angle_end=270, alpha=self.alpha3)
            
            #self.tex1.set_scale(self.scale_start, self.scale_start)Path
            self.behaviour_depth1.apply(self.tex1)
            self.behave1.apply(self.tex1)
            self.behaviour_rotate1.apply(self.tex1)
            
            self.behaviour_depth2.apply(self.tex2)
            self.behave2.apply(self.tex2)
            self.behaviour_rotate2.apply(self.tex2)
            
            self.behaviour_depth3.apply(self.tex3)
            self.behave3.apply(self.tex3)
            self.behaviour_rotate3.apply(self.tex3)
            
            #Special opacity behaviour to brin ghte fist texture in
            timeline_opacity = clutter.Timeline(20, self.fps)
            alpha_opacity = clutter.Alpha(timeline_opacity, clutter.ramp_inc_func)
            self.behaviour_opacity = clutter.BehaviourOpacity(opacity_start=0, opacity_end=255, alpha=alpha_opacity)
            self.tex1.set_opacity(0)
            self.behaviour_opacity.apply(self.tex1)
            
        
            if self.text1.get_parent() is None: self.add(self.tex1)
            
            parent = self.get_parent()
            if parent is None:
                print "Parent is none!"
            
            parent.show()
            self.frontTex = self.tex1
            self.tex1.show()
            self.show()
            self.timeline1.start()
            timeline_opacity.start()
            #gobject.idle_add(self.get_next_tex)
            self.nextTexture = self.get_rand_tex()
        else:
            self.timeline1.start()
            self.timeline2.start()
            self.timeline3.start()
        
    #This starts the various timelines at the appropriate points
    def kickoff(self, timeline, frame_no):
        if frame_no == (math.floor(self.fps*self.seconds/3)) or frame_no == (2*math.floor(self.fps*self.seconds/3)):
            if timeline == self.timeline1:
                self.add(self.tex2)
                self.tex2.set_opacity(0)
                self.tex2.show()
                self.timeline2.start()
                self.timeline1.disconnect(self.handler_id1)
                self.handler_id1 = None
                
                fade_template = clutter.EffectTemplate( clutter.Timeline(20, self.fps), clutter.ramp_inc_func)
                effect = clutter.effect_fade(template=fade_template, actor=self.tex2, opacity_end=255)
                effect.start()
                
            if timeline == self.timeline2:
                self.add(self.tex3)
                self.tex3.set_opacity(0)
                self.tex3.show()
                self.timeline3.start()
                self.timeline2.disconnect(self.handler_id2)
                self.handler_id2 = None
            
                fade_template = clutter.EffectTemplate( clutter.Timeline(20, self.fps), clutter.ramp_inc_func)
                effect = clutter.effect_fade(template=fade_template, actor=self.tex3, opacity_end=255)
                effect.start()
        
    def get_rand_tex(self):
        rand = random.randint(0, len(self.textures)-1)
        return self.textures[rand]
    
    def get_next_tex(self):
        self.nextTexture = self.get_rand_tex()
        return False
        
        
    def next_image(self, data):
        texture = self.nextTexture
        
        
        
        #Remove the old texture
        if not self.frontTex.get_parent() is None:
            self.frontTex.get_parent().remove(self.frontTex)
        
        
        #Setup the path behaviour specific to this tex
        knots = self.get_texture_knots(texture)
        
        #Set the appropriate tex
        if self.frontTex == self.tex1:
            self.tex1 = texture
            self.behave1 = clutter.BehaviourPath(self.alpha1, knots)
            self.behave1.apply(self.tex1)
            self.behaviour_depth1.remove_all()
            self.behaviour_rotate1.remove_all()
            self.behaviour_depth1.apply(self.tex1)
            self.behaviour_rotate1.apply(self.tex1)
            
            #self.frontTex.unrealize()
            #self.frontTex.destroy()
            self.frontTex = self.tex2
            
        elif self.frontTex == self.tex2:
            self.tex2 = texture
            self.behave2 = clutter.BehaviourPath(self.alpha2, knots)
            self.behave2.apply(self.tex2)
            self.behaviour_depth2.remove_all()
            self.behaviour_rotate2.remove_all()
            self.behaviour_depth2.apply(self.tex2)
            self.behaviour_rotate2.apply(self.tex2)
            
            #self.frontTex.unrealize()
            #self.frontTex.destroy()
            self.frontTex = self.tex3
            
        elif self.frontTex == self.tex3:
            self.tex3 = texture
            self.behave3 = clutter.BehaviourPath(self.alpha3, knots)
            self.behave3.apply(self.tex3)
            self.behaviour_depth3.remove_all()
            self.behaviour_rotate3.remove_all()
            self.behaviour_depth3.apply(self.tex3)
            self.behaviour_rotate3.apply(self.tex3)
            
            #self.frontTex.unrealize()
            #self.frontTex.destroy()
            self.frontTex = self.tex1
            
        #Special opacity behaviour to bring texture in
        timeline_opacity = clutter.Timeline(20, self.fps)
        alpha_opacity = clutter.Alpha(timeline_opacity, clutter.ramp_inc_func)
        self.behaviour_opacity = clutter.BehaviourOpacity(opacity_start=0, opacity_end=255, alpha=alpha_opacity)
        texture.set_opacity(0)
        self.behaviour_opacity.apply(texture)
        timeline_opacity.start()
        
        if texture.get_parent() is None: self.add(texture)
        texture.show()
        #gobject.idle_add(self.get_next_tex)
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
    
    def stop(self, data):
        self.timeline1.pause()
        self.timeline2.pause()
        self.timeline3.pause()
        