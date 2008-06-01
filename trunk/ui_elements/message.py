import clutter
import pango
from ui_elements.rounded_rectangle import RoundedRectangle
from ui_elements.Spinner import Spinner

class Message():
    theme_dir = "themes"
    
    font = "Lucida Grande "
    message_font_size = 30
    detail_font_size = 22
    
    def __init__(self, glossMgr):
        self.glossMgr = glossMgr
        self.stage = glossMgr.stage
        self.active = False
        self.msgQueue = []
        
        self.backdrop = clutter.Rectangle()
        self.backdrop.set_color(clutter.color_parse('Black'))
        #self.backdrop.set_opacity(240)
        self.backdrop.set_width(self.stage.get_width())
        self.backdrop.set_height(self.stage.get_height())
        
        self.main_group = clutter.Group()
        
        """
        pixbuf = gtk.gdk.pixbuf_new_from_file(self.theme_dir + "/splash_box.png")
        self.box = clutter.Texture()
        self.box.set_pixbuf(pixbuf)
        self.box.set_opacity(int(255 * 0.75))
        self.box.set_height(int(self.stage.get_height()* 0.3))
        self.main_group.add(self.box)
        """
        
        width = int(self.stage.get_width()* 0.4)
        height = int(self.stage.get_height()* 0.3)
        self.box = RoundedRectangle(width, height, clutter.color_parse('White'))
        self.box.set_opacity(int(255 * 0.55))
        self.main_group.add(self.box)

        self.message = clutter.Label()
        self.message.set_font_name(self.font + str(self.message_font_size))
        self.message.set_color(clutter.color_parse('White'))
        pos_x = int(self.box.get_width() * 0.10)
        pos_y = int(self.box.get_height() * 0.10)
        self.message.set_position(pos_x, pos_y)
        width = int(self.box.get_width() * 0.80) #Width is 80% of the box, giving 10% gap each side
        self.message.set_width(width)
        self.message.set_ellipsize(pango.ELLIPSIZE_END)
        self.message.set_text("")
        self.main_group.add(self.message)
        
        self.detail = clutter.Label()
        self.detail.set_font_name(self.font + str(self.detail_font_size))
        self.detail.set_color(clutter.color_parse('White'))
        pos_x = self.message.get_x()
        pos_y = self.message.get_y() + self.message.get_height()
        self.detail.set_position(pos_x, pos_y)
        height = self.box.get_height() - pos_y
        self.detail.set_height(height)
        #self.detail.set_ellipsize(pango.ELLIPSIZE_END)
        self.main_group.add(self.detail)
        self.detail.set_line_wrap(True)
        
        group_x = (self.stage.get_width()/2) - (self.box.get_width()/2)
        group_y = (self.stage.get_height()/2) - (self.box.get_height()/2)
        self.main_group.set_position(group_x, group_y)

    def display_msg(self, title, text):
        if self.active:
            self.msgQueue.append((title, text))
            return
       
        self.message.set_text(title)
        self.detail.set_text(text)
        width = int(self.box.get_width() * 0.80) #Width is 80% of the box, giving 10% gap each side
        self.detail.set_width(width)
        self.message.set_width(width)


        self.main_group.set_opacity(0)      
        self.backdrop.set_opacity(0)
        self.stage.add(self.backdrop)
        self.stage.add(self.main_group)
        self.main_group.show_all()
        self.backdrop.show()
        
        self.timeline = clutter.Timeline(10,30)
        alpha = clutter.Alpha(self.timeline, clutter.ramp_inc_func)
        self.behaviour_group = clutter.BehaviourOpacity(opacity_start=0, opacity_end=255, alpha=alpha)
        self.behaviour_backdrop = clutter.BehaviourOpacity(opacity_start=0, opacity_end=180, alpha=alpha)
        self.behaviour_group.apply(self.main_group)
        self.behaviour_backdrop.apply(self.backdrop)
        self.timeline.start()

        self.active = True
        
    def hide_msg(self):
        self.active = False
        
        self.timeline = clutter.Timeline(10,30)
        self.timeline.connect("completed", self.remove_from_stage)
        alpha = clutter.Alpha(self.timeline, clutter.ramp_inc_func)
        self.behaviour_group = clutter.BehaviourOpacity(opacity_start=255, opacity_end=0, alpha=alpha)
        self.behaviour_backdrop = clutter.BehaviourOpacity(opacity_start=180, opacity_end=0, alpha=alpha)
        self.behaviour_group.apply(self.main_group)
        self.behaviour_backdrop.apply(self.backdrop)
        self.timeline.start()
        
    def remove_from_stage(self, timeline):
        self.stage.remove(self.backdrop)
        self.stage.remove(self.main_group)
        
        #if there's messages in the queue, run through them
        if len(self.msgQueue) > 0:
            (title, text) = self.msgQueue.pop()
            self.display_msg(title, text)
        
    def on_key_press_event (self, stage, event):
        self.hide_msg()
        self.glossMgr.ui_overide = None