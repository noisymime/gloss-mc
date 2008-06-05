import clutter
import pango
import gobject
from threading import Semaphore
from ui_elements.label_list import LabelList
from ui_elements.rounded_rectangle import RoundedRectangle

class OptionDialog(clutter.Group):
    #Setup signals
    __gsignals__ =  { 
        "option-selected": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_INT,))
        }
    
    theme_dir = "themes"
    
    font = "Lucida Grande "
    message_font_size = 30
    detail_font_size = 22
    
    def __init__(self, glossMgr):
        clutter.Group.__init__(self)
        self.glossMgr = glossMgr
        self.stage = glossMgr.stage
        
        self.backdrop = clutter.Rectangle()
        self.backdrop.set_color(clutter.color_parse('Black'))
        self.backdrop.set_width(self.stage.get_width())
        self.backdrop.set_height(self.stage.get_height())
        
        width = int(self.stage.get_width()* 0.4)
        height = int(self.stage.get_height()* 0.3)
        self.box = RoundedRectangle(width, height, clutter.color_parse('White'))
        self.box.set_opacity(int(255 * 0.55))
        self.add(self.box)

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
        self.add(self.message)
        
        self.label_list = LabelList()
        self.add(self.label_list)
        self.items = []
        
        group_x = (self.stage.get_width()/2) - (self.box.get_width()/2)
        group_y = (self.stage.get_height()/2) - (self.box.get_height()/2)
        self.set_position(group_x, group_y)
        
        self.setup()
        
    def setup(self):
        themeMgr = self.glossMgr.themeMgr
        themeMgr.get_group("option_dialog", group = self)
        result = self.label_list.setup_from_theme_id(themeMgr, "option_dialog_list", parent = self)

    def add_item(self, text):
        tmpItem = self.label_list.add_item(text)
        self.items.append(tmpItem)
        id = int(len(self.items)-1)
        tmpItem.set_data(id)
        
        return id

    def display(self, title):
        self.glossMgr.ui_overide = self
       
        self.message.set_text(title)
        width = int(self.box.get_width() * 0.80) #Width is 80% of the box, giving 10% gap each side
        self.message.set_width(width)


        self.set_opacity(0)      
        self.backdrop.set_opacity(0)
        self.stage.add(self.backdrop)
        self.stage.add(self)
        self.show_all()
        self.backdrop.show()
        
        self.timeline = clutter.Timeline(10,30)
        alpha = clutter.Alpha(self.timeline, clutter.ramp_inc_func)
        self.behaviour_group = clutter.BehaviourOpacity(opacity_start=0, opacity_end=255, alpha=alpha)
        self.behaviour_backdrop = clutter.BehaviourOpacity(opacity_start=0, opacity_end=180, alpha=alpha)
        self.behaviour_group.apply(self)
        self.behaviour_backdrop.apply(self.backdrop)
        self.timeline.start()

        #return self.label_list.get_current_item().get_data()
        
    def hide(self):
        self.active = False
        
        self.timeline = clutter.Timeline(10,30)
        self.timeline.connect("completed", self.remove_from_stage)
        alpha = clutter.Alpha(self.timeline, clutter.ramp_inc_func)
        self.behaviour_group = clutter.BehaviourOpacity(opacity_start=255, opacity_end=0, alpha=alpha)
        self.behaviour_backdrop = clutter.BehaviourOpacity(opacity_start=180, opacity_end=0, alpha=alpha)
        self.behaviour_group.apply(self)
        self.behaviour_backdrop.apply(self.backdrop)
        self.timeline.start()
        
    def remove_from_stage(self, timeline):
        self.stage.remove(self.backdrop)
        self.stage.remove(self)
        
    def on_key_press_event (self, stage, event):
        if event.keyval == clutter.keysyms.Up or event.keyval == clutter.keysyms.Down:
            self.label_list.on_key_press_event
        elif event.keyval == clutter.keysyms.Return:
            self.emit("option_selected", self.label_list.selected)
            self.hide()
            self.glossMgr.ui_overide = None