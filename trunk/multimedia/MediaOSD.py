import clutter
import time

class osd:

    def __init__(self, glossMgr):
        self.glossMgr = glossMgr
        self.stage = glossMgr.stage
        self.timerRunning = False
        self.setup_ui()
        
        self.bar_group = clutter.Group()
        
    
        #self.background = clutter.Texture()
        #self.background.set_pixbuf( gtk.gdk.pixbuf_new_from_file("ui/default/osd_bar3.png") )
        #self.background.set_opacity(255)
        #self.background.set_width(stage.get_width())
        self.bar_group.add(self.background)
        self.bar_group.show_all()
        
    def setup_ui(self):
        self.background = self.glossMgr.themeMgr.get_texture("video_osd_bar", self.stage, None)
        
    def enter(self):
        self.stage.add(self.bar_group)
        self.bar_group.show()
        
        self.bar_group.set_position(0, self.stage.get_height())
        bar_position_y = int(self.stage.get_height() - self.background.get_height())
        
        knots = (\
                (self.bar_group.get_x(), self.bar_group.get_y()),\
                (self.bar_group.get_x(), bar_position_y) \
                )
                
        self.timeline = clutter.Timeline(25, 50)
        self.alpha = clutter.Alpha(self.timeline, clutter.ramp_inc_func)
        self.enter_behaviour_path = clutter.BehaviourPath(self.alpha, knots)
        
        self.enter_behaviour_path.apply(self.bar_group)
        
        self.timeline.start()
        
        self.timer = threading.Timer(3.0, self.exit)
        self.timer.start()
        
    def exit(self):
        
        knots = (\
                (self.bar_group.get_x(), self.bar_group.get_y()),\
                (self.bar_group.get_x(), int(self.stage.get_height())) \
                )
                
        self.timeline = clutter.Timeline(25, 50)
        self.timeline.connect('completed', self.exit_end_event)
        self.alpha = clutter.Alpha(self.timeline, clutter.ramp_inc_func)
        self.exit_behaviour_path = clutter.BehaviourPath(self.alpha, knots)
        
        self.exit_behaviour_path.apply(self.bar_group)
        self.timeline.start()
        
    def exit_end_event(self, data):
        self.stage.remove(self.bar_group)
    
    #Is called when the media is skipped forwards or backwards
    def shift_media(self, shift_amount):
        #Firstly check whether the label is already there from last time
        if self.timerRunning:
            return
            
        shiftDistance = 100
        
        self.shift_label = clutter.Label()
        self.shift_label.set_font_name("Lucida Grande 60")
        self.shift_label.set_opacity(0)
        self.shift_label.set_color(clutter.color_parse('White'))
    
        #Set the string for the fast forward / rewind as well as the 
        if shift_amount > 0:
            self.shift_label.set_text("+" + str(shift_amount) + "s >")
            shift_label_x = int(self.stage.get_width() - self.shift_label.get_width() - shiftDistance)
            direction = 1
        else:
            self.shift_label.set_text("< " + str(shift_amount) + "s")
            shift_label_x = int(0 + shiftDistance)
            direction = -1
        
        shift_label_y = int(self.stage.get_height() - self.shift_label.get_height()) 
        self.shift_label.set_position( shift_label_x, shift_label_y )
        incoming_label_knots = (\
            ( shift_label_x, shift_label_y ),\
            ( int(shift_label_x + (shiftDistance*direction)), shift_label_y )\
            )
        
        self.incoming_text_timeline = clutter.Timeline(20, 60)
        alpha = clutter.Alpha(self.incoming_text_timeline, clutter.ramp_inc_func)
        self.behaviour1 = clutter.BehaviourPath(alpha, incoming_label_knots)
        self.behaviour2 = clutter.BehaviourOpacity(opacity_start=0, opacity_end=120, alpha=alpha)
        
        self.behaviour1.apply(self.shift_label)
        self.behaviour2.apply(self.shift_label)
        self.stage.add(self.shift_label)
        self.shift_label.show()
        
        #self.timer = threading.Timer(1.5, self.label_exit)
        gobject.timeout_add(1500, self.label_exit)
        self.timerRunning = True
        #self.timer.start()
        
        self.incoming_text_timeline.start()
        #print time.strftime("%H:%M:%S", time.gmtime(amount))
        
    def label_exit(self):
        self.timerRunning = False
        #Check which way this label needs to go
        if self.shift_label.get_text()[0] == "<":
            end_x = int(self.shift_label.get_width() * -1)
        else:
            end_x = int(self.stage.get_width())
        
        (starting_pos_x, starting_pos_y) = self.shift_label.get_abs_position()
        outgoing_label_knots = (\
        ( starting_pos_x, starting_pos_y ),\
        ( end_x, starting_pos_y )\
        )
        
        self.outgoing_text_timeline = clutter.Timeline(20, 60)
        self.outgoing_text_timeline.connect('completed', self.removeLabel)
        alpha = clutter.Alpha(self.outgoing_text_timeline, clutter.ramp_inc_func)
        self.behaviour1 = clutter.BehaviourPath(alpha, outgoing_label_knots)
        self.behaviour2 = clutter.BehaviourOpacity(opacity_start=self.shift_label.get_opacity() , opacity_end=0, alpha=alpha)
        
        self.behaviour1.apply(self.shift_label)
        self.behaviour2.apply(self.shift_label)
        
        self.outgoing_text_timeline.start()
        
        return False
        
    def removeLabel(self, data):
        self.stage.remove(self.shift_label)