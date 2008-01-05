import clutter
import gtk

class Spinner (clutter.Texture):
    
    def __init__(self):
        clutter.Texture.__init__ (self)
        
        #self.texture = clutter.Texture()
        pixbuf = gtk.gdk.pixbuf_new_from_file("ui/spinner.svg")
        self.set_pixbuf(pixbuf)
     
    def start(self):  
        self.timeline = clutter.Timeline(40,20)
        self.timeline.set_loop(True)
        alpha = clutter.Alpha(self.timeline, clutter.ramp_inc_func)
        self.spin_behaviour = clutter.BehaviourRotate( axis=clutter.Z_AXIS , direction=clutter.ROTATE_CW, angle_start=0, angle_end=359, alpha=alpha)
        self.spin_behaviour.set_center(self.get_width()/2,self.get_height()/2, 0) 
        self.spin_behaviour.apply(self)
        self.timeline.start()
        
    def stop(self):
        self.timeline.stop()
