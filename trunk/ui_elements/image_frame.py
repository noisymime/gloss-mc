import pygtk
import gtk
import pango
import clutter
import os

class ImageFrame(clutter.Group):
    
    def __init__(self, pixbuf, img_size):
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
        

        """
        #This just seems to keep changing in Clutter so I'll leave it here
        gap = (cover_size - self.main_pic.get_width())/2
        anchor_x = (cover_size - gap)/2 
        #anchor_x = cover_size/2
        gap = (cover_size - self.main_pic.get_height())/2
        anchor_y = (cover_size - gap)/2 
        #anchor_y = cover_size/2 #self.main_pic.get_height()/2
        self.set_anchor_point(anchor_x, anchor_y)
        #self.set_anchor_point_from_gravity(clutter.GRAVITY_CENTER)
        """ 
            
        
        self.main_pic.set_position(x, y)        
        self.add(self.main_pic)