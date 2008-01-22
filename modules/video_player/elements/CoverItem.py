import pygtk
import gtk
import pango
import clutter
import os

class cover_item(clutter.Group):
    font = "Lucida Grande "
    title_font_size = 30
    main_font_size = 22
    plot_font_size = 18
    
    def __init__(self, glossMgr, video, folder_name, cover_size):
        clutter.Group.__init__(self)
        self.width = cover_size
        self.height = cover_size
        
        #Set whether or not this is a folder or a video cover
        if not folder_name is None:
            element = glossMgr.themeMgr.search_docs("video_cover_viewer", "main").childNodes
            imagePath = "ui/" + glossMgr.themeMgr.currentTheme + "/" + glossMgr.themeMgr.find_child_value(element, "folder_img_src")
            pixbuf = gtk.gdk.pixbuf_new_from_file(imagePath)
            self.isFolder = True
        else:
            imagePath = video.getCoverfile()
            #Check that coverfile exists
            # In the future this will change so that the video is still included with a blank image
            if not os.path.exists(imagePath):
                element = glossMgr.themeMgr.search_docs("video_cover_viewer", "main").childNodes
                imagePath = "ui/" + glossMgr.themeMgr.currentTheme + "/" + glossMgr.themeMgr.find_child_value(element, "video_default_src")
                
            pixbuf = gtk.gdk.pixbuf_new_from_file(imagePath)
            self.isFolder = False
            self.video = video
        
        self.main_pic = clutter.Texture()
        self.main_pic.set_pixbuf(pixbuf)
        
        
        self.main_pic.show()
        (x, y) = (0, 0)
        if self.main_pic.get_height() > self.main_pic.get_width():
            xy_ratio = float(self.main_pic.get_width()) / self.main_pic.get_height()
            self.main_pic.set_height(cover_size)
            width = int(cover_size * xy_ratio)
            self.main_pic.set_width(width)
            x = x + (cover_size - width)/2
            #x = x + (cover_size - width)
        else:
            xy_ratio = float(self.main_pic.get_height()) / float(self.main_pic.get_width())
            self.main_pic.set_width(cover_size)
            height = int(cover_size * xy_ratio)
            self.main_pic.set_height(height)
            y = y + (cover_size - height)/2
            #y = y + (cover_size - height)
        

            
        #This just seems to keep changing in Clutter so I'll leave it here
        gap = (cover_size - self.main_pic.get_width())/2
        anchor_x = (cover_size - gap)/2 #cover_size/2
        gap = (cover_size - self.main_pic.get_height())/2
        anchor_y = (cover_size - gap)/2 #cover_size/2 #self.main_pic.get_height()/2
        self.set_anchor_point(anchor_x, anchor_y)
        #self.set_anchor_point_from_gravity(clutter.GRAVITY_CENTER)
        
        self.main_pic.set_position(x, y)        
            
        
        
        
        
        self.add(self.main_pic)
        
        #If this is a folder, we also add a title
        if not folder_name is None:
            self.add_label(folder_name)
        
    def add_label(self, label):
        #Adds a label in the centre of the item
        self.title = clutter.Label()
        self.title.set_font_name(self.font + str(self.title_font_size))
        self.title.set_color(clutter.color_parse('White'))
        self.title.set_text(label)
        if self.title.get_width() > self.get_width():
                self.title.set_width(self.get_width())
        
        #Add an ellipsis
        self.title.set_ellipsize(pango.ELLIPSIZE_END)
        #Centre the label
        y = (self.height - self.title.get_height())/2
        x = (self.width - self.title.get_width())/2
        self.title.set_position(x, y)
        
        self.title.show()
        self.add(self.title)