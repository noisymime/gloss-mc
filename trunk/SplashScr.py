import pygtk
import gtk
import pygst
import gst
import gobject
import pango
import clutter
from ui_elements.Spinner import Spinner
from ui_elements.rounded_rectangle import RoundedRectangle

class SplashScr(clutter.Group):
    font = "Lucida Grande "
    message_font_size = 30
    detail_font_size = 22
    
    def __init__(self, glossMgr):
        clutter.Group.__init__ (self)
        self.glossMgr = glossMgr
        self.stage = self.glossMgr.stage
        
        self.backdrop = clutter.Rectangle()
        self.backdrop.set_color(clutter.color_parse('Black'))
        self.backdrop.set_width(self.stage.get_width())
        self.backdrop.set_height(self.stage.get_height())
        self.add(self.backdrop)
        
        self.centre_group = clutter.Group()
        self.add(self.centre_group)
        
        #THIS NEEDS THEMING!!!
        width = int(self.stage.get_width()* 0.4)
        height = int(self.stage.get_height()* 0.15)
        self.box = RoundedRectangle(width, height, clutter.color_parse('White'))
        self.box.set_opacity(int(255 * 0.55))
        
        self.centre_group.add(self.box)        
       
        self.spinner = Spinner(self.glossMgr)
        height = int(self.box.get_height() * 0.90)
        height = height + (height % 2) # Make sure that the dimension is even
        self.spinner.set_height(height)
        self.spinner.set_width(height)
        self.spinner.set_position(5, int(self.box.get_height() * 0.05 ) )
        self.centre_group.add(self.spinner)

        self.message = clutter.Label()
        self.message.set_font_name(self.font + str(self.message_font_size))
        self.message.set_color(clutter.color_parse('White'))
        pos_x = self.spinner.get_x()
        pos_x = pos_x + int (self.spinner.get_width() * 1.1)
        self.message.set_position(pos_x, 0)
        self.message.set_text("Loading...")
        self.centre_group.add(self.message)
        
        self.detail = clutter.Label()
        self.detail.set_font_name(self.font + str(self.detail_font_size))
        self.detail.set_color(clutter.color_parse('White'))
        self.detail.set_position(\
                                 self.message.get_x(),\
                                 self.message.get_y() + self.message.get_height()\
                                 )
        self.centre_group.add(self.detail)
       
    def display(self):
        self.stage.add(self)
        self.backdrop.show()
        

        group_x = (self.stage.get_width()/2) - (self.box.get_width()/2)
        group_y = (self.stage.get_height()/2) - (self.box.get_height()/2)
        self.centre_group.set_position(group_x, group_y)
        self.centre_group.show_all()
        self.centre_group.show()
        
        self.show()
        self.show_all()
        self.set_opacity(255)
        self.centre_group.set_opacity(255)
        self.spinner.start()

    #Same as above, except fades everything in
    def display_elegant(self):
        self.set_opacity(0)
        self.stage.add(self)
        self.show_all()
        
        group_x = (self.stage.get_width()/2) - (self.box.get_width()/2)
        group_y = (self.stage.get_height()/2) - (self.box.get_height()/2)
        self.centre_group.set_position(group_x, group_y)
        self.centre_group.show_all()
        self.centre_group.show()
        
        timeline_opacity = clutter.Timeline(20, 25)
        alpha_opacity = clutter.Alpha(timeline_opacity, clutter.ramp_inc_func)
        self.behaviour_opacity = clutter.BehaviourOpacity(opacity_start=0, opacity_end=255, alpha=alpha_opacity)
        self.behaviour_opacity.apply(self)
        timeline_opacity.start()
        self.spinner.start()
    
    def remove(self, data=None):
        self.stage.remove(self)
        self.spinner.stop()
        
    def remove_elegant(self):
        timeline_opacity = clutter.Timeline(20, 25)
        timeline_opacity.connect("completed", self.remove)
        alpha_opacity = clutter.Alpha(timeline_opacity, clutter.ramp_inc_func)
        self.behaviour_opacity = clutter.BehaviourOpacity(opacity_start=255, opacity_end=0, alpha=alpha_opacity)
        self.behaviour_opacity.apply(self)
        timeline_opacity.start()       
        
        return timeline_opacity
        
    def set_msg(self, msg):
        self.message.set_text(msg)
        
        (x1, y1, x2, y2) = self.message.get_coords()
        if x2 > self.box.get_width():
            new_width = int(x2 * 1.10)
            self.box.set_width(new_width)
            
            new_x = int( (self.stage.get_width() - new_width) / 2 )
            self.centre_group.set_x(new_x)
        
    def set_details(self, detail):
        self.detail.set_text(detail)
        
        
        