import clutter
from themeMgr import ThemeMgr
from Spinner import Spinner
import pygtk
import gtk
import pango
import copy

class GlossMgr:

    def __init__ (self, stage):
        self.stage = stage
        self.menus = []
        self.menuHistory = [] #A list that contains menus in the order that they've been viewed
        self.currentMenu = None
        self.debug = False #Debug flag
        self.uiMsg = message(stage)
        
        self.themeMgr = ThemeMgr(self)
        
        #Set the menu interface
        element = self.themeMgr.search_docs("menu", "main").childNodes
        interface_name = self.themeMgr.find_child_value(element, "interface")
        self.set_menu_interface(interface_name)
        
        #Set a default menu transition
        self.set_menu_transition("slide")
        
        #The background is a bit messy due to the depth issues :(
        background = self.themeMgr.get_texture("background", None, None)
        background.set_size(self.stage.get_width(), self.stage.get_height())
        """
        (width, height) = background.get_abs_size()
        print background.get_abs_size()
        #background.set_anchor_point_from_gravity(clutter.GRAVITY_NORTH_WEST)
        background.set_anchor_point(int(background.get_width()/3.5), int(background.get_height()/3.5))    
        #background.set_anchor_point_from_gravity(clutter.GRAVITY_CENTER)
        background.set_depth(-self.stage.get_width())
        print background.get_abs_size()
        #
        (width_new, height_new) = background.get_abs_size()
        #width = self.stage.get_width()
        #height = self.stage.get_height()
        scale_x = float(width)/float(width_new)
        scale_y = float(height)/float(height_new)
        background.set_scale(scale_x, scale_y)
        print background.get_abs_size()
        #background.set_width(width)
        #background.set_height(height)
        """
        background.show()
        
        self.stage.add(background)
        print "Perspective: " + str(stage.get_perspective())
        #stage.set_perspective(60.0, 1.0, 0.1, 1)
        
        #Setip the selector bar
        self.selector_bar = MenuSelector(self)
        self.selector_bar.show_all()        
        self.stage.add(self.selector_bar)
        

        self.currentPlugin = None
        
    def addMenu(self, newMenu):
        self.menus.append(newMenu)
        #If this is the first menu, make it the active one
        if self.currentMenu == None:
            self.currentMenu = newMenu
            self.menuHistory.append(newMenu)
            #self.currentMenu.getItemGroup().show_all()
            self.currentMenu.show_all()
            self.currentMenu.show()
            
            #self.stage.add(self.currentMenu)
            #self.stage.add(self.currentMenu.getItemGroup())
            
            #This is a bit hacky, but we set the selector bar size based on the font size
            tmpLabel = clutter.Label()
            tmpLabel.set_text("AAA")
            tmpLabel.set_font_name(self.currentMenu.font)
            #Selector bar height is 20% larger than the labels
            self.selector_bar.set_height( int(tmpLabel.get_height()*self.selector_bar.height_percent) )
            self.selector_bar.set_menu(self.currentMenu)
            tmpLabel = None

        
    def get_selector_bar(self):
        return self.selector_bar
        
    def get_stage(self):
        return self.stage
        
    def get_themeMgr(self):
        return self.themeMgr
                
    def on_key_press_event (self, stage, event):
        #Firstly check whether any messages are currently displayed
        if self.uiMsg.active:
            self.uiMsg.on_key_press_event(stage, event)
            return
            
        #Secondly, checking whether we are in the process of running a plugin (And that the key isn't escape)
        if (not self.currentPlugin == None) and (not event.keyval == clutter.keysyms.Escape):
            #If it is, simply pass the event details along to the plugin
            self.currentPlugin.on_key_press_event(stage, event)
            return None
            
            
        # If none of these things, the menu needs to do something
        if event.keyval == clutter.keysyms.Up: #Up button pressed
            self.currentMenu.input_queue.input(event)
            #self.currentMenu.selectPrevious()
        if event.keyval == clutter.keysyms.Down: #Down button pressed
            self.currentMenu.input_queue.input(event)
            #self.currentMenu.selectNext()
        if event.keyval == clutter.keysyms.q:
            self.stage.show_cursor()
            clutter.main_quit()
        if event.keyval == clutter.keysyms.Return:
            # Need to decide what action to take
            # Options are:
            # 1) Switch to a new menu
            # 2) Launch a module
            action = self.currentMenu.get_current_item().getAction()
            if action.__class__.__name__ == "Interface": # Check whether we're a pointing to an interface
                self.transition.do_transition(self.currentMenu, action)
                self.menuHistory.append(action)
            else:
                #We have a plugin and need to start it
                self.currentPlugin = action
                if action is None:
                    self.display_msg("Error", "Could not start " + self.currentMenu.get_current_item().get_text())
                else:
                    #hide any unnecesary actors
                    self.currentMenu.hide()
                    #self.stage.remove(self.currentMenu.getItemGroup())
                    #And begin the plugin
                    action.begin( self )
        # This is tres bodge
        if event.keyval == clutter.keysyms.Escape:
            #If there's a plugin running then end it
            if not self.currentPlugin == None:
                #Plugins on_key_press_event should return true if the plugin is finishing
                if self.currentPlugin.on_key_press_event(stage, event):
                    self.currentPlugin.stop()
                    self.currentPlugin = None
                    
                    timeline_stop = clutter.Timeline(10,30)
                    alpha = clutter.Alpha(timeline_stop, clutter.ramp_inc_func)
                    self.stop_behaviour = clutter.BehaviourOpacity(opacity_start=0, opacity_end=255, alpha=alpha)
                    self.currentMenu.set_opacity(0)
                    self.currentMenu.show()
                    self.stop_behaviour.apply(self.currentMenu)
                    timeline_stop.start()
            #If there's no plugin running, go back one in the menu list (Providing we're not already at the first item.
            else:
                if len(self.menuHistory)>1:
                    self.transition.do_transition(self.menuHistory.pop(), self.menuHistory[-1])
                    self.currentMenu = self.menuHistory[-1]
        #print event.hardware_keycode
    
    def get_current_menu(self):
        return self.currentMenu
    
    def go_up_x_levels(self, num_levels):
        for i in range(1, num_levels):
            if len(self.menuHistory)>1:
                    self.transition_fade_zoom(self.menuHistory.pop(), self.menuHistory[-1])
                    self.currentMenu = self.menuHistory[-1]
                    
    def display_msg(self, title, msg):
        self.uiMsg.display_msg(title, msg)
    
    def set_menu_interface(self, interface_name):
        #Setup the menu interface
        interface_path = "interfaces/" + interface_name + "/" + interface_name
        self.interface = __import__(interface_path)
        
    def set_menu_transition(self, transition_name):
        #Setup the menu transition
        transition_path = "transitions/menus/" + transition_name
        self.transition = __import__(transition_path).Transition(self)
        
    def create_menu(self):
        return self.interface.Interface(self)
        
        
