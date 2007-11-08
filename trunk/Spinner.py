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
        self.spin_behaviour = clutter.BehaviourRotate(alpha, clutter.Z_AXIS, clutter.ROTATE_CW, 0, 359)
        self.spin_behaviour.set_center(self.get_width()/2,self.get_height()/2, 0) 
        self.spin_behaviour.apply(self)
        self.timeline.start()
        
    def stop(self):
        self.timeline.stop()
