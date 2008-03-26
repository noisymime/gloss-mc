import cairo
import clutter
import gtk
from clutter.cluttercairo import CairoTexture


class Texture_Reflection (CairoTexture):

    def __init__(self, origTexture, reflection_height = 0.5, opacity = 0.9):
        #clutter.Texture.__init__(self)
        CairoTexture.__init__(self, origTexture.get_width(), origTexture.get_height())
        
        #Connect to the textures pixbuf-change signal so the reflection will auto update
        origTexture.connect("pixbuf-change", self.update_pixbuf)
        self.reflection_height = reflection_height
        self.opacity = opacity
        
        if origTexture.get_pixbuf() is None:
            return None
        
        #self.set_size(origTexture.get_width(), origTexture.get_height())
        #self.set_pixbuf(origTexture.get_pixbuf())
        
        self.update_pixbuf(origTexture)

    def update_pixbuf(self, origTexture):
        context = self.cairo_create()
        ct = gtk.gdk.CairoContext(context)
        
        self.gradient = cairo.LinearGradient(0, 0, 0, origTexture.get_pixbuf().get_height())
        self.gradient.add_color_stop_rgba(1 - self.reflection_height, 1, 1, 1, 0)
        self.gradient.add_color_stop_rgba(1, 0, 0, 0, self.opacity)

        ct.set_source_pixbuf(origTexture.get_pixbuf(),0,0)
        context.mask(self.gradient)

        del context # Update texture
        del ct
        
        #Rotate the reflection based on any rotations to the master
        ang_y = origTexture.get_rotation(clutter.Y_AXIS) #ryang()
        self.set_rotation(clutter.Y_AXIS, ang_y[0], (origTexture.get_width()), 0, 0)
        ang_x = origTexture.get_rotation(clutter.X_AXIS)
        self.set_rotation(clutter.X_AXIS, ang_x[0], 0, (origTexture.get_height()), 0)
        #ang_z = origTexture.get_rotation(clutter.Z_AXIS)
        #self.set_rotation(clutter.Z_AXIS, ang_z[0], 0, 0, 0)
        
        (w, h) = origTexture.get_size()
        self.set_width(w)
        self.set_height(h)
        
        #Flip it upside down
        self.set_rotation(clutter.X_AXIS, 180, 0, origTexture.get_height(), 0)
        self.set_opacity(50)

        #Get/Set the location for it               
        (x, y) = origTexture.get_position()
        self.set_position(x, y)
        
        
        """
        self.set_pixbuf(origTexture.get_pixbuf())
        
        #Rotate the reflection based on any rotations to the master
        ang_y = origTexture.get_rotation(clutter.Y_AXIS) #ryang()
        self.set_rotation(clutter.Y_AXIS, ang_y[0], (origTexture.get_width()), 0, 0)
        ang_x = origTexture.get_rotation(clutter.X_AXIS)
        self.set_rotation(clutter.X_AXIS, ang_x[0], 0, (origTexture.get_height()), 0)
        #ang_z = origTexture.get_rotation(clutter.Z_AXIS)
        #self.set_rotation(clutter.Z_AXIS, ang_z[0], 0, 0, 0)
        
        (w, h) = origTexture.get_size()
        self.set_width(w)
        self.set_height(h)
        
        #Flip it upside down
        self.set_rotation(clutter.X_AXIS, 180, 0, origTexture.get_height(), 0)
        self.set_opacity(50)

        #Get/Set the location for it               
        (x, y) = origTexture.get_position()
        self.set_position(x, y)
        """