import pygtk
import gtk
import pango
import cluttergtk
import clutter
import os
from ui_elements.ReflectionTexture import Texture_Reflection

class ImageFrame(clutter.Group):
    QUALITY_FAST, QUALITY_NORMAL, QUALITY_SLOW = range(3)
    quality = QUALITY_NORMAL
    orig_pixbuf = None
    
    def __init__(self, pixbuf, img_size, use_reflection = False, quality = QUALITY_NORMAL, anchor = None):
        clutter.Group.__init__(self)
        self.width = img_size
        self.height = img_size
        self.img_size = img_size
        self.use_reflection = use_reflection
        self.quality = quality
        self.orig_pixbuf = pixbuf
        
        
        self.main_pic = cluttergtk.Texture()
        self.reflection = None
        #self.reflection = Texture_Reflection(self.main_pic)

        self.set_from_pixbuf(pixbuf)               
        self.add(self.main_pic)
        
    def resize_pixbuf(self, pixbuf):
        #New method of resizing changes size of pixbuf rather than texture.... MUCH better performance :)
        (self.x, self.y) = (0, 0)
        if pixbuf.get_height() > pixbuf.get_width():
            xy_ratio = float(pixbuf.get_width()) / pixbuf.get_height()
            height = self.img_size
            width = int(self.img_size * xy_ratio)
            self.x = (self.img_size - width)/2
            #x = int(cover_size / 2)
            #x = x + (cover_size - width)
        else:
            xy_ratio = float(pixbuf.get_height()) / float(pixbuf.get_width())
            width = self.img_size
            height = int(self.img_size * xy_ratio)
            self.y = (self.img_size - height)/2
            #y = y + (cover_size - height)
        
        #Set the conversion mode / quality
        if self.quality == self.QUALITY_FAST: conversion_mode = gtk.gdk.INTERP_NEAREST #gtk.gdk.INTERP_TILES
        elif self.quality == self.QUALITY_NORMAL: conversion_mode = gtk.gdk.INTERP_BILINEAR
        elif self.quality == self.QUALITY_SLOW: conversion_mode = gtk.gdk.INTERP_HYPER
        
        #Check to see whether the dimensions are already within 10% of the new ones
        """
        height_max = int(pixbuf.get_height() * 1.1)
        height_min = int(pixbuf.get_height() * 0.9)
        width_max  = int(pixbuf.get_width() * 1.1)
        width_min  = int(pixbuf.get_width() * 0.9)
        #If not, perform the resize
        if ((height < height_max) and (height > height_min)) or ((width < width_max) and (width > width_min)):
        #Changed my mind, it has to be the exact right size
        """
        if (height == pixbuf.get_height()) or (width == pixbuf.get_width()):
            return pixbuf
        else:         
            pixbuf = pixbuf.scale_simple(width, height, conversion_mode)
        
        return pixbuf
        
    def set_from_pixbuf(self, pixbuf):
        self.orig_pixbuf = pixbuf
        if pixbuf is None:
            self.main_pic.hide()
            if not self.reflection is None: self.reflection.hide()
            return
        else:
            self.pixbuf = self.resize_pixbuf(pixbuf)
            self.main_pic.set_from_pixbuf(self.pixbuf)
            self.main_pic.set_position(self.x, self.y)
            self.main_pic.show()
        
        #For the most part the Reflection texture automatically takes car of pixbuf changes
        #So we only need to set the flection the first time arouns (ie self.reflection is None)
        if self.use_reflection:
            self.set_reflection(True)               
        else:
            self.reflection = None
    
    #Turns reflections on and off
    def set_reflection(self, toggle):
        #If the current state is the requested state, do nothing
        if self.reflection == toggle:
            return
        
        self.use_reflection = toggle
        if self.use_reflection:
            if not self.reflection is None:
                self.remove(self.reflection)
                self.reflection = None
            self.reflection = Texture_Reflection(self.main_pic)
            self.add(self.reflection)
            self.reflection.show()
        else:
            self.remove(self.reflection)
            self.reflection = None
        
    def get_texture(self):
        return self.main_pic
    
    def get_width(self):
        return self.img_size
    def get_height(self):
        return self.img_size