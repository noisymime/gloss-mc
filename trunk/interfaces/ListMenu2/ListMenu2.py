import clutter
import pygtk
import gtk
import pango
import time
import math
from utils.InputQueue import InputQueue
from interfaces.MenuItem import MenuItem
from ui_elements.label_list import LabelList, ListItem

class Interface(clutter.Group):
    usePreviewEffects = True # Tells the modules to use any image preview effects where available
    font = ""
    menu_item_transition = None
    zoomLevel = 0.5
    opacityStep = 120
    position_0 = None
    
    def __init__ (self, glossMgr):
        clutter.Group.__init__(self)
        self.glossMgr = glossMgr
        self.stage = self.glossMgr.get_stage()
        self.itemGroup = clutter.Group()
        
        #Setup input queue controller
        self.input_queue = InputQueue()
        self.input_queue.set_action(InputQueue.NORTH, self.selectPrevious)
        self.input_queue.set_action(InputQueue.SOUTH, self.selectNext)
        
        self.label_list = LabelList()
        self.label_list.show()
        
        self.add(self.label_list)
        
        #This is a group to hold all the images
        self.image_group = clutter.Group()
        self.image_group.show()
        
        self.setup(glossMgr.themeMgr)
        
    def setup(self, themeMgr):
        element = themeMgr.search_docs("menu", "main").childNodes
        
        #setup the menu_image properties
        tmp_frame = themeMgr.get_imageFrame("menu_item_texture")
        self.menu_image_size = int(tmp_frame.img_size)
        self.use_reflection = tmp_frame.use_reflection
        self.menu_image_x = tmp_frame.get_x()
        self.menu_image_y = tmp_frame.get_y()
        
        self.label_list.setup_from_theme_id(themeMgr, "main_menu")
        #This is a hack, but we move the label list to (0,0) and set self to be where it was (As specified in the theme)
        self.set_position(self.label_list.get_x(), self.label_list.get_y())
        self.label_list.set_position(0, 0)
        
        #Setup the menu image transition
        image_transition = themeMgr.find_child_value(element, "image_transition.name")
        transition_options = themeMgr.find_child_value(element, "image_transition.options")
        transition_path = "interfaces/ListMenu2/transitions/" + str(image_transition)
        try:
            self.menu_item_transition = __import__(transition_path).Transition(self.glossMgr)
            self.menu_item_transition.set_options(transition_options)
        except ImportError:
            print "Theme Error: No menu_item transition titled '" + str(image_transition) + "'"
            self.menu_item_transition = None
        
        #Setup the menu transition
        menu_transition = themeMgr.find_child_value(element, "menu_transition.name")
        menu_transition_options = themeMgr.find_child_value(element, "menu_transition.options")
        themeMgr.glossMgr.set_menu_transition(menu_transition)
        
    def on_key_press_event(self, event):
        self.input_queue.input(event)
        
    def addItem(self, itemLabel):
        font = self.label_list.font_string
        
        newItem = MenuListItem(self, itemLabel, self.label_list, font)
        self.label_list.add_item(itemLabel, newItem=newItem)
        
        return newItem
        
    def display(self):
        self.label_list.display()
        
        self.stage.add(self)
        self.stage.add(self.image_group)
        self.image_group.show()
        self.image_group.show_all()
        self.show()
        
    def undisplay(self):
        self.stage.remove(self)
        self.stage.remove(self.image_group)
        self.image_group.hide_all()
        
    def selectNext(self):
        timeline = clutter.Timeline(self.label_list.frames, self.label_list.fps)
        self.input_queue.set_timeline(timeline)
        
        #Do the transition of the menu graphic
        #If there's no transition set (Would have been set in the theme) then the item is simply show
        if not self.menu_item_transition is None:
            item_to = self.label_list.get_current_item(offset=1)
            #if item_to is None, means we're at the bottom of the list
            if not item_to is None: item_to = item_to.get_item_textures()
            else: return
            
            item_from = self.label_list.get_current_item().get_item_textures()
            if not item_to is None: self.image_group.add(item_to)
            self.menu_item_transition.forward(timeline, item_from, item_to)
        else:
            self.menuItems[self.selected].get_item_textures().show()
        
        self.label_list.move_selection(self.label_list.DIRECTION_DOWN, timeline=timeline)
        
    def selectPrevious(self):
        timeline = clutter.Timeline(self.label_list.frames, self.label_list.fps)
        self.input_queue.set_timeline(timeline)
        
        #Do the transition of the menu graphic
        #If there's no transition set (Would have been set in the theme) then the item is simply show
        if not self.menu_item_transition is None:
            item_to = self.label_list.get_current_item(offset=-1)
            #if item_to is None, means we're at the top of the list
            if not item_to is None: item_to = item_to.get_item_textures()
            else: return
            
            item_from = self.label_list.get_current_item().get_item_textures()
            if not item_to is None: self.image_group.add(item_to)
            self.menu_item_transition.backward(timeline, item_from, item_to)
        else:
            self.menuItems[self.selected].get_item_textures().show()
            
        self.label_list.move_selection(self.label_list.DIRECTION_UP, timeline=timeline)
        
    def selectFirst(self, moveBar=False):
        if moveBar: self.label_list.select_first_elegant()
        else: self.label_list.select_first()
        self.input_queue.set_timeline(self.label_list.timeline)
        
        #Show the current menu item's graphic
        self.label_list.get_current_item().get_item_textures().show()
        self.image_group.add(self.label_list.get_current_item().get_item_textures())
        #self.menuItems[self.selected].itemTexturesGroup.show()
        
    def get_current_item(self):
        return self.label_list.get_current_item()
    
    def get_selector_bar(self):
        return self.label_list.selector_bar
        
class MenuListItem (ListItem):
    """
    
    This class really should have used multiple inheritance (MenuItem, ListItem) however due to gobject not supporting
    multiple inheritance this was not possible. To make it work, it singly inherits from ListItem and 'pretends' to be a MenuItem as well
    
    """
    def __init__(self, menu, label, label_list, font):
        ListItem.__init__(self, font, label, label_list=label_list)
        
        self.menu_item = MenuItem(menu, label, 0)
        self.menu = menu
        #MenuItem.__init__(self, menu, label, 0)
        
    #All methods below are to 'mask' this class as a MenuItem
    def add_image_from_path(self, path, x, y, width=None, height=None):
        self.menu_item.add_image_from_path(path, x, y, width, height)
        
    def add_image_from_texture(self, texture):
        self.menu_item.add_image_from_texture(texture)
        
    def set_data(self, data):
        self.menu_item.set_data(data)
        
    def get_data(self):
        return self.menu_item.data
    
    def get_main_texture(self):
        return self.menu_item.main_texture
    
    def setAction(self, newAction):
        self.menu_item.action = newAction
        
    def getAction(self):
        return self.menu_item.action
    
    def get_menu(self):
        return self.menu 
    
    def get_item_textures(self):
        return self.menu_item.itemTexturesGroup
        