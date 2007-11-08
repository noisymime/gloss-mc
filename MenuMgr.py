import clutter
from SkinMgr import SkinMgr
from Spinner import Spinner
import pygtk
import gtk

class MenuMgr:

    def __init__ (self, stage):
        self.stage = stage
        self.menus = []
        self.menuHistory = [] #A list that contains menus in the order that they've been viewed
        self.currentMenu = None
        
        self.skinMgr = SkinMgr(self.stage)
        background = self.skinMgr.get_Background()
        self.stage.add(background)
        
        self.selector_bar = MenuSelector(self)
        self.stage.add(self.selector_bar)
        self.selector_bar.show_all()
        self.currentPlugin = None
        
    def addMenu(self, newMenu):
        self.menus.append(newMenu)
        
        #If this is the first menu, make it the active one
        if self.currentMenu == None:
            self.currentMenu = newMenu
            self.menuHistory.append(newMenu)
            self.currentMenu.getItemGroup().show_all()
            self.currentMenu.getMenuGroup().show_all()
            self.selector_bar.set_menu(self.currentMenu)
        
    def get_selector_bar(self):
        return self.selector_bar
        
    def get_stage(self):
        return self.stage
        
    def get_skinMgr(self):
        return self.skinMgr
        
    def transition_fade_zoom(self, fromMenu, toMenu):
        oldGroup = fromMenu.getItemGroup()
        oldMenuGroup = fromMenu.getMenuGroup()
        newGroup = toMenu.getItemGroup()
        newMenuGroup = toMenu.getMenuGroup()
        
        oldGroup.set_opacity(255)
        
        self.timeline = clutter.Timeline(25, 50)
        self.alpha = clutter.Alpha(self.timeline, clutter.ramp_inc_func)
        #self.exit_behaviour_scale = clutter.BehaviourScale(self.alpha, 1, 0.5, clutter.GRAVITY_CENTER)
        self.exit_behaviour_opacity = clutter.BehaviourOpacity(self.alpha, 150, 0)
        
        #Setup some knots
        knots_exiting = (\
                (oldGroup.get_x(), oldGroup.get_y()),\
                #(-oldGroup.get_x(), int(fromMenu.getStage().get_height()/2))
                (-oldGroup.get_x(), oldGroup.get_y())\
                )
        self.exit_behaviour_path = clutter.BehaviourPath(self.alpha, knots_exiting)
        
        #self.exit_behaviour_scale.apply(oldGroup)
        self.exit_behaviour_opacity.apply(oldGroup)
        self.exit_behaviour_opacity.apply(oldMenuGroup)
        self.exit_behaviour_path.apply(oldGroup)
        
        
        ##################################################################
        #Start incoming menu
        #self.exit_behaviour_scale = clutter.BehaviourScale(self.alpha, 1, 0.5, clutter.GRAVITY_CENTER)
        self.entrance_behaviour_opacity = clutter.BehaviourOpacity(self.alpha, 0, 255)
        
        #Setup some knots
        start_y = int(self.stage.get_height()/2 - newGroup.get_height()/2)
        start_x = int(self.stage.get_width())
        newGroup.set_position(start_x, start_y)
        #end_x = int(self.stage.get_width() - newGroup.get_width())/2
        (end_x, end_y) = toMenu.get_display_position()
        end_x = oldGroup.get_x() #int(end_x)
        end_y = oldGroup.get_y() #int(end_y)
        knots_entering = (\
                (newGroup.get_x(), newGroup.get_y()),\
                #(-oldGroup.get_x(), int(fromMenu.getStage().get_height()/2))
                (end_x, end_y) \
                #toMenu.get_display_position()
                )

        self.entrance_behaviour_path = clutter.BehaviourPath(self.alpha, knots_entering)
        
        self.entrance_behaviour_opacity.apply(newGroup)
        self.entrance_behaviour_opacity.apply(newMenuGroup)
        self.entrance_behaviour_path.apply(newGroup)
        #newGroup.show_all()
        #newMenuGroup.show_all()
        toMenu.display()
        
        #Finally, move the selector bar
        self.selector_bar.selectItem(fromMenu.getItem(0), self.timeline)
        #(to_x, to_y) = toMenu.get_display_position() #fromMenu.getItem(0).get_abs_position()
        #self.selector_bar.move_to(int(to_x), int(to_y), self.timeline)
        toMenu.selectFirst(False)
        
        #self.timeline.connect('completed', self.on_transition_complete)
        self.timeline.start()
        self.currentMenu = toMenu
        
    def on_key_press_event (self, stage, event):
        #Firstly checking whether we are in the process of running a plugin (And that the key isn't escape)
        if (not self.currentPlugin == None) and (not event.keyval == clutter.keysyms.Escape):
            #If it is, simply pass the event details along to the plugin
            self.currentPlugin.on_key_press_event(stage, event)
            return None
            
        #print event.hardware_keycode 
        if event.keyval == clutter.keysyms.Up: #Up button pressed
            self.currentMenu.selectPrevious()
        if event.keyval == clutter.keysyms.Down: #Down button pressed
            self.currentMenu.selectNext()
        if event.keyval == clutter.keysyms.q:
            clutter.main_quit()
        if event.hardware_keycode == 36: #return button pressed
            #self.aList.set_processing(True)
            action = self.currentMenu.get_current_item().getAction()
            if action.__class__.__name__ == "Menu": # Check whether we're a pointing to a menu object
                self.transition_fade_zoom(self.currentMenu, action)
                self.menuHistory.append(action)
            else:
                #We have a plugin and need to start it
                self.currentPlugin = action
                action.begin( self )
        if event.keyval == clutter.keysyms.Escape:
            #If there's a plugin running then end it
            if not self.currentPlugin == None:
                #Plugins on_key_press_event should return true if the plugin is finishing
                if self.currentPlugin.on_key_press_event(stage, event):
                    self.currentPlugin.stop()
                    self.currentPlugin = None
            #If there's no plugin running, go back one in the menu list (Providing we're not already at the first item.
            else:
                if len(self.menuHistory)>1:
                    self.transition_fade_zoom(self.menuHistory.pop(), self.menuHistory[-1])
                    self.currentMenu = self.menuHistory[-1]
        #print event.hardware_keycode
    
    def get_current_menu(self):
        return self.currentMenu
        