class MenuSelector(clutter.Texture):
    x_offset = -50
    height_percent = 1
    position_0 = None

    def __init__ (self, glossMgr):
        clutter.Texture.__init__ (self)
        self.glossMgr = glossMgr
        glossMgr.themeMgr.get_texture("selector_bar", glossMgr.stage, self)
        self.set_position(0, self.get_y())
        if not self.get_pixbuf() is None:
            self.x_offset = int(glossMgr.themeMgr.get_value("texture", "selector_bar", "position.x"))
            self.height_percent = float(glossMgr.themeMgr.get_value("texture", "selector_bar", "height_percent")) / float(100)
        else:
            self.position_0 = (0, 0)
        
    #This is a utility function that gets the coordinates of an that has been scaled
    def get_true_abs_position(self, selectee):
        #This whole clone label thing is a HORRIBLE hack but is there to compensate for the movement caused by scaling using GRAVITY_WEST
        #Essentially a clone of the selectee is made and scaled to its final position to retrieve the final abs_position coords
        cloneLabel = clutter.Label()
        cloneLabel.set_text(selectee.get_text())
        cloneLabel.set_font_name(selectee.get_font_name())
        (scale_x, scale_y) = selectee.get_scale()
        cloneLabel.set_anchor_point_from_gravity(clutter.GRAVITY_WEST)
        cloneLabel.set_scale(scale_x, scale_y)
        selectee.get_parent().add(cloneLabel)
        
        cloneLabel.set_position(selectee.get_x(), selectee.get_y())
        
        #Now that all the cloning is done, find out what the scale is to become and set it on the clone
        scale = selectee.currentZoom
        cloneLabel.set_scale(scale, scale)
        
        return cloneLabel.get_abs_position()

    def selectItem(self, selectee, timeline):
                
        
        #Now get the end position of the clone
        (x, y) = self.get_true_abs_position(selectee)
        #print (x, y)
        
        #Do some minor adjustments for centering etc
        x = x + self.x_offset
        y = y - int( (self.get_height()-selectee.get_height())/2 )
        
        #Yet another little hack, but this stores the position of the first element
        if self.position_0 is None:
            self.position_0 = (x, y)

        #Move the bar
        self.move_to(x, y, timeline)
        
    def move_to(self, x, y, timeline):  
        knots = (\
                (self.get_x(), self.get_y()),\
                (x, y)\
                )
                
        self.alpha = clutter.Alpha(timeline, clutter.ramp_inc_func)
        self.behaviour = clutter.BehaviourPath(self.alpha, knots)
        
        self.behaviour.apply(self)
        
    def set_menu(self, menu):
        self.menu = menu
        
    def set_spinner(self, state):
        self.timeline = clutter.Timeline(25, 25)
        self.alpha = clutter.Alpha(self.timeline, clutter.ramp_inc_func)
        self.behaviour = clutter.BehaviourOpacity(opacity_start=0, opacity_end=255, alpha=self.alpha)
        if state:
            self.spinner = Spinner()
            
            height = self.get_height() - int(self.get_height() * 0.11)
            #Height has to be even otherwise spinner rotates on a slightly off axis
            if (height % 2) == 1:
                height = height -1
            
            width = height
            self.spinner.set_size(width, height)
            
            (x, y) = self.get_abs_position()
            x = x + self.get_width() - int(self.get_width() * 0.13)
            y = y + int(self.get_height() * 0.03)
            self.spinner.set_position(x, y)
            
            self.spinner.set_opacity(0)
            self.spinner.show()
            self.glossMgr.get_stage().add(self.spinner)
            self.behaviour = clutter.BehaviourOpacity(opacity_start=0, opacity_end=255, alpha=self.alpha)
            self.spinner.start()
        else:
            self.behaviour = clutter.BehaviourOpacity(opacity_start=255, opacity_end=0, alpha=self.alpha)
            self.timeline.connect('completed', self.spinner_end_event)
            #self.menuMgr.get_stage().remove(self.spinner)
            #self.spinner = None
        
        self.behaviour.apply(self.spinner)
        self.timeline.start()
        
    def spinner_end_event(self, data):
        self.glossMgr.get_stage().remove(self.spinner)
        self.spinner = None
        
    def get_x_offset(self):
        return self.x_offset
        
