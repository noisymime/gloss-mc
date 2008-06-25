import clutter
from ui_elements.label_queue import LabelQueue

class Module(clutter.Group):
    title = "Tests"
    
    max_percent_of_stage = 0.75 # The maximum percentage of the stage size that images can be

    def __init__(self, glossMgr, dbMgr):
        clutter.Group.__init__(self)
        self.glossMgr = glossMgr
        self.stage = glossMgr.stage
        
        
        self.backdrop = clutter.Rectangle()
        self.backdrop.set_color(clutter.color_parse('Black'))
        self.backdrop.set_width(self.stage.get_width())
        self.backdrop.set_height(self.stage.get_height())
        self.add(self.backdrop)
        
        self.queue = LabelQueue(orientation=LabelQueue.ORIENTATION_BOTTOM)
        self.queue.setup_from_theme_id(glossMgr.themeMgr, "tests_label_queue")
        self.add(self.queue)
        
    def on_key_press_event(self, stage, event):
        #print event.hardware_keycode
        if event.keyval == clutter.keysyms.p:
            self.add_string_item("here is a string that gets added")
        if event.keyval == clutter.keysyms.q:
            clutter.main_quit()
        if event.keyval == clutter.keysyms.o:
            self.queue.clear()
        if event.keyval == clutter.keysyms.Escape:
            self.stage.remove(self)
            return True
        
    def begin(self, glossMgr):
        
        self.backdrop.set_opacity(0)
        self.backdrop.show()
        self.queue.set_opacity(0)
        self.queue.show()
        self.queue.display()
        
        self.stage.add(self)
        self.show()
        
        timeline = clutter.Timeline(10,30)
        alpha = clutter.Alpha(timeline, clutter.ramp_inc_func)
        self.opacity_behaviour = clutter.BehaviourOpacity(opacity_start=0, opacity_end=255, alpha=alpha)
        
        self.opacity_behaviour.apply(self.backdrop)
        self.opacity_behaviour.apply(self.queue)
        
        timeline.start()
        
    def add_string_item(self, string):
        self.queue.add_item(string)
        
    def stop(self):
        self.stage.remove(self)