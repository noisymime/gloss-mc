import clutter
import gobject
from ui_elements.rounded_rectangle import RoundedRectangle

class ProgressBar(clutter.Group):
    
    def __init__(self, Controller):
        clutter.Group.__init__(self)
        
        self.media_controller = Controller
            
        self.bg = clutter.Rectangle()        
        self.fg = clutter.Rectangle()

        
        self.add(self.bg)
        self.bg.show()
        self.add(self.fg)
        self.fg.show()
        
    def setup_from_theme_id(self, themeMgr, id):
        element = themeMgr.search_docs("progress_bar", id).childNodes
        colour_element = themeMgr.search_docs("progress_bar", id).getElementsByTagName("colour")
        
        #width = clutter.Stage.get_width(), height = 10
        (self.width, self.height) = themeMgr.get_dimensions(element, themeMgr.stage)
        
        colour_element_bg = themeMgr.find_element(colour_element, "id", "background")
        colour_element_fg = themeMgr.find_element(colour_element, "id", "foreground")
        if not colour_element_bg is None:
            colour_element_bg = colour_element_bg.childNodes
            bgColour = themeMgr.get_colour(colour_element_bg, "background")
        if not colour_element_fg is None:
            colour_element_fg = colour_element_fg.childNodes
            fgColour = themeMgr.get_colour(colour_element_fg, "foreground")
        #bgColour = themeMgr.get_colour(element, "background")
        #fgColour = themeMgr.get_colour(element, "foreground")
        
        
        self.bg.set_size(self.width, self.height)
        #self.bg = RoundedRectangle(self.width, self.height)
        self.bg.set_color(bgColour)
        #self.bg.show()
        #self.add(self.bg)
        
        self.fg = RoundedRectangle(20, self.height)
        self.fg.set_color(fgColour)
        self.fg.show()
        self.add(self.fg)
        #self.fg.set_size(20, self.height)
        
    def display(self):
        self.displayed = True
        
        
        self.show()
        gobject.timeout_add(1000, self.tick)
        
    def tick(self):
        if self.displayed:
            percent = self.media_controller.get_position_percent()
            new_width = int(float(self.width) * float(percent))
            
            #print "new width: %s" % float(new_width)
            self.fg.set_width(new_width)
            
            return True
        else:
            return False
        
        