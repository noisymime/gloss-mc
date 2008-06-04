import clutter
import pygtk
import gtk
import pango
import time
import math
from ui_elements.ReflectionTexture import Texture_Reflection
from interfaces.MenuItem import MenuItem
from utils.InputQueue import InputQueue

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
        self.setup_ui(self.glossMgr.themeMgr, "main", self)

        self.add(self.itemGroup)
        
        #Setup input queue controller
        self.input_queue = InputQueue()
        self.input_queue.set_action(InputQueue.NORTH, self.selectPrevious)
        self.input_queue.set_action(InputQueue.SOUTH, self.selectNext)
        
        self.menuItems = []
        self.selected = 0
        self.displayMin = 0 #The number of menu items that will be shown at a time
        self.moveQueue = 0
        self.displaySize = self.displayMax - self.displayMin
        self.displayPosition = (0, 0)
        
        self.timeline = clutter.Timeline(15, 75) #This timeline is used on any movements that occur when changing items
        self.input_queue.set_timeline(self.timeline)
        self.timeline_completed=True
        self.glossMgr.addMenu(self)
        
    #Sets up the UI from the theme
    def setup_ui(self, themeMgr, name, menu):
        element = themeMgr.search_docs("menu", name).childNodes
        #Quick check to make sure we found something
        if element is None:
            return None
        
        menu.item_gap = int(themeMgr.find_child_value(element, "item_gap"))
        menu.displayMax = int(themeMgr.find_child_value(element, "num_visible_elements"))
        
        #Grab the font
        font_node = themeMgr.get_subnode(element, "font")
        fontString = themeMgr.get_font("main", font_node)
        menu.font = fontString
        
        #Set the selection effect steps
        menu.zoomStep0 = float(themeMgr.find_child_value(element, "scale_step0"))
        menu.zoomStep1 = float(themeMgr.find_child_value(element, "scale_step1"))
        menu.zoomStep2 = float(themeMgr.find_child_value(element, "scale_step2"))
        menu.opacityStep0 = int(themeMgr.find_child_value(element, "opacity_step0"))
        menu.opacityStep1 = int(themeMgr.find_child_value(element, "opacity_step1"))
        menu.opacityStep2 = int(themeMgr.find_child_value(element, "opacity_step2"))
        
        #setup the menu_image properties
        menu.useReflection = "True" == (themeMgr.find_child_value(element, "menu_item_texture.use_image_reflections"))
        menu.menu_image_rotation = int(themeMgr.find_child_value(element, "menu_item_texture.image_y_rotation"))
        menu_image_node = themeMgr.get_subnode(element, "menu_item_texture")
        if not menu_image_node is None:
            #Set the position
            (x, y) = themeMgr.get_position(menu_image_node, self.stage)
            menu.menu_image_x = int(x)
            menu.menu_image_y = int(y)
            
            """
            #Set the size
            (width, height) = self.get_dimensions(menu_image_node, self.stage)
            if width is None:
                print "no size change"
                menu.menu_image_width = None
                menu.menu_image_height = None
            else:
                menu.menu_image_width = int(width)
                menu.menu_image_height = int(height)
            """
        
        #Setup the menu image transition
        image_transition = themeMgr.find_child_value(element, "menu_item_texture.image_transition.name")
        transition_options = themeMgr.find_child_value(element, "menu_item_texture.image_transition.options")
        transition_path = "transitions/menu_items/" + str(image_transition)
        try:
            menu.menu_item_transition = __import__(transition_path).Transition(self.glossMgr)
            menu.menu_item_transition.set_options(transition_options)
        except ImportError:
            print "Theme Error: No menu_item transition titled '" + str(image_transition) + "'"
            menu.menu_item_transition = None
            
        #Setup the menu transition
        menu_transition = themeMgr.find_child_value(element, "menu_transition.name")
        menu_transition_options = themeMgr.find_child_value(element, "menu_transition.options")
        themeMgr.glossMgr.set_menu_transition(menu_transition)
                
        #Finally set general actor properties (position etc)
        #themeMgr.setup_actor(menu.getItemGroup(), element, themeMgr.stage)
        themeMgr.setup_actor(menu, element, themeMgr.stage)
    
    def addItem(self, itemLabel):
        if len(self.menuItems) == 0:
            tempLabel = clutter.Label()
            tempLabel.set_font_name(self.font)
            tempLabel.set_text("S")
            #tempLabel.set_scale_with_gravity(self.zoomStep0, self.zoomStep0, clutter.GRAVITY_WEST)
            self.label_height = tempLabel.get_height()
            #self.label_height = self.label_height * self.zoomStep1
            label_width = 0
        
        label_y = len(self.menuItems) * (self.label_height + self.item_gap)
        
        newItem = MenuListItem(self, itemLabel, label_y)
        self.menuItems.append(newItem)
        self.itemGroup.add(newItem)
        
        return newItem
        
    def display(self):
        if self.displayMax > len(self.menuItems):
            self.displayMax = len(self.menuItems)
            self.displaySize = self.displayMax - self.displayMin
        
        for i in range(self.displaySize):
            self.menuItems[i].show()
        
        
        self.stage.add(self)

        self.itemGroup.show()
        self.show()
        
    def getItem(self, index):
        return self.menuItems[index]
    def getStage(self):
        return self.stage
    def getGlossMgr(self):
        return self.glossMgr
    
    #The display position is the x, y coords of where the menu is when it is active
    def get_display_position(self):
        return (self.itemGroup.get_x(), self.itemGroup.get_y())
        
    def setMenuPosition(self, x, y):
        self.itemGroup.set_position(x,y)
        
    def getItemGroup(self):
        return self.itemGroup
    
    #Returns the newly selected item
    def selectNext(self):

        #Check if we're at the last item in the list
        if (self.selected) != (len(self.menuItems)-1):           
            self.timeline = clutter.Timeline (15,85)
            self.input_queue.set_timeline(self.timeline)
            #self.timeline.connect('completed', self.completeMove)

            if not self.moveQueue == 0:
                self.selected = self.selected +1 #+ self.moveQueue
                self.moveQueue = self.moveQueue - 1 #0
                if self.selected > (len(self.menuItems)-1):
                    self.selected = (len(self.menuItems)-1)
            else:
                self.selected = self.selected+1
            
            
            #This horrible loop does all the scaling
            #This includes, the selected item and the ones on either side of it
            for i in range(len(self.menuItems)):
                if i == self.selected:
                    self.menuItems[i].scaleLabel(0, self.timeline)
                elif (i == self.selected-1) and (i >= self.displayMin):
                    self.menuItems[i].scaleLabel(1, self.timeline)
                elif (i == self.selected+1) and (i <= self.displayMax-1):
                    self.menuItems[i].scaleLabel(1, self.timeline)
                else:
                    self.menuItems[i].scaleLabel(2, self.timeline)
            
            #print self.menuItems[self.selected].data + " " + str(self.menuItems[self.selected].itemTexturesGroup.scale_start)
            #Do the transition of the menu graphic
            #If there's no transition set (Would have been set in the theme) then the item is simply show
            if not self.menu_item_transition is None:
                self.menu_item_transition.forward(self.timeline, self.menuItems[self.selected-1].itemTexturesGroup, self.menuItems[self.selected].itemTexturesGroup)
            else:
                self.menuItems[self.selected].itemTexturesGroup.show()
                
            #Check we're at the bottom of the viewable list
            if self.selected >= (self.displayMax):
                #If yes, move the menu, leave the selection bar where is
                self.menuItems[self.selected].set_opacity(0)
                self.menuItems[self.selected].show()
                self.rollMenu( self.menuItems[self.selected], self.menuItems[self.selected-self.displaySize], self.timeline)
            else:
                #move the selection bar
                self.glossMgr.get_selector_bar().selectItem(self.menuItems[self.selected], self.timeline)
        
            self.timeline.start()
            self.moveQueue = 0
        
    #Returns the newly selected item
    def selectPrevious(self):
                
        #Check if we're at the first item in the list
        if (self.selected) != 0:        
            self.timeline = clutter.Timeline (15,85)
            self.input_queue.set_timeline(self.timeline)
            #self.timeline.connect('completed', self.completeMove)
                
            if not self.moveQueue == 0:
                self.selected = self.selected -1 #+ self.moveQueue
                self.moveQueue = self.moveQueue + 1 # 0
                if self.selected < 0:
                    self.selected = 0
            else:
                self.selected = self.selected-1
            
            #This horrible loop does all the scaling
            #This includes, the selected item and the ones on either side of it
            for i in range(len(self.menuItems)):
                #print str(i)
                if i == self.selected:
                    self.menuItems[i].scaleLabel(0, self.timeline)
                elif (i == self.selected-1) and (i >= self.displayMin):
                    self.menuItems[i].scaleLabel(1, self.timeline)
                elif (i == self.selected+1) and (i <= self.displayMax-1):
                    self.menuItems[i].scaleLabel(1, self.timeline)
                else:
                    self.menuItems[i].scaleLabel(2, self.timeline)
                    
            #Do the transition of the menu graphic
            #If there's no transition set (Would have been set in the theme) then the item is simply show
            if not self.menu_item_transition is None:
                self.menu_item_transition.backward(self.timeline, self.menuItems[self.selected+1].itemTexturesGroup, self.menuItems[self.selected].itemTexturesGroup)
            else:
                self.menuItems[self.selected].itemTexturesGroup.show()
            
            #Check we're at the top of the viewable list
            if self.selected < (self.displayMin):
                #If yes, move the menu, leave the selection bar where is
                #self.menuItems[self.selected].set_opacity(0)
                #self.menuItems[self.selected].show()
                self.rollMenu( self.menuItems[self.selected], self.menuItems[self.selected+self.displaySize], self.timeline)
            else:
                #move the selection bar
                self.glossMgr.get_selector_bar().selectItem(self.menuItems[self.selected], self.timeline)

            self.timeline.start()
                        
    def selectFirst(self, moveBar):
        if self.timeline.is_playing:
            "ERROR: Timeline should NOT be playing here!"
               
        self.timeline = clutter.Timeline(1, 75)
        self.selected = 0
        for i in range(0,len(self.menuItems)):
            if i == 0:
                self.menuItems[i].scaleLabel(0, self.timeline)
            elif i == 1:
                self.menuItems[i].scaleLabel(1, self.timeline)
            else:
                self.menuItems[i].scaleLabel(2, self.timeline)
            
        
        #Show the current menu item's graphic
        self.menuItems[self.selected].itemTexturesGroup.show()
        
        if moveBar:    
            self.glossMgr.get_selector_bar().selectItem(self.menuItems[self.selected], self.timeline)
        
        self.timeline.start()
        
    #When the menu needs to display a new item from the top or bottom, it rolls
    # The distance the menu moves is the distance (in pixels) between the incoming item and the selector bar
    def rollMenu(self, incomingMenuItem, outgoingMenuItem, timeline):  
        print "Rolling: " + incomingMenuItem.data + "<------" + outgoingMenuItem.data  
        (group_x, group_y) = self.itemGroup.get_abs_position()
        (bar_x, bar_y) = self.glossMgr.get_selector_bar().get_abs_position() # incomingMenuItem.get_menu().getMenuMgr().
        (incoming_x, incoming_y) = self.glossMgr.get_selector_bar().get_true_abs_position(incomingMenuItem) #incomingMenuItem.get_abs_position()
        
        print "Starting group position: " + str(self.itemGroup.get_abs_position())
        
        if incoming_y > bar_y:  
            #Then the incoming item is below the selector bar
            height_diff = int(self.glossMgr.get_selector_bar().get_height() - incomingMenuItem.get_height()) #self.glossMgr.get_selector_bar().get_height())
            #print "height diff: " + str(height_diff)
            gap = ((incoming_y - bar_y) - math.floor(height_diff/2)) * -1
            gap = int(gap)
            #gap = -65
            self.displayMin = self.displayMin+1
            self.displayMax = self.displayMax+1
        else:
            #Then the incoming item is above the selector bar
            height_diff = int(self.glossMgr.get_selector_bar().get_height() - incomingMenuItem.get_height()) #self.glossMgr.get_selector_bar().get_height())
            gap = bar_y - incoming_y + math.ceil(height_diff/2)
            gap = int(gap)
            #gap = 65
            self.displayMin = self.displayMin-1
            self.displayMax = self.displayMax-1
        
        #print "Gap: " + str(gap)
        new_y = (group_y + gap)
        knots = (\
            (group_x, group_y),\
            (group_x, new_y )\
            )
        alpha = clutter.Alpha(timeline, clutter.ramp_inc_func)
        self.behaviour1 = clutter.BehaviourPath(alpha, knots)
        self.behaviour2 = clutter.BehaviourOpacity(opacity_start=outgoingMenuItem.get_opacity(), opacity_end=0, alpha=alpha)
        
        #print "Going to: "+ str(new_y)
        #print behaviour1.get_knots()
        
        self.behaviour1.apply(self)
        self.behaviour2.apply(outgoingMenuItem)

    def get_current_item(self):
        return self.menuItems[self.selected]
    def get_group_y(self):
        (abx_x, abs_y) = self.itemGroup.get_position()
        height = self.get_y() + self.menuItems[1].get_y() * (self.displayMin)
        return height
        #return int(self.menuItems[self.displayMin].get_y())
            
    
