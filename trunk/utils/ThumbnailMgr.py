#Given a directory, file and size, the thumbnail mgr looks for a pre-created thumbnail
#of the correct size. 
#If it can't find it, it will create it and save it in a .thumbnails directory

import os
import gobject
import pygtk
import gtk
from ui_elements.image_frame import ImageFrame

class ThumbnailMgr():
    
    thumbnails_directory_name = ".thumbnails"
    thumbnail_file_type = "jpg"
    
    def __init__(self):
        pass
    
    def get_image_frame(self, file_src, size):
        
        thumb_file = self.get_thumbnail_file_src(file_src, size)
        #Check if the thumbnail file already exists
        if os.path.exists(thumb_file):
            pixbuf = gtk.gdk.pixbuf_new_from_file(thumb_file)
            img_frame = ImageFrame(pixbuf, size)
        else:
            pixbuf = gtk.gdk.pixbuf_new_from_file(file_src)
            img_frame = ImageFrame(pixbuf, size)
            pixbuf = img_frame.pixbuf
            self.save_thumbnail_file(thumb_file, pixbuf)
            
        return img_frame
    
    def get_pixbuf(self, file_src, size):
        thumb_file = self.get_thumbnail_file_src(file_src, size)
        #Check if the thumbnail file already exists
        if os.path.exists(thumb_file):
            pixbuf = gtk.gdk.pixbuf_new_from_file(thumb_file)
            img_frame = ImageFrame(pixbuf, size)
        else:
            pixbuf = gtk.gdk.pixbuf_new_from_file(file_src)
            img_frame = ImageFrame(pixbuf, size)
            pixbuf = img_frame.pixbuf
            self.save_thumbnail_file(thumb_file, pixbuf)
            
        return pixbuf
    
    def get_thumbnail_file_src(self, file_src, size):
        (dir, sep, file) = file_src.rpartition("/")
        (filename, dot, extension) = file.rpartition(".")
        extension = "png"
        thumb_file = dir + sep + self.thumbnails_directory_name + sep + filename + str(size) + dot + self.thumbnail_file_type
        
        return thumb_file
        
    #Saves a pixbuf back to the thumbnail file
    def save_thumbnail_file(self, file_src, pixbuf):
        (dir, sep, file) = file_src.rpartition("/")
        #Check to make sure the above directory exists
        if not os.path.isdir(dir):
            try:
                os.makedirs(dir, int('777',8))
            except OSError:
                print "Thumbnail Mgr Error: Unable to write to thumbnail directory '%s'" % (dir)
                return
        
        #And create the file
        try:
            pixbuf.save(file_src, "jpeg")
        except gobject.GError, e:
            print "Thumbnail Mgr: Cannot write thumbnail image '%s'" % file_src