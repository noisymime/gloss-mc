import clutter
import gtk

class Spinner (clutter.Texture):
    
    def __init__(self):
        clutter.Texture.__init__ (self)
        
        #self.texture = clutter.Texture()
        pixbuf = gtk.gdk.pixbuf_new_from_file("ui/spinner.svg")
        self.set_pixbuf(pixbuf)
        
        timeline = clutter.Timeline(40,20)
        timeline.set_loop(True)
        alpha = clutter.Alpha(timeline, clutter.ramp_inc_func)
        spin_behaviour = clutter.BehaviourRotate(alpha, clutter.Z_AXIS, clutter.ROTATE_CW, 0, 359)
        spin_behaviour.set_center(self.get_width()/2,self.get_height()/2, 0) 
        spin_behaviour.apply(self)
        
        timeline.start()