import pygtk
import gtk
import clutter

########################################################
# A simple class that copies all of an images properties 
# and returns a clone texture.
########################################################
class ImageClone(clutter.CloneTexture):
    
    
    def __init__(self, texture):
        clutter.CloneTexture.__init__(self, texture)
        
        (width, height) = texture.get_abs_size()
        self.set_size(width, height)
        self.set_opacity(texture.get_opacity())
        (abs_x, abs_y) = texture.get_abs_position()
        self.set_position(abs_x, abs_y)
        
        """
        ang_y = texture.get_rotation(clutter.Y_AXIS)
        self.set_rotation(clutter.Y_AXIS, ang_y[0], (texture.get_width()), 0, 0)
        ang_x = texture.get_rotation(clutter.X_AXIS)
        self.set_rotation(clutter.X_AXIS, ang_x[0], 0, (texture.get_height()), 0)
        #ang_z = origTexture.get_rotation(clutter.Z_AXIS)
        #self.set_rotation(clutter.Z_AXIS, ang_z[0], 0, 0, 0
        """
        
        self.set_depth(texture.get_depth())
        (anchor_x, anchor_y) = texture.get_anchor_point()
        self.set_anchor_point(anchor_x, anchor_y)
        
        #if texture.has_clip(): self.set_clip(texture.get_clip())
        