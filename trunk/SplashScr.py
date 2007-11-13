import pygtk
import gtk
import pygst
import gst
import gobject
import pango
import clutter
from Spinner import Spinner

class SplashScr():
    font = "Lucida Grande "
    message_font_size = 30
    detail_font_size = 22
    
    def __init__(self, stage):
        self.stage = stage
        
        self.backdrop = clutter.Rectangle()
        self.backdrop.set_color(clutter.color_parse('Black'))
        self.backdrop.set_width(self.stage.get_width())
        self.backdrop.set_height(self.stage.get_height())


        self.main_group = clutter.Group()
        
        pixbuf = gtk.gdk.pixbuf_new_from_file("ui/splash_box.png")
        self.box = clutter.Texture()
        self.box.set_pixbuf(pixbuf)
        self.box.set_opacity(int(255 * 0.75))
        self.box.set_height(int(self.stage.get_height()* 0.15))
        self.main_group.add(self.box)
       
        self.spinner = Spinner()
        height = int(self.box.get_height() * 0.90)
        height = height + (height % 2) # Make sure that the dimension is even
        self.spinner.set_height(height)
        self.spinner.set_width(height)
        self.spinner.set_position(5, int(self.box.get_height() * 0.05 ) )
        self.main_group.add(self.spinner)

        self.message = clutter.Label()
        self.message.set_font_name(self.font + str(self.message_font_size))
        self.message.set_color(clutter.color_parse('White'))
        pos_x = self.spinner.get_x()
        pos_x = pos_x + int (self.spinner.get_width() * 1.1)
        self.message.set_position(pos_x, 0)
        self.message.set_text("Loading...")
        self.main_group.add(self.message)
        
        self.detail = clutter.Label()
        self.detail.set_font_name(self.font + str(self.detail_font_size))
        self.detail.set_color(clutter.color_parse('White'))
        self.main_group.add(self.detail)
        
        
    def display(self):
        self.stage.add(self.backdrop)
        self.backdrop.show()
        
        self.stage.add(self.main_group)
        self.main_group.show_all()
        group_x = (self.stage.get_width()/2) - (self.box.get_width()/2)
        group_y = (self.stage.get_height()/2) - (self.box.get_height()/2)
        self.main_group.set_position(group_x, group_y)
        self.main_group.show()
        
        self.spinner.start()
    
    def remove(self):
        self.stage.remove(self.main_group)
        self.stage.remove(self.backdrop)
        self.spinner.stop()
        
        
    def set_msg(self, msg):
        self.message.set_text(msg)
        
    def set_details(self, detail):
        self.detail.set_test(detail)
        
        
        