import clutter
import copy
from utils.themeMgr import ThemeMgr
from ui_elements.message import Message
from ui_elements.Spinner import Spinner

"""The core control class for Gloss

GlossMgr handles and controls the input. It maintains the status of any modules / plugins
as well as the interface that is to be used. All input goes through GlossMgr, which in turns passes it
to the correct module. It also stores certain global properties (Eg a 'debug' flag). The GlossMgr instance is passed to all modules so that they my reference this data
"""
__author__ =  'Josh Stewart (noisymime)'
__version__=  '0.1'"""The core control class for Gloss

GlossMgr handles and controls the input. It maintains the status of any modules / plugins
as well as the interface that is to be used. All input goes through GlossMgr, which in turns passes it
to the correct module. It also stores certain global properties (Eg a 'debug' flag). The GlossMgr instance is passed to all modules so that they my reference this data
"""
__author__ =  'Josh Stewart (noisymime)'
__version__=  '0.1'

class GlossMgr:
    theme_dir = "themes/"

    def __init__ (self, stage, dbMgr, theme=None):
        self.stage = stage
        self.menus = []
        self.menuHistory = [] #A list that contains menus in the order that they've been viewed
        self.currentMenu = None
        self.debug = False #Debug flag
        self.ui_overide = None
        self.uiMsg = Message(self)
        self.dbMgr = dbMgr
        
        self.themeMgr = ThemeMgr(self, theme)
        
        #Set the menu interface
        element = self.themeMgr.search_docs("menu", "main").childNodes
        interface_name = self.themeMgr.find_child_value(element, "interface")
        self.set_menu_interface(interface_name)
        
        #Set a default menu transition
        self.set_menu_transition("slide")
        
        #The background is a bit messy due to the depth issues :(
        background = self.themeMgr.get_texture("background", None, None)
        background.set_size(self.stage.get_width(), self.stage.get_height())

        background.show()
        
        self.stage.add(background)

        self.currentPlugin = None
        
    def addMenu(self, newMenu):
        """Adds a new menu to the main interface
        
        Arguments:
        newMenu -- The new menu to be added to the interface
        
        """
        self.menus.append(newMenu)
        #If this is the first menu, make it the active one
        if self.currentMenu == None:
            self.currentMenu = newMenu
            self.menuHistory.append(newMenu)
            self.currentMenu.show_all()
            self.currentMenu.show()
            
            #This is a bit hacky, but we set the selector bar size based on the font size
            tmpLabel = clutter.Label()
            tmpLabel.set_text("AAA")
            tmpLabel.set_font_name(self.currentMenu.font)
            #Selector bar height is 20% larger than the labels
            #self.selector_bar.set_height( int(tmpLabel.get_height()*self.selector_bar.height_percent) )
            #self.selector_bar.set_menu(self.currentMenu)
            tmpLabel = None

    def get_stage(self):
        return self.stage
        
    def get_themeMgr(self):
        return self.themeMgr
                
    def on_key_press_event (self, stage, event):
        """Handles *all* input in Gloss
        
        In 'normal' mode, this will pass the event to the menu item and select it accordingly. If the key is 'Return' then it will start the currently selected module
        Exceptions to this:
        1) If the UI Overide variable is set, the event is sent to it. This is used for things such as UI prompts (messages) and option dialogs that need to have UI focus above all else
        2) If there is a plugin running, the input event gets sent through to its 'on_key_press_event()' method. If this method returns True, GlossMgr assumes the plugin to have terminated. 
        
        Arguments:
        stage -- The primary stage object
        event -- The Clutter event object
        """
        #Firstly check whether any messages are currently displayed
        if not self.ui_overide is None:
            self.ui_overide.on_key_press_event(stage, event)
            return
            
        #Secondly, checking whether we are in the process of running a plugin (And that the key isn't escape)
        if (not self.currentPlugin == None) and (not event.keyval == clutter.keysyms.Escape):
            #If it is, simply pass the event details along to the plugin
            self.currentPlugin.on_key_press_event(stage, event)
            return None
            
            
        # If none of these things, the menu needs to do something
        if event.keyval == clutter.keysyms.Up: #Up button pressed
            self.currentMenu.on_key_press_event(event)
            #self.currentMenu.selectPrevious()
        if event.keyval == clutter.keysyms.Down: #Down button pressed
            self.currentMenu.on_key_press_event(event)
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
                    self.kill_plugin()
            #If there's no plugin running, go back one in the menu list (Providing we're not already at the first item.
            else:
                if len(self.menuHistory)>1:
                    self.transition.do_transition(self.menuHistory.pop(), self.menuHistory[-1])
                    self.currentMenu = self.menuHistory[-1]
        #print event.hardware_keycode
        
    def kill_plugin(self):
        """Kills any currently running plugin/module"""
        
        if not self.currentPlugin is None:
            self.currentPlugin.stop()
            self.currentPlugin = None
            
            timeline_stop = clutter.Timeline(10,30)
            alpha = clutter.Alpha(timeline_stop, clutter.ramp_inc_func)
            self.stop_behaviour = clutter.BehaviourOpacity(opacity_start=0, opacity_end=255, alpha=alpha)
            self.currentMenu.set_opacity(0)
            self.currentMenu.show()
            self.stop_behaviour.apply(self.currentMenu)
            timeline_stop.start()
    
    def get_current_menu(self):
        return self.currentMenu

    def go_up_x_levels(self, num_levels):
        for i in range(1, num_levels):
            if len(self.menuHistory)>1:
                    self.transition_fade_zoom(self.menuHistory.pop(), self.menuHistory[-1])
                    self.currentMenu = self.menuHistory[-1]
                    
    def display_msg(self, title, msg):
        self.uiMsg.display_msg(title, msg)
        self.ui_overide = self.uiMsg
    
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
        