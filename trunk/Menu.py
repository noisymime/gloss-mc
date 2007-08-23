import clutter
import pygtk
import gtk
import time
from ReflectionTexture import Texture_Reflection

class Menu:
    item_gap = 10 #Distance between items
    
    def __init__ (self, menuMgr):
        self.menuMgr = menuMgr
        self.stage = self.menuMgr.get_stage()
        self.menuItems = []
        self.selected = 0
        self.displayMin = 0 #The number of menu items that will be shown at a time
        self.displayMax = 6
        self.moveQueue = 0
        self.displaySize = self.displayMax - self.displayMin
        self.displayPosition = (0, 0)
        self.itemGroup = clutter.Group()
        self.menuGroup = clutter.Group()
        self.stage.add(self.itemGroup)
        self.stage.add(self.menuGroup)
        #self.hasTimeline = False
        self.timeline = clutter.Timeline(15, 75) #This timeline is used on any movements that occur when changing items
        self.timeline_completed=True
        self.menuMgr.addMenu(self)
        #self.itemGroup.hide_all()
    
    def addItem(self, itemLabel, imagePath):
        if len(self.menuItems) == 0:
            label_height = 0
            label_width = 0
        else:
            (label_width, label_height) = self.menuItems[0].get_size()
            
        label_y = label_height * len(self.menuItems)+self.item_gap
        
        newItem = ListItem(self, itemLabel, label_y, imagePath)
        self.menuItems.append(newItem)
        self.itemGroup.add(newItem)
        
        group_x = self.itemGroup.get_x()
        group_y = self.itemGroup.get_y() - (label_height)
        self.itemGroup.set_position(group_x, group_y) 
        
        return newItem
        
    def display(self):
        if self.displayMax > len(self.menuItems):
            self.displayMax = len(self.menuItems)
            self.displaySize = self.displayMax - self.displayMin
        print self.displayMax
        
        for i in range(self.displaySize):
            self.menuItems[i].show()
            
        self.itemGroup.show()
        
    def getItem(self, index):
        return self.menuItems[index]
    def getStage(self):
        return self.stage
    def getMenuMgr(self):
        return self.menuMgr
        
    def setMenuPositionByName(self, location):
        if location == "center":
            menu_y = (self.stage.get_height()-self.itemGroup.get_height())/2
            menu_x = (self.stage.get_width()-self.itemGroup.get_width())/2
            self.itemGroup.set_position(menu_x, menu_y)
            self.displayPosition = (menu_x, menu_y)
            print "Original Group size: " + str(self.itemGroup.get_width())
            print "Starting at : " + str(menu_x) + ":" + str(menu_y)
    
    #The display position is the x, y coords of where the menu is when it is active
    def get_display_position(self):
        return self.displayPosition
        
    def setMenuPosition(self, x, y):
        self.itemGroup.set_position(x,y)
        
    def getItemGroup(self):
        return self.itemGroup
        
    def getMenuGroup(self):
        return self.menuGroup
        
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
        
        #Initially check whether the last animation is still going           
        if self.timeline.is_playing():
            self.moveQueue = self.moveQueue + 1
            #self.timeline.set_speed(1000) # Nasty hack to make sure the timeline finishes
            return None
    
        self.timeline = clutter.Timeline (15,85)
        self.timeline.connect('completed', self.completeMove)
        
        #Check if we're at the last item in the list
        if (self.selected) != (len(self.menuItems)-1):
            if not self.moveQueue == 0:
                self.selected = self.selected + self.moveQueue
                if self.selected > (len(self.menuItems)-1):
                    self.selected = (len(self.menuItems)-1)
            else:
                self.selected = self.selected+1
            
            #This horrible loop does all the scaling
            #This includes, the selected item and the ones on either side of it
            for i in range(len(self.menuItems)):
                if i == self.selected:
                    self.menuItems[i].scaleLabel(0, self.timeline)
                elif (i == self.selected-1) and (i >= self.displayMin+1):
                    self.menuItems[i].scaleLabel(1, self.timeline)
                elif (i == self.selected+1) and (i <= self.displayMax-1):
                    self.menuItems[i].scaleLabel(1, self.timeline)
                else:
                    self.menuItems[i].scaleLabel(2, self.timeline)
                
            #Check we're at the bottom of the viewable list
            if self.selected >= self.displayMax:
                #If yes, move the menu, leave the selection bar where is
                self.menuItems[self.selected].set_opacity(0)
                self.menuItems[self.selected].show()
                self.rollMenu( self.menuItems[self.selected], self.menuItems[self.selected-self.displaySize], self.timeline)
            else:
                #move the selection bar
                self.menuMgr.get_selector_bar().selectItem(self.menuItems[self.selected], self.timeline)
        
        self.timeline.start()
        self.moveQueue = 0
        
    #Returns the newly selected item
    def selectPrevious(self):
        
        #Initially check whether the last animation is still going
        if self.timeline.is_playing():
            self.moveQueue = self.moveQueue - 1
            #self.timeline.set_speed(1000) # Nasty hack to make sure the timeline finishes
            return None
            
        self.timeline = clutter.Timeline (15,85)
        self.timeline.connect('completed', self.completeMove)
        
        #Check if we're at the first item in the list
        if (self.selected) != 0:
            if not self.moveQueue == 0:
                self.selected = self.selected + self.moveQueue
                if self.selected < 0:
                    self.selected = 0
            else:
                self.selected = self.selected-1
            
            #This horrible loop does all the scaling
            #This includes, the selected item and the ones on either side of it
            for i in range(len(self.menuItems)):
                if i == self.selected:
                    self.menuItems[i].scaleLabel(0, self.timeline)
                elif (i == self.selected-1) and (i >= self.displayMin+1):
                    self.menuItems[i].scaleLabel(1, self.timeline)
                elif (i == self.selected+1) and (i <= self.displayMax-1):
                    self.menuItems[i].scaleLabel(1, self.timeline)
                else:
                    self.menuItems[i].scaleLabel(2, self.timeline)
            
            #Check we're at the top of the viewable list
            if self.selected < self.displayMin:
                #If yes, move the menu, leave the selection bar where is
                #self.menuItems[self.selected].set_opacity(0)
                #self.menuItems[self.selected].show()
                self.rollMenu( self.menuItems[self.selected], self.menuItems[self.selected+self.displaySize], self.timeline)
            else:
                #move the selection bar
                self.menuMgr.get_selector_bar().selectItem(self.menuItems[self.selected], self.timeline)

        self.timeline.start()
        self.moveQueue = 0
        
    def completeMove(self, data):
        if self.moveQueue > 0:
            self.selectNext()
        elif self.moveQueue < 0:
            self.selectPrevious()
            
    def selectFirst(self, moveBar):
        self.timeline = clutter.Timeline(1, 75)
        self.selected = 0
        for i in range(0,len(self.menuItems)):
            if i == 0:
                self.menuItems[i].scaleLabel(0, self.timeline)
            elif i == 1:
                self.menuItems[i].scaleLabel(1, self.timeline)
            else:
                self.menuItems[i].scaleLabel(2, self.timeline)
        
        if moveBar:    
            self.menuMgr.get_selector_bar().selectItem(self.menuItems[self.selected], self.timeline)
        
        self.timeline.start()
        
    #When the menu needs to display a new item from the top or bottom, it rolls
    def rollMenu(self, incomingMenuItem, outgoingMenuItem, timeline):    
        (group_x, group_y) = self.itemGroup.get_abs_position()
        (bar_x, bar_y) = incomingMenuItem.get_menu().getMenuMgr().get_selector_bar().get_abs_position()
        (incoming_x, incoming_y) = incomingMenuItem.get_abs_position()
        if incoming_y > bar_y:  
            #Then the incoming item is below the selector bar
            gap = (incoming_y - bar_y) * -1
            self.displayMin = self.displayMin+1
            self.displayMax = self.displayMax+1
        else:
            #Then the incoming item is above the selector bar
            gap = bar_y - incoming_y + (self.item_gap/2)
            self.displayMin = self.displayMin-1
            self.displayMax = self.displayMax-1
        
        knots = (\
            (group_x, group_y),\
            (group_x, group_y+gap)\
            )
                
        alpha = clutter.Alpha(timeline, clutter.ramp_inc_func)
        behaviour = clutter.BehaviourPath(alpha, knots)
        behaviour2 = clutter.BehaviourOpacity(alpha, outgoingMenuItem.get_opacity(), 0)
        
        behaviour.apply(self.itemGroup)
        behaviour2.apply(outgoingMenuItem)
        
    def get_item_gap(self):
        return self.item_gap
        
    def get_current_item(self):
        return self.menuItems[self.selected]
            
    
