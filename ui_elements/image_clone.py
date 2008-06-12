import pygtk
import gtk
import clutter
from ui_elements.image_frame import ImageFrame

########################################################
# A simple class that copies all of an images properties 
# and returns an ImageFrame.
# Note: The location of the texture being cloned is set to absolute rather than relative to any parent
########################################################
class ImageClone(ImageFrame):
    
    
    def __init__(self, texture = None, img_frame = None):
        use_reflection = False
        if not img_frame is None:
            pixbuf = img_frame.orig_pixbuf
            texture = img_frame
            (width, height) = img_frame.main_pic.get_abs_size()
            if height > width:
                size = height
            else:
                size = width
            size = img_frame.img_size
            (anchor_x, anchor_y) = img_frame.get_anchor_point()
            use_reflection = img_frame.use_reflection
            opacity = img_frame.get_opacity()
            (abs_x, abs_y) = img_frame.main_pic.get_abs_position()
        else:
            pixbuf = texture.get_pixbuf()
            (width, height) = texture.get_abs_size()
            if height > width:
                size = height
            else:
                size = width
            (anchor_x, anchor_y) = texture.get_anchor_point()
            opacity = texture.get_opacity()
            (abs_x, abs_y) = texture.get_abs_position()
            
        ImageFrame.__init__(self, pixbuf, size, use_reflection = use_reflection)
        #self.set_anchor_point(anchor_x, anchor_y)
        #clutter.CloneTexture.__init__(self, texture)
        
        #(width, height) = texture.get_abs_size()
        #self.set_size(width, height)
        self.set_opacity(opacity)
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
        
        #if texture.has_clip(): self.set_clip(texture.get_clip())
        