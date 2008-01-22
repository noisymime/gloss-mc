import clutter
import pygtk
import gtk
import pango
import time
import math
from ReflectionTexture import Texture_Reflection
from InputQueue import InputQueue

class Menu(clutter.Group):
    font = ""
    menu_item_transition = None
    zoomLevel = 0.5
    opacityStep = 120
    
    def __init__ (self, glossMgr):
        clutter.Group.__init__(self)
        self.glossMgr = glossMgr
        self.stage = self.glossMgr.get_stage()
        self.itemGroup = clutter.Group()
        self.glossMgr.themeMgr.setup_menu("main", self)
        
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
    
    def addItem(self, itemLabel):
        if len(self.menuItems) == 0:
            tempLabel = clutter.Label()
            tempLabel.set_font_name(self.font)
            tempLabel.set_text("S")
            #tempLabel.set_scale_with_gravity(self.zoomStep0, self.zoomStep0, clutter.GRAVITY_WEST)
            self.label_height = tempLabel.get_height()
            #self.label_height = self.label_height * self.zoomStep1
            label_width = 0
        #else:
        #    (label_width, label_height) = self.menuItems[0].get_size()
        
        label_y = len(self.menuItems) * (self.label_height + self.item_gap)
        #print "Label height: " + str(self.label_height)
        
        newItem = ListItem(self, itemLabel, label_y)
        self.menuItems.append(newItem)
        self.itemGroup.add(newItem)
        
        #group_x = self.itemGroup.get_x()
        #group_y = self.itemGroup.get_y() - (self.label_height)
        #self.itemGroup.set_position(group_x, group_y) 
        
        return newItem
        
    def display(self):
        if self.displayMax > len(self.menuItems):
            self.displayMax = len(self.menuItems)
            self.displaySize = self.displayMax - self.displayMin
        
        for i in range(self.displaySize):
            self.menuItems[i].show()
            
        self.itemGroup.show()
        
    def getItem(self, index):
        return self.menuItems[index]
    def getStage(self):
        return self.stage
    def getGlossMgr(self):
        return self.glossMgr
        
    def setMenuPositionByName(self, location):
        return None
        if location == "center":
            menu_y = (self.stage.get_height()-self.itemGroup.get_height())/2
            menu_x = (self.stage.get_width()-self.itemGroup.get_width())/2
            self.itemGroup.set_position(menu_x, menu_y)
            #print "Original Group size: " + str(self.itemGroup.get_width())
            #print "Starting at : " + str(menu_x) + ":" + str(menu_y)
    
    #The display position is the x, y coords of where the menu is when it is active
    def get_display_position(self):
        return (self.itemGroup.get_x(), self.itemGroup.get_y())
        
    def setMenuPosition(self, x, y):
        self.itemGroup.set_position(x,y)
        
    def getItemGroup(self):
        return self.itemGroup
        
    def setListFont(self, newFont):
        currentY= 0 #self.itemGroup.get_y()
        self.font = newFont
        for li in self.menuItems:
            x = li.get_x()
            #y = li.getPositionY()
            li.set_font_name(newFont)
            li.set_position(x,currentY)
            currentY = currentY + li.get_height()
    
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
            
        #Empty out things on the menu first (if any)
        for group in self.get_children():
            self.remove(group)
            
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
        (group_x, group_y) = self.itemGroup.get_abs_position()
        (bar_x, bar_y) = self.glossMgr.get_selector_bar().get_abs_position() # incomingMenuItem.get_menu().getMenuMgr().
        (incoming_x, incoming_y) = self.glossMgr.get_selector_bar().get_true_abs_position(incomingMenuItem) #incomingMenuItem.get_abs_position()
        
        #print self.itemGroup.get_abs_position()
        #print "Starting group position: " + self.itemGroup.get_abs_position()
        
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
        
        self.behaviour1.apply(self.itemGroup)
        self.behaviour2.apply(outgoingMenuItem)
        
    def get_item_gap(self):
        return self.item_gap
        
    def get_current_item(self):
        return self.menuItems[self.selected]
            
    
class ListItem (clutter.Label):
    zoomLevel = 0.5
    opacityStep = 120

    def __init__ (self, menu, itemLabel, y):
        clutter.Label.__init__ (self)
        glossMgr = menu.getGlossMgr()
        self.menu = menu
        self.stage = glossMgr.get_stage()
        
        #ItemTexturesGroup is what shows any images / reflections associated with the item
        self.itemTexturesGroup = clutter.Group()
        self.itemTexturesGroup.set_position(menu.menu_image_x, menu.menu_image_y)
        
        
        #setup the label
        font = menu.font
        self.set_font_name(font)
        self.set_text(itemLabel)
        self.color = clutter.Color(0xff, 0xff, 0xff, 0xdd)
        self.set_color(self.color)
        self.currentOpacity = 255
        self.data = itemLabel #By default the items data is simply its label
        #The width is the length of the selector bar minus its offset
        width = glossMgr.get_selector_bar().get_width() + glossMgr.get_selector_bar().get_x_offset()
        self.set_width(width)

        self.set_ellipsize(pango.ELLIPSIZE_END)
        #Text is actually scaled down in 'regular' position so that it doesn't get jaggies when zoomed in
        self.set_scale(self.zoomLevel, self.zoomLevel)
        self.currentZoom = 0        
        
        #(label_width, label_height) = self.label.get_size()
        label_x = 0 #x #self.stage.get_width() - label_width - 50
        label_y = y #self.stage.get_height() - label_height
        self.set_position(0, y)
        
        #Add textures group and mark whether or not the textures are currently on the stage
        self.itemTexturesGroup.show_all()
        self.onStage = False
        
    def scaleLabel(self, level, timeline):
       
        #Determine the zooming level
        zoomTo=0
        opacityTo = 255
        
        if level==0:
            zoomTo = self.menu.zoomStep0 #self.zoomLevel * 1.5
            opacityTo = self.menu.opacityStep0
            self.itemTexturesGroup.hide()
            self.menu.add(self.itemTexturesGroup)
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
        #self.set_anchor_point_from_gravity(clutter.GRAVITY_WEST)
        self.behaviour1.set_property("scale-gravity", clutter.GRAVITY_WEST) #As at Clutter r1807 you cannot set the gravity on the line above. 
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

        
    def add_image_from_path(self, path, x, y):
        self.tempTexture = clutter.Texture()
        pixbuf = gtk.gdk.pixbuf_new_from_file(path)
        tempTexture.set_pixbuf(pixbuf)
        
        self.add_image_from_texture(tempTexture, x, y)
        
    def add_image_from_texture(self, texture):
        if texture is None:
            print "NO TEXTURE!"

        """
        Removing as this is currently already handled in individual module files
        #Set the image to the size in the theme
        if not self.menu.menu_image_height is None:
            texture.set_height(self.menu.menu_image_height)
        if not self.menu.menu_image_width is None:            
            texture.set_width(self.menu.menu_image_width)
        """
        
        #Rotate appropriately
        rotation = self.menu.menu_image_rotation
        x_rotation = (texture.get_width())
        texture.set_rotation(clutter.Y_AXIS, rotation, x_rotation, 0, 0)
        self.itemTexturesGroup.add(texture)        
        
        #If reflection is turned on in the theme, add a reflection texture
        if self.menu.useReflection:
            self.reflectionTexture = Texture_Reflection(texture)
            self.itemTexturesGroup.add(self.reflectionTexture)
        
        self.itemTexturesGroup.show_all()
        
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