class ListItem (clutter.Label):
    zoomLevel = 0.5
    opacityStep = 120

    def __init__ (self, menu, itemLabel, y, imagePath):
        clutter.Label.__init__ (self)
        self.itemTexturesGroup = clutter.Group()
        font = menu.getMenuMgr().get_skinMgr().get_menu_font()
        self.stage = menu.getMenuMgr().get_stage()
        self.set_font_name(font)
        self.set_text(itemLabel)
        self.color = clutter.Color(0xff, 0xff, 0xff, 0xdd)
        self.set_color(self.color)
        self.currentOpacity = 255
        self.menu = menu
        self.data = itemLabel #By default the items data is simply its label
        
        #Text is actually scaled down in 'regular' position so that it doesn't get jaggies when zoomed in
        self.set_scale(self.zoomLevel, self.zoomLevel)
        self.currentZoom = self.zoomLevel
        
        
        #(label_width, label_height) = self.label.get_size()
        label_x = 0 #x #self.stage.get_width() - label_width - 50
        label_y = y #self.stage.get_height() - label_height
        self.set_position(0, y)
        self.addImage(imagePath, True)
        
        #Add textures group and hide it
        self.menu.getMenuGroup().add(self.itemTexturesGroup)
        self.itemTexturesGroup.hide_all()
        
    def scaleLabel(self, level, timeline):
        self.timeline = timeline
        self.timeline.set_loop(False)
        
        #Determine the zooming level
        zoomTo=0
        opacityTo = 255
        if level==0:
            zoomTo = 1 #self.zoomLevel * 1.5
            opacityTo = 255
            self.itemTexturesGroup.show_all()
        if level==1:
            zoomTo = self.zoomLevel * 1.2
            opacityTo = 255 - self.opacityStep
            self.itemTexturesGroup.hide_all()
        if level==2:
            zoomTo = self.zoomLevel
            opacityTo = 255 - 2*self.opacityStep
            self.itemTexturesGroup.hide_all()
            
        if zoomTo == self.currentZoom:
            return None
        
        alpha = clutter.Alpha(self.timeline, clutter.ramp_inc_func)
        self.behaviour1 = clutter.BehaviourScale(alpha, self.currentZoom, zoomTo, clutter.GRAVITY_WEST)
        self.behaviour2 = clutter.BehaviourOpacity(alpha, self.currentOpacity, opacityTo)
        self.behaviour1.apply(self)
        self.behaviour2.apply(self)

        
        self.currentZoom = zoomTo
        self.currentOpacity = opacityTo
        return self.timeline
        
    def get_zoom_level(self):
        return self.zoomLevel

        
    def addImage(self, path, useReflection):
        self.tempTexture = clutter.Texture()
        pixbuf = gtk.gdk.pixbuf_new_from_file(path)

        self.tempTexture.set_pixbuf(pixbuf)
        (abs_x, abs_y) = self.get_abs_position()

        x = abs_x# - self.tempTexture.get_width()
        y = (self.menu.getStage().get_height()/2) - (self.tempTexture.get_height()/2)
        self.tempTexture.set_position(x, y)
        
        self.tempTexture.rotate_y(45,0,0)    
        self.itemTexturesGroup.add(self.tempTexture)
        self.tempTexture.hide_all()
        
        #Scale the image down by half
        xy_ratio = self.tempTexture.get_width() / self.tempTexture.get_height()
        self.tempTexture.set_width(int(self.stage.get_width() * 0.30)) #30% of the stages width
        self.tempTexture.set_height(self.tempTexture.get_width() * xy_ratio ) #Just makes sure the sizes stay the same
        
        if useReflection:
            self.reflectionTexture = Texture_Reflection(self.tempTexture)
            #self.reflectionTexture.set_position(0, 0)#self.tempTexture.get_height())
            self.itemTexturesGroup.add(self.reflectionTexture)
        self.itemTexturesGroup.hide_all()
        
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
