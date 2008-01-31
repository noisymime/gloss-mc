import clutter
import pygtk
import gtk
import pango
import time
import math
from ReflectionTexture import Texture_Reflection
from interfaces.ListItem import ListItem
from InputQueue import InputQueue

class Interface(clutter.Group):
    itemGroup = clutter.Group()
    
    def __init__ (self, glossMgr):
        clutter.Group.__init__(self)
        self.glossMgr = glossMgr
        self.stage = self.glossMgr.get_stage()
        self.itemGroup = clutter.Group()
        self.setup_ui(self.glossMgr.themeMgr, "main", self)
        
        #Setup input queue controller
        self.input_queue = InputQueue()
        self.input_queue.set_action(InputQueue.NORTH, self.selectPrevious)
        self.input_queue.set_action(InputQueue.SOUTH, self.selectNext)
        
    def addItem(self, itemLabel):
        if len(self.itemsGroup) == 0:
            tempLabel = clutter.Label()
            tempLabel.set_font_name(self.font)
            tempLabel.set_text("S")
            self.label_height = tempLabel.get_height()
            label_width = 0
        
        label_y = len(self.menuItems) * (self.label_height + self.item_gap)
        #print "Label height: " + str(self.label_height)
        
        newItem = MenuListItem(self, itemLabel, label_y)
        self.menuItems.append(newItem)
        self.itemGroup.add(newItem)