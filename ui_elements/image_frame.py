import pygtk
import gtk
import pango
import clutter
import os
from ui_elements.ReflectionTexture import Texture_Reflection

class ImageFrame(clutter.Group):
    
    def __init__(self, pixbuf, img_size, use_reflection = False):
        clutter.Group.__init__(self)
        self.width = img_size
        self.height = img_size
        
        self.main_pic = clutter.Texture()

        #New method of resizing changes size of pixbuf rather than texture.... MUCH better performance :)
        (x, y) = (0, 0)
        if pixbuf.get_height() > pixbuf.get_width():
            xy_ratio = float(pixbuf.get_width()) / pixbuf.get_height()
            height = img_size
            width = int(img_size * xy_ratio)
            x = (img_size - width)/2
            #x = int(cover_size / 2)
            #x = x + (cover_size - width)
        else:
            xy_ratio = float(pixbuf.get_height()) / float(pixbuf.get_width())
            width = img_size
            height = int(img_size * xy_ratio)
            y = (img_size - height)/2
            #y = y + (cover_size - height)
        pixbuf = pixbuf.scale_simple(width, height, gtk.gdk.INTERP_BILINEAR)
        self.main_pic.set_pixbuf(pixbuf)
        self.main_pic.show()        
        

        #If a reflection is desired, add it on
        if use_reflection:
            self.reflection = Texture_Reflection(self.main_pic)
            self.add(self.reflection)
            self.reflection.show()
        else:
            self.reflection = None
        
        self.main_pic.set_position(x, y)        
        self.add(self.main_pic)