class message():
    font = "Lucida Grande "
    message_font_size = 30
    detail_font_size = 22
    
    def __init__(self, stage):
        self.stage = stage
        self.active = False
        
        self.backdrop = clutter.Rectangle()
        self.backdrop.set_color(clutter.color_parse('Black'))
        #self.backdrop.set_opacity(240)
        self.backdrop.set_width(self.stage.get_width())
        self.backdrop.set_height(self.stage.get_height())
        
        self.main_group = clutter.Group()
        
        pixbuf = gtk.gdk.pixbuf_new_from_file("ui/splash_box.png")
        self.box = clutter.Texture()
        self.box.set_pixbuf(pixbuf)
        self.box.set_opacity(int(255 * 0.75))
        self.box.set_height(int(self.stage.get_height()* 0.3))
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
        self.active = True
        
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
        
    def hide_msg(self):
        self.active = False
        
        self.timeline = clutter.Timeline(10,30)
        alpha = clutter.Alpha(self.timeline, clutter.ramp_inc_func)
        self.behaviour_group = clutter.BehaviourOpacity(opacity_start=255, opacity_end=0, alpha=alpha)
        self.behaviour_backdrop = clutter.BehaviourOpacity(opacity_start=180, opacity_end=0, alpha=alpha)
        self.behaviour_group.apply(self.main_group)
        self.behaviour_backdrop.apply(self.backdrop)
        self.timeline.start()
        
    def on_key_press_event (self, stage, event):
        self.hide_msg()