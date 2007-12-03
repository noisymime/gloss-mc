import pygtk
import gtk
import pango
import clutter

class cover_item(clutter.Group):
    font = "Lucida Grande "
    title_font_size = 30
    main_font_size = 22
    plot_font_size = 18
    
    def __init__(self, video, folder_name, cover_size):
        clutter.Group.__init__(self)
        self.width = cover_size
        self.height = cover_size
        
        #Set whether or not this is a folder or a video cover
        if not folder_name is None:
            imagePath = "ui/mv_gallery_folder_sel.png"
            pixbuf = gtk.gdk.pixbuf_new_from_file(imagePath)
            self.isFolder = True
        else:
            imagePath = video.getCoverfile()
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
        else:
            xy_ratio = float(self.main_pic.get_height()) / float(self.main_pic.get_width())
            self.main_pic.set_width(cover_size)
            height = int(cover_size * xy_ratio)
            self.main_pic.set_height(height)
            y = y + (cover_size - height)/2
            
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