class MenuListItem (MenuItem):
    zoomLevel = 0.5
    opacityStep = 120

    def __init__ (self, menu, itemLabel, y):
        MenuItem.__init__ (self, menu, itemLabel, y)
        self.glossMgr = menu.getGlossMgr()
        #self.menu = menu
        #self.stage = glossMgr.get_stage()
        
        #ItemTexturesGroup is what shows any images / reflections associated with the item
        #self.itemTexturesGroup = clutter.Group()
        #self.itemTexturesGroup.set_position(menu.menu_image_x, menu.menu_image_y)
        
        
        #setup the label
        """
        font = menu.font
        self.set_font_name(font)
        self.set_text(itemLabel)
        self.color = clutter.Color(0xff, 0xff, 0xff, 0xdd)
        self.set_color(self.color)
        self.currentOpacity = 255
        self.data = itemLabel #By default the items data is simply its label
        
        #The width is the length of the selector bar minus its offset
        width = self.glossMgr.get_selector_bar().get_width() + self.glossMgr.get_selector_bar().get_x_offset()
        self.set_width(width)
        
        self.set_ellipsize(pango.ELLIPSIZE_END)
        """
        #Text is actually scaled down in 'regular' position so that it doesn't get jaggies when zoomed in
        self.set_scale(self.zoomLevel, self.zoomLevel)
        self.currentZoom = 0        
        
        """
        #(label_width, label_height) = self.label.get_size()
        label_x = 0 #x #self.stage.get_width() - label_width - 50
        label_y = y #self.stage.get_height() - label_height
        self.set_position(0, y)
        
        #Add textures group and mark whether or not the textures are currently on the stage
        self.itemTexturesGroup.show_all()
        self.onStage = False
        """
        
    def scaleLabel(self, level, timeline):
       
        #Determine the zooming level
        zoomTo=0
        opacityTo = 255

        
        if level==0:
            zoomTo = self.menu.zoomStep0 #self.zoomLevel * 1.5
            opacityTo = self.menu.opacityStep0
            self.itemTexturesGroup.hide()
            self.glossMgr.stage.add(self.itemTexturesGroup)
            self.onStage = True
            #self.itemTexturesGroup.show_all()
        if level==1:
            zoomTo = self.menu.zoomStep1
            opacityTo = self.menu.opacityStep1
            if self.onStage: 
                #self.menu.remove(self.itemTexturesGroup)
                self.onStage = False
            #self.itemTexturesGroup.hide_all()
        if level==2:
            zoomTo = self.menu.zoomStep2
            opacityTo = self.menu.opacityStep2
            if self.onStage:
                #self.menu.remove(self.itemTexturesGroup)
                self.onStage = False
            #self.itemTexturesGroup.hide_all()
            
        if (zoomTo == self.currentZoom) and (opacityTo == self.currentOpacity):
            return None
    
        alpha = clutter.Alpha(timeline, clutter.ramp_inc_func)
        #self.behaviour1 = clutter.BehaviourScale(scale_start=self.currentZoom, scale_end=zoomTo, alpha=alpha) #scale_gravity=clutter.GRAVITY_WEST, 
        self.behaviour1 = clutter.BehaviourScale(x_scale_start=self.currentZoom, y_scale_start=self.currentZoom, x_scale_end=zoomTo, y_scale_end=zoomTo, alpha=alpha) #scale_gravity=clutter.GRAVITY_WEST, 
        self.set_anchor_point_from_gravity(clutter.GRAVITY_WEST)
        self.behaviour2 = clutter.BehaviourOpacity(opacity_start=self.currentOpacity, opacity_end=opacityTo, alpha=alpha)
        self.behaviour1.apply(self)
        self.behaviour2.apply(self)
        
        #timeline.connect('completed', self.scale_end_event, zoomTo, opacityTo)
        self.currentZoom = zoomTo
        self.currentOpacity = opacityTo

    def scale_end_event(self, data, zoomTo, opacityTo):
        pass
        
    def get_zoom_level(self):
        return self.zoomLevel
        
    def set_data(self, data):
        self.data = data
        
    def get_data(self):
        return self.data
    
    def setAction(self, newAction):
        self.action = newAction
        
    def getAction(self):
        return self.action
    
    def get_menu(self):
        return self.menu