class MenuSelector(clutter.Texture):
    x_offset = -50
    width = 400

    def __init__ (self, menuMgr):
        clutter.Texture.__init__ (self)
        self.menuMgr = menuMgr
        pixbuf = gtk.gdk.pixbuf_new_from_file("ui/active_bar.png")
        self.set_pixbuf(pixbuf)
        self.set_width(self.width)
        
        #pixbuf = gtk.gdk.pixbuf_new_from_file("ui/spinner1.gif")
        #self.spinner = clutter.Texture()
        #self.spinner.set_pixbuf(pixbuf)
        #self.spinner.hide()
        

    def selectItem(self, selectee, timeline):
        (x, y) = selectee.get_abs_position()
        
        x = x + self.x_offset
       
        #Check if we're going up or down
        if y > self.get_y():     
            #Going down
            y = int(y - selectee.get_menu().get_item_gap()/2)
        else:
            #Going up
            y = int(y - selectee.get_menu().get_item_gap()/2)
            
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
        self.behaviour = clutter.BehaviourOpacity(self.alpha, 0,255)
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
            self.menuMgr.get_stage().add(self.spinner)
            self.behaviour = clutter.BehaviourOpacity(self.alpha, 0,255)
            self.spinner.start()
        else:
            self.behaviour = clutter.BehaviourOpacity(self.alpha, 255,0)
            self.timeline.connect('completed', self.spinner_end_event)
            #self.menuMgr.get_stage().remove(self.spinner)
            #self.spinner = None
        
        self.behaviour.apply(self.spinner)
        self.timeline.start()
        
    def spinner_end_event(self, data):
        self.menuMgr.get_stage().remove(self.spinner)
        self.spinner = None
        
    def get_x_offset(self):
        return self.x_offset
    def get_width(self):
        return self.width
        
